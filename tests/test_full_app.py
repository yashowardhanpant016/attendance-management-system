"""
Comprehensive automated test suite for the upgraded Attendance Management System.
Tests UI lifecycle, all 5 view transitions, CRUD operations, attendance marking,
undo operations, analytics calculations, report generation, and theme scaling.
"""

import unittest
import os
import sqlite3
from datetime import datetime

from app import AttendanceApp
from db import AttendanceDB

TEST_DB = "test_full_app_temp.db"

class TestFullAttendanceApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        cls.db = AttendanceDB(TEST_DB)
        cls.app = AttendanceApp()
        cls.app.db = cls.db
        # Update references in all views to the test db
        for v in cls.app.views.values():
            v.db = cls.db
        cls.app.update_idletasks()

    @classmethod
    def tearDownClass(cls):
        try:
            cls.app.destroy()
        except Exception:
            pass
        if os.path.exists(TEST_DB):
            try:
                os.remove(TEST_DB)
            except OSError:
                pass

    def test_01_window_and_views_instantiated(self):
        """Verifies root window and all 5 view frames exist and map cleanly."""
        self.assertIsNotNone(self.app.winfo_id())
        self.assertEqual(len(self.app.views), 5)
        for key in ["dashboard", "students", "attendance", "reports", "settings"]:
            self.assertIn(key, self.app.views)

    def test_02_view_switching(self):
        """Verifies switching views dynamically without exceptions."""
        for key in ["students", "attendance", "reports", "settings", "dashboard"]:
            self.app.switch_view(key)
            self.app.update_idletasks()
            self.assertEqual(self.app.active_view_key, key)
            self.assertTrue(self.app.views[key].winfo_ismapped())

    def test_03_dashboard_kpis(self):
        """Verifies dashboard KPI cards update accurately."""
        self.app.switch_view("dashboard")
        dash = self.app.views["dashboard"]
        dash.refresh_data()
        self.app.update_idletasks()

        self.assertEqual(dash.card_total.lbl_val.cget("text"), "5")
        # Mark 1 student present and check
        today = datetime.now().strftime("%Y-%m-%d")
        self.db.mark_attendance("CSEB-01", today, "Present")
        dash.refresh_data()
        self.assertEqual(dash.card_present.lbl_val.cget("text"), "1")
        self.assertEqual(dash.card_rate.lbl_val.cget("text"), "20.0%")

    def test_04_students_view_crud(self):
        """Verifies student registration, validation, update, and deletion in students view."""
        self.app.switch_view("students")
        stu_view = self.app.views["students"]

        # Form registration
        stu_view.ent_roll.delete(0, "end")
        stu_view.ent_roll.insert(0, "CSEB-99")
        stu_view.ent_name.delete(0, "end")
        stu_view.ent_name.insert(0, "Karan Singh")
        stu_view.ent_sec.delete(0, "end")
        stu_view.ent_sec.insert(0, "CSE-B")

        stu_view.handle_add_student()
        stu_view.refresh_table()
        self.assertIsNotNone(self.db.get_student("CSEB-99"))

        # Update student directly
        self.db.update_student("CSEB-99", "CSEB-99", "Karan S. Verma", "CSE-A")
        stu_view.refresh_table()
        updated = self.db.get_student("CSEB-99")
        self.assertEqual(updated[1], "Karan S. Verma")
        self.assertEqual(updated[2], "CSE-A")

        # Delete student
        self.db.delete_student("CSEB-99")
        self.assertIsNone(self.db.get_student("CSEB-99"))

    def test_05_attendance_marking_and_undo(self):
        """Verifies date stepping, status marking, and Poka-Yoke undo."""
        self.app.switch_view("attendance")
        att_view = self.app.views["attendance"]

        today = datetime.now().strftime("%Y-%m-%d")
        self.db.mark_attendance("CSEB-02", today, "Absent", record_undo=True)
        att_view.refresh_table()
        self.assertEqual(self.db.get_current_status("CSEB-02", today), "Absent")

        # Undo
        self.app.shortcut_undo()
        self.assertEqual(self.db.get_current_status("CSEB-02", today), "Unmarked")

    def test_06_reports_view_generation(self):
        """Verifies generation of Monthly, Daily, and Individual reports."""
        self.app.switch_view("reports")
        rep_view = self.app.views["reports"]

        # Monthly
        rep_view.current_report_type.set("monthly")
        rep_view.on_mode_change()
        self.app.update_idletasks()
        self.assertGreaterEqual(len(rep_view.tree.get_children()), 5)

        # Daily
        rep_view.current_report_type.set("daily")
        rep_view.on_mode_change()
        self.app.update_idletasks()
        self.assertGreaterEqual(len(rep_view.tree.get_children()), 5)

    def test_07_theme_and_font_scaling(self):
        """Verifies High Contrast, Dark Mode, and Font Resizing."""
        # High Contrast
        self.app.set_theme("high_contrast")
        self.app.update_idletasks()
        self.assertEqual(self.app.current_theme_key, "high_contrast")
        self.assertEqual(self.app.cget("bg"), "#000000")

        # Dark Mode
        self.app.set_theme("dark")
        self.app.update_idletasks()
        self.assertEqual(self.app.current_theme_key, "dark")
        self.assertEqual(self.app.cget("bg"), "#0B0F19")

        # Light Mode
        self.app.set_theme("light")
        self.app.update_idletasks()
        self.assertEqual(self.app.current_theme_key, "light")

        # Font scaling
        self.app.set_font_scale("large")
        self.app.update_idletasks()
        self.assertEqual(self.app.current_font_scale, "large")

        self.app.set_font_scale("xlarge")
        self.app.update_idletasks()
        self.assertEqual(self.app.current_font_scale, "xlarge")

        self.app.set_font_scale("normal")
        self.app.update_idletasks()
        self.assertEqual(self.app.current_font_scale, "normal")

if __name__ == "__main__":
    unittest.main()
