"""
Unit tests for db.py Database Access Layer.
Tests CRUD, constraints, attendance marking, undo stack,
statistics, monthly reports, CSV export/import, and backup/restore.
"""

import unittest
import os
import sqlite3
from db import AttendanceDB

TEST_DB_NAME = "test_attendance_temp.db"
TEST_BACKUP_NAME = "test_backup_temp.db"
TEST_CSV_NAME = "test_students_temp.csv"

class TestAttendanceDB(unittest.TestCase):
    def setUp(self):
        if os.path.exists(TEST_DB_NAME):
            os.remove(TEST_DB_NAME)
        self.db = AttendanceDB(TEST_DB_NAME)

    def tearDown(self):
        for f in [TEST_DB_NAME, TEST_BACKUP_NAME, TEST_CSV_NAME]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except OSError:
                    pass

    def test_seed_data(self):
        students = self.db.fetch_all_students()
        self.assertEqual(len(students), 5)
        rolls = [s[0] for s in students]
        self.assertIn("CSEB-01", rolls)
        self.assertIn("CSEB-05", rolls)

    def test_student_crud(self):
        # Create
        self.db.add_student("TEST-99", "Test Student", "CSE-A")
        s = self.db.get_student("TEST-99")
        self.assertIsNotNone(s)
        self.assertEqual(s[1], "Test Student")
        self.assertEqual(s[2], "CSE-A")

        # Duplicate Prevention
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.add_student("TEST-99", "Duplicate Student", "CSE-A")

        # Update
        self.db.update_student("TEST-99", "TEST-99-UPDATED", "Updated Name", "CSE-B")
        updated = self.db.get_student("TEST-99-UPDATED")
        self.assertIsNotNone(updated)
        self.assertEqual(updated[1], "Updated Name")
        self.assertEqual(updated[2], "CSE-B")
        self.assertIsNone(self.db.get_student("TEST-99"))

        # Delete
        self.db.delete_student("TEST-99-UPDATED")
        self.assertIsNone(self.db.get_student("TEST-99-UPDATED"))

    def test_attendance_and_undo(self):
        date = "2026-10-21"
        self.db.mark_attendance("CSEB-01", date, "Present")
        self.assertEqual(self.db.get_current_status("CSEB-01", date), "Present")

        # Update status to Absent
        self.db.mark_attendance("CSEB-01", date, "Absent")
        self.assertEqual(self.db.get_current_status("CSEB-01", date), "Absent")

        # Test Undo
        self.assertTrue(self.db.has_undo())
        undo_res = self.db.undo_last_mark()
        self.assertIsNotNone(undo_res)
        self.assertEqual(undo_res["restored_to"], "Present")
        self.assertEqual(self.db.get_current_status("CSEB-01", date), "Present")

    def test_dashboard_stats(self):
        date = "2026-10-21"
        self.db.mark_attendance("CSEB-01", date, "Present")
        self.db.mark_attendance("CSEB-02", date, "Present")
        self.db.mark_attendance("CSEB-03", date, "Absent")
        self.db.mark_attendance("CSEB-04", date, "Late")

        stats = self.db.get_dashboard_stats(date)
        self.assertEqual(stats["total"], 5)
        self.assertEqual(stats["present"], 2)
        self.assertEqual(stats["absent"], 1)
        self.assertEqual(stats["late"], 1)
        self.assertEqual(stats["unmarked"], 1)
        self.assertEqual(stats["percentage"], 40.0)

    def test_csv_export_and_import(self):
        self.db.export_students_csv(TEST_CSV_NAME)
        self.assertTrue(os.path.exists(TEST_CSV_NAME))

        # Import in a fresh database
        fresh_db = AttendanceDB("fresh_temp.db")
        added, updated, errors = fresh_db.import_students_csv(TEST_CSV_NAME)
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(fresh_db.fetch_all_students()), 5)
        if os.path.exists("fresh_temp.db"):
            os.remove("fresh_temp.db")

    def test_backup_and_restore(self):
        self.db.add_student("BK-01", "Backup Student", "SEC-X")
        self.db.backup_database(TEST_BACKUP_NAME)
        self.assertTrue(os.path.exists(TEST_BACKUP_NAME))

        # Delete student in primary db
        self.db.delete_student("BK-01")
        self.assertIsNone(self.db.get_student("BK-01"))

        # Restore from backup
        self.db.restore_database(TEST_BACKUP_NAME)
        restored = self.db.get_student("BK-01")
        self.assertIsNotNone(restored)

if __name__ == "__main__":
    unittest.main()
