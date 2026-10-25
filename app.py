"""
BBAT104 - Fundamentals of TQM Course Project
Professional Attendance Management System (BTech Project Submission Edition)
Quality Goal: Q12 - Improve Accessibility

Rebuilt with CustomTkinter for an EduAttend / CampusEdge Clean White-Card SaaS Dashboard.

Features:
  1. Executive Administration Dashboard with Summary KPI Cards & Analytics Charts
  2. Student Enrollment & Records Directory with Poka-Yoke Validation & Edit Modal
  3. Daily & Historical Attendance Roll Call with Multi-Level Undo & Rapid Hotkeys
  4. Statistical Reports & Quality Analytics with CSV & PDF Export
  5. WCAG 2.1 AAA High Contrast, Low-Strain Dark Mode & Dynamic Font Resizing Engine
  6. Atomic Database Backup & Disaster Recovery Tools
Student: Yashowardhan Pant (CSE-B)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import customtkinter as ctk

# Import modular database, theme, and widget components
from db import AttendanceDB
from theme import THEMES, FONT_SIZES, get_theme, get_fonts
from widgets import AccessibleButton, CardFrame

# Import modular views
from views.dashboard_view import DashboardView
from views.students_view import StudentsView
from views.attendance_view import AttendanceView
from views.calendar_view import CalendarView
from views.reports_view import ReportsView
from views.settings_view import SettingsView
from views.audit_dialog import AuditLogDialog


class AttendanceApp(ctk.CTk):
    """
    Main Application Window and Navigation Controller.
    Implements a responsive SaaS educational ERP dashboard layout:
    - Canvas: Modern off-white light workspace `#F8FAFC`
    - Top Floating Header Card (`#FFFFFF`, `corner_radius=14`, border `#E2E8F0`)
    - Deep Slate Sidebar (`#0F172A`) with rounded pill navigation (`corner_radius=10`)
    - Central view routing, accessibility hotkeys, and dynamic theme engine.
    """
    def __init__(self):
        super().__init__()
        self.title("Attendance Management System - [BBAT104 TQM Project]")
        self.geometry("1160x780")
        self.minsize(1060, 680)

        # Core State
        self.db = AttendanceDB()
        self.current_theme_key = "light"  # Default: EduAttend White SaaS
        self.current_font_scale = "normal"
        self.active_view_key = "dashboard"
        self.current_role = "Faculty"      # Default: Faculty Mode (Role-based access)
        self.current_date = datetime.now().strftime("%Y-%m-%d")

        # Configure CustomTkinter defaults
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")

        # Build UI and setup services
        self.build_ui()
        self.setup_keyboard_shortcuts()
        self.apply_theme_and_font()
        self.switch_view("dashboard")

    def build_ui(self):
        """Constructs Top Floating Header Card, Deep Slate Sidebar, Content Area, and Status Bar."""
        # Top Floating Header Card
        self.header_card = CardFrame(self, corner_radius=14, border_width=1, border_color="#E2E8F0", fg_color="#FFFFFF")
        self.header_card.pack(fill=tk.X, side=tk.TOP, padx=16, pady=(12, 8))
        self.header_card.bind("<Configure>", self._on_header_resize)

        # Header Left: Brand and Section Title
        self.header_left = ctk.CTkFrame(self.header_card, fg_color="transparent")
        self.header_left.pack(side=tk.LEFT, fill=tk.Y, padx=14, pady=8)

        self.lbl_brand = ctk.CTkLabel(
            self.header_left,
            text="🎓 BBAT104 Attendance Pro",
            font=("SF Pro Display", 15, "bold"),
            text_color="#0F172A",
            anchor="w"
        )
        self.lbl_brand.pack(side=tk.LEFT)

        self.lbl_view_title = ctk.CTkLabel(
            self.header_left,
            text="• Dashboard Overview",
            font=("SF Pro Display", 12),
            text_color="#64748B",
            anchor="w"
        )
        self.lbl_view_title.pack(side=tk.LEFT, padx=(10, 0))

        # Header Right: Quick Action Controls (Rounded Pills)
        self.header_right = ctk.CTkFrame(self.header_card, fg_color="transparent")
        self.header_right.pack(side=tk.RIGHT, fill=tk.Y, padx=12, pady=6)

        self.btn_role = AccessibleButton(
            self.header_right,
            text="👤 Role: Faculty",
            command=self.toggle_role,
            corner_radius=10,
            takefocus=True
        )
        self.btn_role.pack(side=tk.RIGHT, padx=4)

        self.btn_help = AccessibleButton(
            self.header_right,
            text="❓ Help [F1]",
            command=self.show_accessibility_guide,
            corner_radius=10,
            takefocus=True
        )
        self.btn_help.pack(side=tk.RIGHT, padx=4)

        self.btn_contrast = AccessibleButton(
            self.header_right,
            text="⚡ Contrast [Ctrl+H]",
            command=self.toggle_high_contrast,
            corner_radius=10,
            takefocus=True
        )
        self.btn_contrast.pack(side=tk.RIGHT, padx=4)

        self.btn_dark = AccessibleButton(
            self.header_right,
            text="🌙 Dark [Ctrl+D]",
            command=self.toggle_dark_mode,
            corner_radius=10,
            takefocus=True
        )
        self.btn_dark.pack(side=tk.RIGHT, padx=4)

        self.btn_font = AccessibleButton(
            self.header_right,
            text="Aa Font [Ctrl+T]",
            command=self.cycle_font_size,
            corner_radius=10,
            takefocus=True
        )
        self.btn_font.pack(side=tk.RIGHT, padx=4)

        # Status Bar at Bottom
        self.status_bar_frame = ctk.CTkFrame(self, height=28, corner_radius=0, fg_color="transparent")
        self.status_bar_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=16, pady=(0, 6))

        self.btn_status_audit = AccessibleButton(
            self.status_bar_frame,
            text="📜 Audit Log",
            command=self.show_audit_log,
            corner_radius=6,
            takefocus=True
        )
        self.btn_status_audit.pack(side=tk.RIGHT, padx=(4, 0))

        self.btn_status_undo = AccessibleButton(
            self.status_bar_frame,
            text="↩️ Undo [Ctrl+Z]",
            command=self.shortcut_undo,
            corner_radius=6,
            takefocus=True
        )
        self.btn_status_undo.pack(side=tk.RIGHT, padx=4)

        self.status_bar = ctk.CTkLabel(
            self.status_bar_frame,
            text=f"System Online | Role: Faculty | Database: {self.db.db_name} | Press F1 for Guide",
            font=("SF Pro Display", 10),
            text_color="#64748B",
            anchor="w"
        )
        self.status_bar.pack(fill=tk.X, side=tk.LEFT, expand=True)

        # Main Workspace Container (Sidebar on left, Content on right)
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 6))

        # -----------------------------------------------------
        # Deep Slate Navigation Sidebar (#0F172A)
        # -----------------------------------------------------
        self.sidebar = ctk.CTkFrame(
            self.main_container,
            width=230,
            corner_radius=14,
            border_width=1,
            border_color="#1E293B",
            fg_color="#0F172A"
        )
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        self.sidebar.pack_propagate(False)

        self.lbl_nav_heading = ctk.CTkLabel(
            self.sidebar,
            text="MAIN NAVIGATION",
            font=("SF Pro Display", 9, "bold"),
            text_color="#94A3B8",
            anchor="w"
        )
        self.lbl_nav_heading.pack(fill=tk.X, pady=(14, 8), padx=14)

        # Sidebar Navigation Pill Buttons
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "📊  Dashboard"),
            ("students", "👥  Manage Students"),
            ("attendance", "📋  Daily Attendance"),
            ("calendar", "📅  Monthly Calendar"),
            ("reports", "📈  Reports & Analytics"),
            ("settings", "⚙️  Settings & Backup")
        ]

        for key, label in nav_items:
            btn = AccessibleButton(
                self.sidebar,
                text=label,
                command=lambda k=key: self.switch_view(k),
                anchor="w",
                corner_radius=8,
                padx=14,
                pady=8
            )
            btn.pack(fill=tk.X, padx=10, pady=3)
            self.nav_buttons[key] = btn

        # Sidebar Academic Project Credits Footer
        self.sidebar_footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.sidebar_footer.pack(side=tk.BOTTOM, fill=tk.X, padx=12, pady=(0, 14))

        self.lbl_credit_name = ctk.CTkLabel(
            self.sidebar_footer,
            text="Yashowardhan Pant",
            font=("SF Pro Display", 10, "bold"),
            text_color="#F8FAFC",
            anchor="w"
        )
        self.lbl_credit_name.pack(fill=tk.X)

        self.lbl_credit_sec = ctk.CTkLabel(
            self.sidebar_footer,
            text="Section: CSE-B",
            font=("SF Pro Display", 9),
            text_color="#94A3B8",
            anchor="w"
        )
        self.lbl_credit_sec.pack(fill=tk.X)

        self.lbl_credit_goal = ctk.CTkLabel(
            self.sidebar_footer,
            text="Goal: Q12 Accessibility",
            font=("SF Pro Display", 9, "italic"),
            text_color="#64748B",
            anchor="w"
        )
        self.lbl_credit_goal.pack(fill=tk.X)

        # -----------------------------------------------------
        # Right View Workspace Frame
        # -----------------------------------------------------
        self.view_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.view_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Instantiate View Frames
        self.views = {
            "dashboard": DashboardView(self.view_container, self.db, self.switch_view, self),
            "students": StudentsView(self.view_container, self.db, self),
            "attendance": AttendanceView(self.view_container, self.db, self),
            "calendar": CalendarView(self.view_container, self.db, self),
            "reports": ReportsView(self.view_container, self.db, self),
            "settings": SettingsView(self.view_container, self.db, self)
        }

        for view in self.views.values():
            view.pack(fill=tk.BOTH, expand=True)
            view.pack_forget()

    # ---------------------------------------------------------
    # View Switching & Routing
    # ---------------------------------------------------------
    def switch_view(self, view_key):
        if view_key not in self.views:
            return

        self.active_view_key = view_key

        # Hide all views and reveal active view
        for k, view in self.views.items():
            if k == view_key:
                view.pack(fill=tk.BOTH, expand=True)
                if hasattr(view, "refresh_data"):
                    view.refresh_data()
                elif hasattr(view, "refresh_table"):
                    view.refresh_table()
                elif hasattr(view, "generate_report"):
                    view.generate_report()
            else:
                view.pack_forget()

        # Update Top Header Subtitle
        title_map = {
            "dashboard": "• Operations Dashboard",
            "students": "• Student Directory & Enrollment",
            "attendance": "• Daily Attendance Roll Call",
            "calendar": "• Student Monthly Attendance Calendar",
            "reports": "• Statistical Reports & Quality Analytics",
            "settings": "• System Configuration & Backup"
        }
        self.lbl_view_title.configure(text=title_map.get(view_key, ""))

        # Update Sidebar Highlighting
        self.update_sidebar_styling()
        self.status_bar.configure(text=f"Active Section: {view_key.capitalize()} | Role: {self.current_role} | Date: {self.current_date}")

    def notify_data_updated(self):
        """Called by child views to notify data changes across all modules."""
        for view in self.views.values():
            if hasattr(view, "refresh_data"):
                view.refresh_data()
            elif hasattr(view, "refresh_table"):
                view.refresh_table()

    # ---------------------------------------------------------
    # Keyboard Navigation & Hotkeys
    # ---------------------------------------------------------
    def setup_keyboard_shortcuts(self):
        """Comprehensive BTech Submission Keyboard Navigation Suite."""
        # View Switching (Ctrl+1 through Ctrl+6)
        self.bind("<Control-Key-1>", lambda e: self.switch_view("dashboard"))
        self.bind("<Control-Key-2>", lambda e: self.switch_view("students"))
        self.bind("<Control-Key-3>", lambda e: self.switch_view("attendance"))
        self.bind("<Control-Key-4>", lambda e: self.switch_view("calendar"))
        self.bind("<Control-Key-5>", lambda e: self.switch_view("reports"))
        self.bind("<Control-Key-6>", lambda e: self.switch_view("settings"))

        # Mac Command Key Equivalents
        self.bind("<Command-Key-1>", lambda e: self.switch_view("dashboard"))
        self.bind("<Command-Key-2>", lambda e: self.switch_view("students"))
        self.bind("<Command-Key-3>", lambda e: self.switch_view("attendance"))
        self.bind("<Command-Key-4>", lambda e: self.switch_view("calendar"))
        self.bind("<Command-Key-5>", lambda e: self.switch_view("reports"))
        self.bind("<Command-Key-6>", lambda e: self.switch_view("settings"))

        # High Contrast Toggle (Ctrl+H)
        self.bind("<Control-h>", lambda e: self.toggle_high_contrast())
        self.bind("<Control-H>", lambda e: self.toggle_high_contrast())

        # Dark Mode Toggle (Ctrl+D, Cmd+D)
        self.bind("<Control-d>", lambda e: self.toggle_dark_mode())
        self.bind("<Control-D>", lambda e: self.toggle_dark_mode())
        self.bind("<Command-d>", lambda e: self.toggle_dark_mode())
        self.bind("<Command-D>", lambda e: self.toggle_dark_mode())

        # Font Resizing Cycle (Ctrl+T, Cmd+T)
        self.bind("<Control-t>", lambda e: self.cycle_font_size())
        self.bind("<Control-T>", lambda e: self.cycle_font_size())
        self.bind("<Command-t>", lambda e: self.cycle_font_size())
        self.bind("<Command-T>", lambda e: self.cycle_font_size())

        # Jump to Student Input (Ctrl+A)
        self.bind("<Control-a>", lambda e: self.shortcut_focus_add())
        self.bind("<Control-A>", lambda e: self.shortcut_focus_add())

        # Quick Mark Present (Ctrl+M, Cmd+M)
        self.bind("<Control-m>", lambda e: self.shortcut_quick_mark_present())
        self.bind("<Control-M>", lambda e: self.shortcut_quick_mark_present())
        self.bind("<Command-m>", lambda e: self.shortcut_quick_mark_present())
        self.bind("<Command-M>", lambda e: self.shortcut_quick_mark_present())

        # Jump to Filter/Search Box (Ctrl+S, Cmd+S)
        self.bind("<Control-s>", lambda e: self.shortcut_focus_search())
        self.bind("<Control-S>", lambda e: self.shortcut_focus_search())
        self.bind("<Command-s>", lambda e: self.shortcut_focus_search())
        self.bind("<Command-S>", lambda e: self.shortcut_focus_search())

        # Undo Last Action (Ctrl+Z, Cmd+Z)
        self.bind("<Control-z>", lambda e: self.shortcut_undo())
        self.bind("<Control-Z>", lambda e: self.shortcut_undo())
        self.bind("<Command-z>", lambda e: self.shortcut_undo())
        self.bind("<Command-Z>", lambda e: self.shortcut_undo())

        # Accessibility Help Reference Modal (F1)
        self.bind("<Escape>", lambda e: None)
        self.bind("<F1>", lambda e: self.show_accessibility_guide())

    def shortcut_focus_add(self):
        self.switch_view("students")
        self.views["students"].ent_roll.focus_set()
        self.views["students"].ent_roll.select_range(0, tk.END)

    def shortcut_focus_search(self):
        active = self.views.get(self.active_view_key)
        if hasattr(active, "search_box"):
            active.search_box.focus_set()
            active.search_box.select_range(0, tk.END)

    def shortcut_quick_mark_present(self):
        if self.active_view_key != "attendance":
            self.switch_view("attendance")
        self.views["attendance"].handle_mark("Present")

    def shortcut_undo(self):
        """Feature 7: Global Undo Last Attendance Change."""
        res = self.db.undo_last_mark(user_role=self.current_role)
        if res:
            self.status_bar.configure(
                text=f"↩️ Reverted {res['roll_no']} on {res['date']} from '{res['reverted_from']}' to '{res['restored_to']}'"
            )
            self.notify_data_updated()
            messagebox.showinfo(
                "Undo Completed",
                f"Successfully reverted attendance mark:\n\nStudent: {res['roll_no']}\nDate: {res['date']}\nReverted from: '{res['reverted_from']}' ➜ Restored: '{res['restored_to']}'"
            )
        else:
            att_view = self.views.get("attendance")
            if att_view and hasattr(att_view, "undo_stack") and att_view.undo_stack:
                att_view.handle_undo()
            else:
                self.status_bar.configure(text="No remaining actions in undo history.")
                messagebox.showinfo("Undo", "No remaining actions to undo.")

    def toggle_role(self):
        """Feature 4: Toggle between Faculty Mode and Admin Mode."""
        if self.current_role == "Faculty":
            self.current_role = "Admin"
            self.status_bar.configure(text="Switched to: Admin Mode (Student deletion & database tools unlocked)")
        else:
            self.current_role = "Faculty"
            self.status_bar.configure(text="Switched to: Faculty Mode (Daily roll call & analytics enabled)")

        self.db.log_audit_event("ROLE_SWITCH", f"User switched role to {self.current_role}", self.current_role)
        self.propagate_role()
        self.apply_theme_and_font()

    def propagate_role(self):
        """Propagates active role permissions across all views."""
        for view in self.views.values():
            if hasattr(view, "update_role_permissions"):
                view.update_role_permissions(self.current_role)

    def show_audit_log(self):
        """Feature 7: Launch System Audit Trail Viewer Modal."""
        AuditLogDialog(
            parent=self,
            db=self.db,
            theme=self.current_theme_key,
            font_cfg=FONT_SIZES[self.current_font_scale]
        )

    # ---------------------------------------------------------
    # Accessibility & Theme Engine
    # ---------------------------------------------------------
    def apply_theme_and_font(self):
        """Applies dynamic theme colors and font sizes synchronously across all widgets."""
        theme = get_theme(self.current_theme_key)
        font_cfg = get_fonts(self.current_font_scale)

        # Sync CTk Appearance Mode
        if self.current_theme_key == "dark":
            ctk.set_appearance_mode("Dark")
        elif self.current_theme_key == "high_contrast":
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")

        # Top-level window canvas
        self.configure(fg_color=theme["bg"])

        # Top Header Card
        self.header_card.configure(fg_color=theme["header_bg"], border_color=theme["card_border"])
        self.lbl_brand.configure(
            text_color=theme["header_fg"],
            font=font_cfg.get("app_title", font_cfg["header_bold"])
        )
        self.lbl_view_title.configure(
            text_color=theme["fg_muted"],
            font=font_cfg.get("section_title", font_cfg["title"])
        )
        self.status_bar.configure(
            text_color=theme["fg_muted"],
            font=font_cfg.get("status_font", ("SF Pro Display", font_cfg["body"]))
        )

        # Header Pill Buttons
        pad_x = font_cfg["btn_pad_x"]
        pad_y = font_cfg["btn_pad_y"]
        for btn in [self.btn_font, self.btn_dark, self.btn_contrast, self.btn_help]:
            btn.apply_style(
                bg=theme["btn_secondary_bg"],
                fg=theme["btn_secondary_fg"],
                font=font_cfg.get("btn_font", ("SF Pro Display", font_cfg["body"])),
                focus_ring=theme["focus_ring"],
                border_color=theme["btn_secondary_border"],
                padx=pad_x - 1,
                pady=pad_y - 1
            )

        # Feature 4: Role Switcher Pill Styling
        is_hc = theme.get("is_high_contrast", False)
        if self.current_role == "Admin":
            self.btn_role.apply_style(
                bg=theme.get("role_admin_bg", "#FEF3C7"),
                fg=theme.get("role_admin_fg", "#92400E"),
                font=font_cfg.get("btn_bold", ("SF Pro Display", font_cfg["body"], "bold")),
                focus_ring=theme["focus_ring"],
                border_color=theme.get("role_admin_bg", "#FEF3C7"),
                padx=pad_x - 1,
                pady=pad_y - 1
            )
            self.btn_role.configure(text="🛡️ Role: Admin")
        else:
            self.btn_role.apply_style(
                bg=theme.get("role_faculty_bg", "#EFF6FF"),
                fg=theme.get("role_faculty_fg", "#1D4ED8"),
                font=font_cfg.get("btn_bold", ("SF Pro Display", font_cfg["body"], "bold")),
                focus_ring=theme["focus_ring"],
                border_color=theme.get("role_faculty_bg", "#EFF6FF"),
                padx=pad_x - 1,
                pady=pad_y - 1
            )
            self.btn_role.configure(text="👤 Role: Faculty")

        # Bottom Status Bar Quick Action Buttons
        for sbtn in [self.btn_status_undo, self.btn_status_audit]:
            sbtn.apply_style(
                bg=theme["btn_secondary_bg"],
                fg=theme["btn_secondary_fg"],
                font=font_cfg.get("status_font", ("SF Pro Display", font_cfg["body"] - 1)),
                focus_ring=theme["focus_ring"],
                border_color=theme["btn_secondary_border"],
                padx=6,
                pady=2
            )

        # Update Button Toggle Labels
        if self.current_font_scale == "xlarge":
            self.btn_font.configure(text=f"Aa [{self.current_font_scale[0].upper()}] [Ctrl+T]")
            self.btn_contrast.configure(text="⚡ Contrast [Ctrl+H]")
        else:
            self.btn_font.configure(text=f"Aa Font: {self.current_font_scale.capitalize()} [Ctrl+T]")
            self.btn_contrast.configure(text="⚡ Std Contrast [Ctrl+H]" if self.current_theme_key == "high_contrast" else "⚡ Contrast [Ctrl+H]")
        self.btn_dark.configure(text="☀️ Light [Ctrl+D]" if self.current_theme_key == "dark" else "🌙 Dark [Ctrl+D]")
        self.btn_help.configure(text="❓ Help [F1]")

        # Dynamic Sidebar Width based on Font Scale
        new_sb_width = font_cfg.get("sidebar_width", 230)
        self.sidebar.configure(
            width=new_sb_width,
            fg_color=theme["sidebar_bg"],
            border_color=theme["card_border"]
        )

        # Sidebar Footer
        self.lbl_nav_heading.configure(
            text_color=theme["sidebar_fg"] if theme.get("is_high_contrast") else "#94A3B8",
            font=font_cfg.get("badge_font", ("SF Pro Display", 9, "bold"))
        )
        self.lbl_credit_name.configure(
            text_color=theme["sidebar_fg"],
            font=font_cfg.get("body_bold", ("SF Pro Display", 10, "bold"))
        )
        self.lbl_credit_sec.configure(
            text_color=theme["sidebar_fg"] if theme.get("is_high_contrast") else "#94A3B8",
            font=font_cfg.get("status_font", ("SF Pro Display", 9))
        )
        self.lbl_credit_goal.configure(
            text_color=theme["sidebar_fg"] if theme.get("is_high_contrast") else "#64748B",
            font=font_cfg.get("status_font", ("SF Pro Display", 9, "italic"))
        )

        # Update Sidebar button styles
        self.update_sidebar_styling()

        # Propagate theme to all child views
        for view in self.views.values():
            if hasattr(view, "apply_theme"):
                view.apply_theme(theme, font_cfg)

    def _on_header_resize(self, event):
        if event.width < 1080 and self.current_font_scale == "xlarge":
            self.lbl_view_title.pack_forget()
        elif event.width < 980:
            self.lbl_view_title.pack_forget()
        else:
            if not self.lbl_view_title.winfo_ismapped():
                self.lbl_view_title.pack(side=tk.LEFT, padx=(10, 0))

    def update_sidebar_styling(self):
        theme = THEMES[self.current_theme_key]
        is_hc = theme.get("is_high_contrast", False)

        for key, btn in self.nav_buttons.items():
            if key == self.active_view_key:
                # Active Tab: Retain vibrant Electric Blue (#2563EB) with crisp white #FFFFFF bold text
                btn.apply_style(
                    bg=theme.get("sidebar_active_bg", "#2563EB"),
                    hover=theme.get("sidebar_active_bg", "#2563EB"),
                    fg="#000000" if is_hc else "#FFFFFF",
                    font=("SF Pro Display", 12, "bold"),
                    focus_ring=theme["focus_ring"],
                    border_color=theme.get("sidebar_active_bg", "#2563EB"),
                    corner_radius=8,
                    padx=14,
                    pady=8
                )
                btn.configure(corner_radius=8)
            else:
                # Inactive button: High contrast crisp text #CBD5E1, font size 12 bold, hover #1E293B
                inactive_fg = "#FFFF00" if is_hc else theme.get("sidebar_text", "#CBD5E1")
                hover_bg = "#222222" if is_hc else theme.get("sidebar_hover_bg", "#1E293B")
                btn.apply_style(
                    bg="transparent",
                    hover=hover_bg,
                    fg=inactive_fg,
                    font=("SF Pro Display", 12, "bold"),
                    focus_ring=theme["focus_ring"],
                    border_color=theme.get("sidebar_bg", "#0B0F19"),
                    corner_radius=8,
                    bd=0,
                    padx=14,
                    pady=8
                )
                btn.configure(corner_radius=8)

    def set_theme(self, theme_key):
        if theme_key in THEMES:
            self.current_theme_key = theme_key
            self.apply_theme_and_font()
            self.status_bar.configure(text=f"Theme set to: {THEMES[self.current_theme_key]['name']}")

    def toggle_high_contrast(self):
        """Feature 1: WCAG AAA High Contrast Toggle."""
        if self.current_theme_key == "high_contrast":
            self.set_theme("light")
        else:
            self.set_theme("high_contrast")

    def toggle_dark_mode(self):
        """Feature 4: Low-Strain Dark Mode Toggle."""
        if self.current_theme_key == "dark":
            self.set_theme("light")
        else:
            self.set_theme("dark")

    def set_font_scale(self, scale_key):
        """Feature 2: Dynamic Font Resizing."""
        if scale_key in FONT_SIZES:
            self.current_font_scale = scale_key
            self.apply_theme_and_font()
            self.status_bar.configure(text=f"Font Scale: {self.current_font_scale.upper()}")

    def cycle_font_size(self):
        scales = ["normal", "large", "xlarge"]
        idx = (scales.index(self.current_font_scale) + 1) % len(scales)
        self.set_font_scale(scales[idx])

    def show_accessibility_guide(self):
        """Feature 3: Comprehensive Accessibility Reference Dialog."""
        guide = (
            "BBAT104 Attendance Pro - Accessibility Guide (Q12)\n"
            "═══════════════════════════════════════════════════════\n\n"
            "NAVIGATION SHORTCUTS:\n"
            "• Ctrl + 1 : Operations Dashboard\n"
            "• Ctrl + 2 : Manage Students Directory & Enrollment\n"
            "• Ctrl + 3 : Daily Attendance Roll Call\n"
            "• Ctrl + 4 : Student Monthly Attendance Calendar (7x5 Grid)\n"
            "• Ctrl + 5 : Statistical Reports & Quality Analytics\n"
            "• Ctrl + 6 : System Configuration, Audit Log & Backup\n\n"
            "ACCESSIBILITY & DISPLAY CONTROLS:\n"
            "• Ctrl + H : Toggle High Contrast Mode (Pure Black #000000 & Yellow #FFFF00)\n"
            "• Ctrl + D : Toggle Low-Luminance Dark Slate Mode (#0F172A)\n"
            "• Ctrl + T : Cycle Dynamic Font Scale (Normal ➜ Large ➜ X-Large)\n"
            "• F1       : Open this Accessibility Reference Modal\n\n"
            "DATA ENTRY & OPERATIONAL ACTIONS:\n"
            "• Ctrl + A : Jump focus to Student Registration input\n"
            "• Ctrl + S : Jump focus to Table Search / Filter box\n"
            "• Ctrl + M : Quick mark selected student as PRESENT\n"
            "• Space Bar: Quick mark selected student as ABSENT\n"
            "• L Key    : Mark selected student as LATE\n"
            "• Ctrl + Z : Revert last attendance change (Poka-Yoke)\n"
            "• P Key    : Export Institutional Student PDF Report Card\n"
            "• Tab / Shift+Tab : Seamlessly traverse all interactive elements\n\n"
            "ROLE-BASED ACCESS CONTROL (RBAC):\n"
            "• Faculty Mode: Daily attendance, multi-metric analytics, student calendar\n"
            "• Admin Mode  : Student deletion, batch CSV validation, database restore"
        )
        messagebox.showinfo("Accessibility & Keyboard Shortcuts", guide)


# Re-export key components for backward compatibility
AccessibleAttendanceApp = AttendanceApp

if __name__ == "__main__":
    app = AttendanceApp()
    app.mainloop()
