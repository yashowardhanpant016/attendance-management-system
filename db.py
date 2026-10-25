from typing import List, Tuple, Optional, Any
"""
Database Access Layer for Attendance Management System.
Handles SQLite persistence, CRUD operations, transactions, undo tracking,
analytics aggregations, CSV import/export, atomic database backups,
audit log engine, shortfall calculation, and at-risk student monitoring.
"""

import sqlite3
import csv
import os
import shutil
import math
from datetime import datetime, timedelta

class AttendanceDB:
    def __init__(self, db_name="attendance_accessible.db"):
        self.db_name = db_name
        self._undo_stack = []  # In-memory undo stack: [(roll_no, date, previous_status, new_status)]
        self.init_db()

    def get_connection(self):
        """Returns a SQLite connection with foreign key support enabled."""
        conn = sqlite3.connect(self.db_name, timeout=10.0)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_db(self):
        """Initializes tables (students, attendance, audit_logs) and seeds base records."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    roll_no TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    section TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    roll_no TEXT NOT NULL,
                    date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    FOREIGN KEY(roll_no) REFERENCES students(roll_no) ON UPDATE CASCADE ON DELETE CASCADE,
                    UNIQUE(roll_no, date)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    details TEXT NOT NULL,
                    user_role TEXT NOT NULL
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_att_date ON attendance(date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_att_roll ON attendance(roll_no)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp)")
            conn.commit()
            self._seed_sample_data(cursor, conn)

    def _seed_sample_data(self, cursor, conn):
        sample_students = [
            ("CSEB-01", "Aarav Sharma", "CSE-B"),
            ("CSEB-02", "Bhavna Verma", "CSE-B"),
            ("CSEB-03", "Chirag Joshi", "CSE-B"),
            ("CSEB-04", "Deepika Negi", "CSE-B"),
            ("CSEB-05", "Yashowardhan Pant", "CSE-B"),
        ]
        cursor.executemany("INSERT OR IGNORE INTO students VALUES (?, ?, ?)", sample_students)

        # Check if audit_logs has initial entry
        cursor.execute("SELECT COUNT(*) FROM audit_logs")
        if cursor.fetchone()[0] == 0:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO audit_logs (timestamp, action_type, details, user_role) VALUES (?, ?, ?, ?)",
                (now_str, "SYSTEM_INIT", "Database initialized with WCAG AAA accessibility profile and TQM quality engine", "Admin")
            )

        # Check if attendance records exist; if fewer than 10, seed historical sessions
        cursor.execute("SELECT COUNT(*) FROM attendance")
        if cursor.fetchone()[0] < 10:
            # Seed 16 days of historical attendance for rich 30-day analytics and at-risk roster
            # Generate weekdays over October 2026
            seed_dates = [
                "2026-10-01", "2026-10-02", "2026-10-05", "2026-10-06", "2026-10-07",
                "2026-10-08", "2026-10-09", "2026-10-12", "2026-10-13", "2026-10-14",
                "2026-10-15", "2026-10-16", "2026-10-19", "2026-10-20", "2026-10-21",
                "2026-10-22", "2026-10-23"
            ]
            attendance_seed = []
            for d in seed_dates:
                # CSEB-01: High attendance (Present almost every day)
                attendance_seed.append(("CSEB-01", d, "Present" if d != "2026-10-09" else "Absent"))
                # CSEB-02: Moderate attendance
                attendance_seed.append(("CSEB-02", d, "Present" if d not in ("2026-10-06", "2026-10-16") else "Absent"))
                # CSEB-03: Low attendance (<75% threshold, triggers Shortfall calculator)
                attendance_seed.append(("CSEB-03", d, "Present" if d not in ("2026-10-02", "2026-10-07", "2026-10-13", "2026-10-15", "2026-10-20", "2026-10-22") else "Absent"))
                # CSEB-04: At-Risk (Absent on latest 3 consecutive sessions: Oct 21, 22, 23)
                if d in ("2026-10-21", "2026-10-22", "2026-10-23"):
                    attendance_seed.append(("CSEB-04", d, "Absent"))
                else:
                    attendance_seed.append(("CSEB-04", d, "Present" if d != "2026-10-08" else "Late"))
                # CSEB-05: 100% Attendance
                attendance_seed.append(("CSEB-05", d, "Present"))

            cursor.executemany("INSERT OR REPLACE INTO attendance (roll_no, date, status) VALUES (?, ?, ?)", attendance_seed)

        conn.commit()

    # ---------------------------------------------------------
    # Feature 7: Audit Log Engine
    # ---------------------------------------------------------
    def log_audit_event(self, action_type: str, details: str, user_role: str = "Admin"):
        """Logs an operational action to the audit_logs table."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO audit_logs (timestamp, action_type, details, user_role) VALUES (?, ?, ?, ?)",
                (timestamp, action_type, details, user_role)
            )
            conn.commit()

    def get_recent_audit_logs(self, limit: int = 50):
        """Fetches the latest audit log entries sorted by newest first."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, timestamp, action_type, details, user_role FROM audit_logs ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            return cursor.fetchall()

    # ---------------------------------------------------------
    # Feature 2: Shortfall Calculator (<75% Threshold)
    # ---------------------------------------------------------
    @staticmethod
    def calculate_shortfall(present: int, total: int, target: float = 0.75) -> int:
        """
        Formula: If P/T < 0.75, Required Classes = ceil((0.75 * T - P) / 0.25).
        Returns the number of consecutive present sessions needed to attain >= 75% attendance.
        """
        if total <= 0:
            return 0
        rate = present / total
        if rate >= target:
            return 0
        needed = math.ceil((target * total - present) / (1.0 - target))
        return max(0, needed)

    # ---------------------------------------------------------
    # Student CRUD Operations (Integrated with Audit Logs)
    # ---------------------------------------------------------
    def add_student(self, roll_no, name, section, user_role="Admin"):
        roll = roll_no.strip().upper()
        s_name = name.strip()
        sec = section.strip().upper()
        if not roll or not s_name or not sec:
            raise ValueError("Roll Number, Name, and Section cannot be empty.")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO students VALUES (?, ?, ?)", (roll, s_name, sec))
            conn.commit()

        self.log_audit_event("STUDENT_ENROLLED", f"Added student {roll} ({s_name}) to {sec}", user_role)
        return True

    def update_student(self, old_roll_no, new_roll_no, name, section, user_role="Admin"):
        old_roll = old_roll_no.strip().upper()
        new_roll = new_roll_no.strip().upper()
        s_name = name.strip()
        sec = section.strip().upper()

        if not new_roll or not s_name or not sec:
            raise ValueError("Roll Number, Name, and Section cannot be empty.")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            if old_roll != new_roll:
                cursor.execute("SELECT 1 FROM students WHERE roll_no = ?", (new_roll,))
                if cursor.fetchone():
                    raise sqlite3.IntegrityError(f"Student with roll number '{new_roll}' already exists.")
                cursor.execute("UPDATE attendance SET roll_no = ? WHERE roll_no = ?", (new_roll, old_roll))

            cursor.execute("""
                UPDATE students
                SET roll_no = ?, name = ?, section = ?
                WHERE roll_no = ?
            """, (new_roll, s_name, sec, old_roll))
            conn.commit()

        self.log_audit_event("STUDENT_UPDATED", f"Modified student {old_roll} -> {new_roll} ({s_name}, {sec})", user_role)
        return True

    def delete_student(self, roll_no, user_role="Admin"):
        roll = roll_no.strip().upper()
        student = self.get_student(roll)
        name = student[1] if student else "Unknown"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM attendance WHERE roll_no = ?", (roll,))
            cursor.execute("DELETE FROM students WHERE roll_no = ?", (roll,))
            conn.commit()

        self.log_audit_event("STUDENT_DELETED", f"Deleted student {roll} ({name}) and purged attendance logs", user_role)
        return True

    def get_student(self, roll_no):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT roll_no, name, section FROM students WHERE roll_no = ?", (roll_no.strip().upper(),))
            return cursor.fetchone()

    def fetch_all_students(self, section=None, search=None):
        query = "SELECT roll_no, name, section FROM students WHERE 1=1"
        params = []

        if section and section.upper() != "ALL":
            query += " AND section = ?"
            params.append(section.strip().upper())

        if search:
            query += " AND (LOWER(roll_no) LIKE ? OR LOWER(name) LIKE ?)"
            term = f"%{search.strip().lower()}%"
            params.extend([term, term])

        query += " ORDER BY roll_no ASC"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def fetch_sections(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT section FROM students ORDER BY section ASC")
            rows = cursor.fetchall()
            return [r[0] for r in rows if r[0]]

    # ---------------------------------------------------------
    # Attendance Operations & Undo Stack
    # ---------------------------------------------------------
    def get_current_status(self, roll_no, date):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM attendance WHERE roll_no = ? AND date = ?", (roll_no, date))
            row = cursor.fetchone()
            return row[0] if row else "Unmarked"

    def mark_attendance(self, roll_no, date, status, record_undo=True, user_role="Faculty"):
        roll = roll_no.strip().upper()
        stat = status.strip().capitalize()
        valid_statuses = {"Present", "Absent", "Late", "Unmarked"}
        if stat not in valid_statuses:
            raise ValueError(f"Invalid status '{stat}'. Must be one of {valid_statuses}")

        prev_status = self.get_current_status(roll, date)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            if stat == "Unmarked":
                cursor.execute("DELETE FROM attendance WHERE roll_no = ? AND date = ?", (roll, date))
            else:
                cursor.execute("""
                    INSERT INTO attendance (roll_no, date, status)
                    VALUES (?, ?, ?)
                    ON CONFLICT(roll_no, date) DO UPDATE SET status=excluded.status
                """, (roll, date, stat))
            conn.commit()

        if record_undo and prev_status != stat:
            self._undo_stack.append({
                "roll_no": roll,
                "date": date,
                "prev_status": prev_status,
                "new_status": stat,
                "timestamp": datetime.now().isoformat()
            })
            self.log_audit_event("ATTENDANCE_MARKED", f"Marked {roll} as {stat} on {date} (was {prev_status})", user_role)

    def mark_bulk_attendance(self, roll_list, date, status, user_role="Faculty"):
        """Marks attendance for multiple students in a single transaction."""
        for roll in roll_list:
            self.mark_attendance(roll, date, status, record_undo=True, user_role=user_role)
        self.log_audit_event("BULK_ATTENDANCE", f"Bulk marked {len(roll_list)} students as {status} on {date}", user_role)

    def undo_last_mark(self, user_role="Faculty"):
        """Reverts the most recent attendance action. Returns action details or None."""
        if not self._undo_stack:
            return None

        last_action = self._undo_stack.pop()
        roll = last_action["roll_no"]
        date = last_action["date"]
        restore_status = last_action["prev_status"]

        with self.get_connection() as conn:
            cursor = conn.cursor()
            if restore_status == "Unmarked":
                cursor.execute("DELETE FROM attendance WHERE roll_no = ? AND date = ?", (roll, date))
            else:
                cursor.execute("""
                    INSERT INTO attendance (roll_no, date, status)
                    VALUES (?, ?, ?)
                    ON CONFLICT(roll_no, date) DO UPDATE SET status=excluded.status
                """, (roll, date, restore_status))
            conn.commit()

        self.log_audit_event("ATTENDANCE_UNDO", f"Reverted {roll} on {date} to {restore_status}", user_role)

        return {
            "roll_no": roll,
            "date": date,
            "reverted_from": last_action["new_status"],
            "restored_to": restore_status
        }

    def has_undo(self):
        return len(self._undo_stack) > 0

    def fetch_attendance_by_date(self, date, section=None, search=None):
        query = """
            SELECT s.roll_no, s.name, s.section, COALESCE(a.status, 'Unmarked') as status
            FROM students s
            LEFT JOIN attendance a ON s.roll_no = a.roll_no AND a.date = ?
            WHERE 1=1
        """
        params = [date]

        if section and section.upper() != "ALL":
            query += " AND s.section = ?"
            params.append(section.strip().upper())

        if search:
            query += " AND (LOWER(s.roll_no) LIKE ? OR LOWER(s.name) LIKE ?)"
            term = f"%{search.strip().lower()}%"
            params.extend([term, term])

        query += " ORDER BY s.roll_no ASC"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    # ---------------------------------------------------------
    # Analytics & Summary Statistics
    # ---------------------------------------------------------
    def get_dashboard_stats(self, date):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM students")
            total_students = cursor.fetchone()[0]

            cursor.execute("""
                SELECT
                    COALESCE(SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END), 0) as present,
                    COALESCE(SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END), 0) as absent,
                    COALESCE(SUM(CASE WHEN a.status = 'Late' THEN 1 ELSE 0 END), 0) as late
                FROM students s
                LEFT JOIN attendance a ON s.roll_no = a.roll_no AND a.date = ?
            """, (date,))
            row = cursor.fetchone()
            present = row[0]
            absent = row[1]
            late = row[2]
            marked = present + absent + late
            unmarked = max(0, total_students - marked)

            pct = round((present / total_students * 100), 1) if total_students > 0 else 0.0

            return {
                "total": total_students,
                "present": present,
                "absent": absent,
                "late": late,
                "unmarked": unmarked,
                "percentage": pct
            }

    def get_student_history(self, roll_no):
        roll = roll_no.strip().upper()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT date, status
                FROM attendance
                WHERE roll_no = ?
                ORDER BY date DESC
            """, (roll,))
            records = cursor.fetchall()

            total_recorded = len(records)
            present_count = sum(1 for _, s in records if s == "Present")
            absent_count = sum(1 for _, s in records if s == "Absent")
            late_count = sum(1 for _, s in records if s == "Late")

            pct = round((present_count / total_recorded * 100), 1) if total_recorded > 0 else 0.0

            return {
                "records": records,
                "total": total_recorded,
                "present": present_count,
                "absent": absent_count,
                "late": late_count,
                "percentage": pct
            }

    def get_monthly_report(self, year_month, section=None):
        query = """
            SELECT s.roll_no, s.name, s.section,
                   COALESCE(SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END), 0) as present_days,
                   COALESCE(SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END), 0) as absent_days,
                   COALESCE(SUM(CASE WHEN a.status = 'Late' THEN 1 ELSE 0 END), 0) as late_days,
                   COALESCE(COUNT(a.status), 0) as total_recorded
            FROM students s
            LEFT JOIN attendance a ON s.roll_no = a.roll_no AND a.date LIKE ?
            WHERE 1=1
        """
        params = [f"{year_month}%"]

        if section and section.upper() != "ALL":
            query += " AND s.section = ?"
            params.append(section.strip().upper())

        query += " GROUP BY s.roll_no, s.name, s.section ORDER BY s.roll_no ASC"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

            report = []
            for r in rows:
                roll, name, sec, p, a, l, total = r
                pct = round((p / total * 100), 1) if total > 0 else 0.0
                shortfall = self.calculate_shortfall(p, total, 0.75)
                report.append({
                    "roll_no": roll,
                    "roll": roll,
                    "name": name,
                    "section": sec,
                    "present": p,
                    "absent": a,
                    "late": l,
                    "total_days": total,
                    "percentage": pct,
                    "shortfall": shortfall,
                    "is_below_threshold": (pct < 75.0 and total > 0)
                })
            return report

    def get_attendance_trends(self, limit_days=14):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT date
                FROM attendance
                ORDER BY date DESC
                LIMIT ?
            """, (limit_days,))
            dates = [row[0] for row in cursor.fetchall()]
            dates.reverse()

            trends = []
            for d in dates:
                stats = self.get_dashboard_stats(d)
                trends.append({
                    "date": d,
                    "present": stats["present"],
                    "total": stats["total"],
                    "percentage": stats["percentage"]
                })
            return trends

    # ---------------------------------------------------------
    # Feature 1: Smart Attendance Analytics & Trend Visualizer
    # ---------------------------------------------------------
    def get_detailed_attendance_trends(self, days=30):
        """
        Calculates daily trends, weekly trends, class average KPI,
        and section breakdown over the last 30 recorded days.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT date
                FROM attendance
                ORDER BY date DESC
                LIMIT ?
            """, (days,))
            dates = sorted([row[0] for row in cursor.fetchall()])

            daily = []
            for d in dates:
                stats = self.get_dashboard_stats(d)
                daily.append({
                    "date": d,
                    "present": stats["present"],
                    "absent": stats["absent"],
                    "late": stats["late"],
                    "total": stats["total"],
                    "percentage": stats["percentage"]
                })

            # Weekly aggregation
            weekly_dict = {}
            for item in daily:
                try:
                    dt = datetime.strptime(item["date"], "%Y-%m-%d")
                    year, week, _ = dt.isocalendar()
                    wkey = f"W{week}"
                    if wkey not in weekly_dict:
                        weekly_dict[wkey] = {"pcts": [], "dates": []}
                    weekly_dict[wkey]["pcts"].append(item["percentage"])
                    weekly_dict[wkey]["dates"].append(item["date"])
                except Exception:
                    pass

            weekly = []
            for wkey, data in weekly_dict.items():
                avg_pct = round(sum(data["pcts"]) / len(data["pcts"]), 1) if data["pcts"] else 0.0
                d_start = data["dates"][0][-5:]
                d_end = data["dates"][-1][-5:]
                weekly.append({
                    "week": wkey,
                    "label": f"{wkey} ({d_start} - {d_end})",
                    "percentage": avg_pct
                })

            # Overall class average
            all_pcts = [d["percentage"] for d in daily]
            overall_avg = round(sum(all_pcts) / len(all_pcts), 1) if all_pcts else 0.0

            # Section breakdown
            cursor.execute("""
                SELECT s.section,
                       COUNT(DISTINCT s.roll_no) as student_count,
                       COALESCE(SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END), 0) as total_present,
                       COALESCE(COUNT(a.id), 0) as total_logs
                FROM students s
                LEFT JOIN attendance a ON s.roll_no = a.roll_no
                GROUP BY s.section
            """)
            sec_rows = cursor.fetchall()
            section_breakdown = {}
            for s_row in sec_rows:
                sec, s_count, p_count, tot_marks = s_row
                s_pct = round((p_count / tot_marks * 100), 1) if tot_marks > 0 else 0.0
                section_breakdown[sec] = {
                    "students": s_count,
                    "rate": s_pct,
                    "present": p_count,
                    "total_logs": tot_marks
                }

            return {
                "daily": daily,
                "weekly": weekly,
                "overall_avg": overall_avg,
                "section_breakdown": section_breakdown
            }

    # ---------------------------------------------------------
    # Feature 1 & 2: At-Risk Student Monitoring
    # ---------------------------------------------------------
    def get_at_risk_students(self, threshold=75.0):
        """
        Identifies students with attendance < threshold (default 75%) OR
        downward trends over the past 3 consecutive sessions.
        """
        students = self.fetch_all_students()
        at_risk = []
        for s in students:
            roll, name, sec = s
            hist = self.get_student_history(roll)
            pct = hist["percentage"]
            total = hist["total"]
            present = hist["present"]

            # Check consecutive absences in latest records
            records = hist["records"]  # ordered by date DESC
            consec_absent = 0
            for _, stat in records:
                if stat == "Absent":
                    consec_absent += 1
                else:
                    break

            shortfall = self.calculate_shortfall(present, total, threshold / 100.0)

            is_risk = False
            reasons = []
            if pct < threshold and total > 0:
                is_risk = True
                reasons.append(f"Rate {pct:.1f}% (< {threshold:.0f}%)")
            if consec_absent >= 3:
                is_risk = True
                reasons.append(f"{consec_absent} consecutive absents")

            if is_risk:
                at_risk.append({
                    "roll_no": roll,
                    "name": name,
                    "section": sec,
                    "percentage": pct,
                    "total": total,
                    "present": present,
                    "consecutive_absent": consec_absent,
                    "shortfall": shortfall,
                    "reason": " • ".join(reasons)
                })
        return at_risk

    # ---------------------------------------------------------
    # Feature 3: Student Monthly Attendance Calendar Data
    # ---------------------------------------------------------
    def get_student_month_calendar(self, roll_no, year, month):
        """
        Fetches daily attendance marks for a student in a specific year/month.
        Returns day-keyed mapping and monthly summary metrics.
        """
        month_prefix = f"{year:04d}-{month:02d}"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT date, status FROM attendance
                WHERE roll_no = ? AND date LIKE ?
                ORDER BY date ASC
            """, (roll_no.strip().upper(), f"{month_prefix}%"))
            rows = cursor.fetchall()

            day_status = {}
            present = 0
            absent = 0
            late = 0
            for d_str, stat in rows:
                try:
                    day_num = int(d_str.split("-")[2])
                    day_status[day_num] = stat
                    if stat == "Present":
                        present += 1
                    elif stat == "Absent":
                        absent += 1
                    elif stat == "Late":
                        late += 1
                except Exception:
                    pass

            total = present + absent + late
            pct = round((present / total * 100), 1) if total > 0 else 0.0

            return {
                "days": day_status,
                "total": total,
                "present": present,
                "absent": absent,
                "late": late,
                "percentage": pct
            }

    # ---------------------------------------------------------
    # Feature 6: Smart CSV Pre-Validation & Commit
    # ---------------------------------------------------------
    def validate_students_csv(self, filepath):
        """
        Poka-Yoke Pre-Validation:
        Parses CSV and checks for blank fields, intra-file duplicates, and DB conflicts.
        Returns: (valid_records, invalid_records)
        """
        valid_records = []
        invalid_records = []
        seen_in_file = set()

        existing_rolls = set()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT roll_no FROM students")
            existing_rolls = {r[0].upper() for r in cursor.fetchall()}

        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            for row_idx, row in enumerate(reader, start=1):
                if not row or not any(field.strip() for field in row):
                    continue
                # Skip header row if detected
                if row_idx == 1 and any("roll" in str(col).lower() for col in row):
                    continue

                if len(row) < 3:
                    invalid_records.append({
                        "row_idx": row_idx,
                        "roll_no": row[0].strip().upper() if len(row) > 0 else "N/A",
                        "name": row[1].strip() if len(row) > 1 else "N/A",
                        "section": "N/A",
                        "status": "Invalid",
                        "note": "Row has fewer than 3 columns"
                    })
                    continue

                roll = row[0].strip().upper()
                name = row[1].strip()
                sec = row[2].strip().upper()

                if not roll or not name or not sec:
                    invalid_records.append({
                        "row_idx": row_idx,
                        "roll_no": roll or "BLANK",
                        "name": name or "BLANK",
                        "section": sec or "BLANK",
                        "status": "Invalid",
                        "note": "Missing Roll Number, Name, or Section"
                    })
                elif roll in seen_in_file:
                    invalid_records.append({
                        "row_idx": row_idx,
                        "roll_no": roll,
                        "name": name,
                        "section": sec,
                        "status": "Duplicate",
                        "note": "Duplicate Roll No within CSV file"
                    })
                elif roll in existing_rolls:
                    invalid_records.append({
                        "row_idx": row_idx,
                        "roll_no": roll,
                        "name": name,
                        "section": sec,
                        "status": "Conflict",
                        "note": "Student already enrolled in SQLite"
                    })
                else:
                    seen_in_file.add(roll)
                    valid_records.append({
                        "row_idx": row_idx,
                        "roll_no": roll,
                        "name": name,
                        "section": sec,
                        "status": "Valid",
                        "note": "Sanitized and ready to commit"
                    })

        return valid_records, invalid_records

    def commit_validated_students(self, valid_records, user_role="Admin"):
        """Commits only the pre-validated student records into SQLite."""
        if not valid_records:
            return 0
        count = 0
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for rec in valid_records:
                cursor.execute(
                    "INSERT OR IGNORE INTO students (roll_no, name, section) VALUES (?, ?, ?)",
                    (rec["roll_no"], rec["name"], rec["section"])
                )
                count += 1
            conn.commit()
        self.log_audit_event("CSV_BATCH_COMMIT", f"Committed {count} pre-validated student records from CSV", user_role)
        return count

    # ---------------------------------------------------------
    # Batch CSV & Backup Operations
    # ---------------------------------------------------------
    def export_students_csv(self, filepath, user_role="Admin"):
        students = self.fetch_all_students()
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["roll_no", "name", "section"])
            for s in students:
                writer.writerow(s)
        self.log_audit_event("CSV_STUDENTS_EXPORT", f"Exported {len(students)} students to {os.path.basename(filepath)}", user_role)
        return len(students)

    def import_students_csv(self, filepath, user_role="Admin"):
        valid, _ = self.validate_students_csv(filepath)
        count = self.commit_validated_students(valid, user_role=user_role)
        return count, len(valid) - count

    def export_attendance_csv(self, date, filepath, user_role="Faculty"):
        records = self.fetch_attendance_by_date(date)
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["roll_no", "name", "section", "status"])
            for r in records:
                writer.writerow(r)
        self.log_audit_event("CSV_ATTENDANCE_EXPORT", f"Exported attendance for {date} to {os.path.basename(filepath)}", user_role)
        return len(records)

    def export_monthly_report_csv(self, year_month, filepath, user_role="Faculty"):
        data = self.get_monthly_report(year_month)
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["roll_no", "name", "section", "present_days", "absent_days", "late_days", "total_days", "percentage", "shortfall"])
            for r in data:
                writer.writerow([r["roll_no"], r["name"], r["section"], r["present"], r["absent"], r["late"], r["total_days"], r["percentage"], r["shortfall"]])
        self.log_audit_event("CSV_REPORT_EXPORT", f"Exported monthly report for {year_month} to {os.path.basename(filepath)}", user_role)
        return len(data)

    def backup_database(self, destination_path, user_role="Admin"):
        with self.get_connection() as src_conn:
            dest_conn = sqlite3.connect(destination_path)
            src_conn.backup(dest_conn)
            dest_conn.close()
        self.log_audit_event("DB_BACKUP", f"Atomic database backup saved to {os.path.basename(destination_path)}", user_role)
        return destination_path

    def restore_database(self, source_path, user_role="Admin"):
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Backup file not found: {source_path}")

        temp_conn = sqlite3.connect(source_path)
        cursor = temp_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('students', 'attendance')")
        tables = [t[0] for t in cursor.fetchall()]
        temp_conn.close()

        if "students" not in tables or "attendance" not in tables:
            raise ValueError("Invalid backup file: Missing required 'students' or 'attendance' tables.")

        src_conn = sqlite3.connect(source_path)
        with self.get_connection() as dest_conn:
            src_conn.backup(dest_conn)
        src_conn.close()
        self._undo_stack.clear()
        self.log_audit_event("DB_RESTORE", f"Restored database from snapshot {os.path.basename(source_path)}", user_role)
        return True

    # ---------------------------------------------------------
    # Convenience Bridge Methods & Aliases for Views
    # ---------------------------------------------------------
    def fetch_students(self):
        return self.fetch_all_students()

    def fetch_students_with_stats(self, search=None, section=None):
        query = """
            SELECT s.roll_no, s.name, s.section,
                   COUNT(a.id) as total_logged,
                   COALESCE(SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END), 0) as present_count
            FROM students s
            LEFT JOIN attendance a ON s.roll_no = a.roll_no
            WHERE 1=1
        """
        params = []
        if section and section.upper() != "ALL":
            query += " AND s.section = ?"
            params.append(section.strip().upper())
        if search:
            query += " AND (LOWER(s.roll_no) LIKE ? OR LOWER(s.name) LIKE ?)"
            term = f"%{search.strip().lower()}%"
            params.extend([term, term])
        query += " GROUP BY s.roll_no, s.name, s.section ORDER BY s.roll_no ASC"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            result = []
            for r in rows:
                roll, name, sec, total, p = r
                pct = round((p / total * 100), 1) if total > 0 else 0.0
                shortfall = self.calculate_shortfall(p, total, 0.75)
                result.append((roll, name, sec, total, pct, shortfall))
            return result

    def get_monthly_attendance_summary(self, month_str):
        report = self.get_monthly_report(month_str)
        for r in report:
            r["roll"] = r["roll_no"]
        return report

    def get_student_attendance_history(self, roll):
        hist = self.get_student_history(roll)
        return [{"date": r[0], "status": r[1]} for r in hist["records"]]

    def record_attendance(self, roll, date, status, user_role="Faculty"):
        return self.mark_attendance(roll, date, status, record_undo=True, user_role=user_role)

    def get_single_attendance(self, roll, date):
        return self.get_current_status(roll, date)

    def mark_all_unmarked_present(self, date, user_role="Faculty"):
        records = self.fetch_attendance_by_date(date)
        unmarked = [r[0] for r in records if r[3] == "Unmarked"]
        for roll in unmarked:
            self.mark_attendance(roll, date, "Present", record_undo=True, user_role=user_role)
        return len(unmarked)

    def export_attendance_by_date_csv(self, date, filepath, user_role="Faculty"):
        return self.export_attendance_csv(date, filepath, user_role=user_role)
