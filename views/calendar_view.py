"""
Student Monthly Attendance Calendar View.
Feature 3: Interactive 7x5 monthly day-grid visualizer with quality state markers.
Colors day tiles clearly:
  - Green tile (#10B981 / #DCFCE7) for Present
  - Red tile (#EF4444 / #FEE2E2) for Absent
  - Amber tile (#F59E0B / #FEF3C7) for Late
  - Neutral tile for Weekends / Holidays / No Session
Compatible with High Contrast mode (displays 'P', 'A', 'L' text markers inside each cell).
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
import calendar
import customtkinter as ctk

from widgets import AccessibleButton, FocusRingEntry, CardFrame
from theme import get_theme, get_fonts
from pdf_exporter import generate_student_report_card


class CalendarView(ctk.CTkFrame):
    def __init__(self, master, db=None, app_controller=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.db = db
        self.app = app_controller
        now = datetime.now()
        self.current_year = now.year
        self.current_month = now.month
        self.selected_roll = None

        self.current_theme = None
        self.current_font_cfg = None
        self.day_tiles = []

        self.build_ui()

    def build_ui(self):
        # Header banner
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill=tk.X, pady=(0, 10))

        self.lbl_title = ctk.CTkLabel(
            self.header_frame,
            text="Student Monthly Attendance Calendar",
            font=("SF Pro Display", 15, "bold"),
            text_color="#0F172A",
            anchor="w"
        )
        self.lbl_title.pack(side=tk.LEFT)

        self.lbl_badge = ctk.CTkLabel(
            self.header_frame,
            text="Interactive 7x5 Grid with State Markers",
            font=("SF Pro Display", 11),
            text_color="#64748B",
            anchor="e"
        )
        self.lbl_badge.pack(side=tk.RIGHT)

        # -----------------------------------------------------
        # Top Control Bar (Student Selector & Month Navigator)
        # -----------------------------------------------------
        self.control_bar = CardFrame(self, corner_radius=14, border_width=1, border_color="#E2E8F0", fg_color="#FFFFFF")
        self.control_bar.pack(fill=tk.X, pady=(0, 8))

        # Left: Student Selector
        self.student_group = ctk.CTkFrame(self.control_bar, fg_color="transparent")
        self.student_group.pack(side=tk.LEFT, padx=14, pady=8)

        self.lbl_sel_student = ctk.CTkLabel(self.student_group, text="Student:", font=("SF Pro Display", 11, "bold"), text_color="#0F172A")
        self.lbl_sel_student.pack(side=tk.LEFT, padx=(0, 6))

        self.student_combo = ttk.Combobox(self.student_group, state="readonly", width=24)
        self.student_combo.pack(side=tk.LEFT, padx=4)
        self.student_combo.bind("<<ComboboxSelected>>", lambda e: self.on_student_change())

        # Middle: Month Navigator
        self.month_group = ctk.CTkFrame(self.control_bar, fg_color="transparent")
        self.month_group.pack(side=tk.LEFT, padx=16, pady=8)

        self.btn_prev_month = AccessibleButton(self.month_group, text="◀ Prev", command=self.prev_month, corner_radius=8)
        self.btn_prev_month.pack(side=tk.LEFT, padx=2)

        self.lbl_month_display = ctk.CTkLabel(
            self.month_group,
            text=f"{calendar.month_name[self.current_month]} {self.current_year}",
            font=("SF Pro Display", 12, "bold"),
            text_color="#0F172A",
            width=130,
            anchor="center"
        )
        self.lbl_month_display.pack(side=tk.LEFT, padx=6)

        self.btn_next_month = AccessibleButton(self.month_group, text="Next ▶", command=self.next_month, corner_radius=8)
        self.btn_next_month.pack(side=tk.LEFT, padx=2)

        self.btn_today_month = AccessibleButton(self.month_group, text="Current Month", command=self.reset_to_current_month, corner_radius=8)
        self.btn_today_month.pack(side=tk.LEFT, padx=(6, 2))

        # Right: Quick PDF Export Button
        self.btn_export_pdf = AccessibleButton(
            self.control_bar,
            text="📄 Export Student PDF Report Card",
            command=self.handle_export_pdf,
            corner_radius=10
        )
        self.btn_export_pdf.pack(side=tk.RIGHT, padx=14, pady=8)

        # -----------------------------------------------------
        # Monthly Metric Summary Bar (Floating White Card)
        # -----------------------------------------------------
        self.kpi_bar = CardFrame(self, corner_radius=14, border_width=1, border_color="#E2E8F0", fg_color="#FFFFFF")
        self.kpi_bar.pack(fill=tk.X, pady=(0, 10))

        self.lbl_stat_sessions = ctk.CTkLabel(self.kpi_bar, text="Sessions: 0", font=("SF Pro Display", 11, "bold"), text_color="#0F172A")
        self.lbl_stat_sessions.pack(side=tk.LEFT, padx=14, pady=8)

        self.lbl_stat_p = ctk.CTkLabel(self.kpi_bar, text="● Present: 0", font=("SF Pro Display", 11, "bold"), text_color="#10B981")
        self.lbl_stat_p.pack(side=tk.LEFT, padx=12, pady=8)

        self.lbl_stat_a = ctk.CTkLabel(self.kpi_bar, text="● Absent: 0", font=("SF Pro Display", 11, "bold"), text_color="#EF4444")
        self.lbl_stat_a.pack(side=tk.LEFT, padx=12, pady=8)

        self.lbl_stat_l = ctk.CTkLabel(self.kpi_bar, text="● Late: 0", font=("SF Pro Display", 11, "bold"), text_color="#F59E0B")
        self.lbl_stat_l.pack(side=tk.LEFT, padx=12, pady=8)

        self.lbl_stat_rate = ctk.CTkLabel(self.kpi_bar, text="Monthly Rate: 0.0%", font=("SF Pro Display", 12, "bold"), text_color="#2563EB")
        self.lbl_stat_rate.pack(side=tk.RIGHT, padx=14, pady=8)

        self.lbl_shortfall_badge = ctk.CTkLabel(
            self.kpi_bar,
            text="",
            font=("SF Pro Display", 11, "bold"),
            text_color="#B91C1C"
        )
        self.lbl_shortfall_badge.pack(side=tk.RIGHT, padx=8, pady=8)

        # -----------------------------------------------------
        # Main Calendar Container (Floating White Card)
        # -----------------------------------------------------
        self.cal_card = CardFrame(self, corner_radius=14, border_width=1, border_color="#E2E8F0", fg_color="#FFFFFF")
        self.cal_card.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        # Weekdays Header Row
        self.weekdays_bar = ctk.CTkFrame(self.cal_card, fg_color="transparent")
        self.weekdays_bar.pack(fill=tk.X, padx=14, pady=(12, 4))
        for col in range(7):
            self.weekdays_bar.columnconfigure(col, weight=1)

        weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        self.weekday_labels = []
        for col, wname in enumerate(weekday_names):
            lbl = ctk.CTkLabel(
                self.weekdays_bar,
                text=wname,
                font=("SF Pro Display", 11, "bold"),
                text_color="#475569" if col < 5 else "#94A3B8"
            )
            lbl.grid(row=0, column=col, sticky="nsew", padx=2, pady=2)
            self.weekday_labels.append(lbl)

        # Grid Container for Day Tiles
        self.grid_container = ctk.CTkFrame(self.cal_card, fg_color="transparent")
        self.grid_container.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 10))

        for col in range(7):
            self.grid_container.columnconfigure(col, weight=1)
        for r in range(6):
            self.grid_container.rowconfigure(r, weight=1)

        # Legend Bar at bottom of card
        self.legend_bar = ctk.CTkFrame(self.cal_card, fg_color="transparent")
        self.legend_bar.pack(fill=tk.X, padx=14, pady=(0, 12))

        self.lbl_leg_p = ctk.CTkLabel(self.legend_bar, text="● Present [P]", font=("SF Pro Display", 10, "bold"), text_color="#10B981")
        self.lbl_leg_p.pack(side=tk.LEFT, padx=(0, 14))

        self.lbl_leg_a = ctk.CTkLabel(self.legend_bar, text="● Absent [A]", font=("SF Pro Display", 10, "bold"), text_color="#EF4444")
        self.lbl_leg_a.pack(side=tk.LEFT, padx=14)

        self.lbl_leg_l = ctk.CTkLabel(self.legend_bar, text="● Late [L]", font=("SF Pro Display", 10, "bold"), text_color="#F59E0B")
        self.lbl_leg_l.pack(side=tk.LEFT, padx=14)

        self.lbl_leg_n = ctk.CTkLabel(self.legend_bar, text="○ No Session / Weekend", font=("SF Pro Display", 10), text_color="#64748B")
        self.lbl_leg_n.pack(side=tk.LEFT, padx=14)

    def populate_students(self):
        students = self.db.fetch_all_students()
        options = [f"{s[0]} - {s[1]} ({s[2]})" for s in students]
        self.student_combo["values"] = options
        if options:
            if not self.selected_roll:
                self.student_combo.set(options[0])
                self.selected_roll = students[0][0]
            else:
                for opt in options:
                    if opt.startswith(self.selected_roll):
                        self.student_combo.set(opt)
                        break

    def on_student_change(self):
        sel = self.student_combo.get()
        if sel:
            self.selected_roll = sel.split(" - ")[0]
            self.refresh_calendar()

    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.refresh_calendar()

    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.refresh_calendar()

    def reset_to_current_month(self):
        now = datetime.now()
        self.current_year = now.year
        self.current_month = now.month
        self.refresh_calendar()

    def refresh_data(self):
        self.populate_students()
        self.refresh_calendar()

    def refresh_calendar(self):
        if not self.selected_roll:
            self.populate_students()
            if not self.selected_roll:
                return

        # Update Month Title
        self.lbl_month_display.configure(text=f"{calendar.month_name[self.current_month]} {self.current_year}")

        # Fetch Month Attendance Data from DB
        cal_data = self.db.get_student_month_calendar(self.selected_roll, self.current_year, self.current_month)
        day_marks = cal_data["days"]
        p_count = cal_data["present"]
        a_count = cal_data["absent"]
        l_count = cal_data["late"]
        tot_count = cal_data["total"]
        pct = cal_data["percentage"]

        self.lbl_stat_sessions.configure(text=f"Logged Classes: {tot_count}")
        self.lbl_stat_p.configure(text=f"● Present: {p_count}")
        self.lbl_stat_a.configure(text=f"● Absent: {a_count}")
        self.lbl_stat_l.configure(text=f"● Late: {l_count}")
        self.lbl_stat_rate.configure(text=f"Monthly Rate: {pct:.1f}%")

        shortfall = self.db.calculate_shortfall(p_count, tot_count, 0.75)
        if tot_count > 0 and pct < 75.0:
            self.lbl_shortfall_badge.configure(text=f"⚠️ SHORTFALL: Needs {shortfall} more consecutive classes for 75%")
        else:
            self.lbl_shortfall_badge.configure(text="✅ ELIGIBLE (>= 75%)" if tot_count > 0 else "")

        # Clear existing day tiles
        for tile in self.day_tiles:
            tile.destroy()
        self.day_tiles.clear()

        # Compute calendar layout
        first_weekday, num_days = calendar.monthrange(self.current_year, self.current_month)
        # first_weekday: Monday is 0, Sunday is 6

        theme = self.current_theme or {}
        is_hc = theme.get("is_high_contrast", False)

        cal_cell_bg = theme.get("cal_cell_bg", "#FFFFFF")
        cal_border = theme.get("cal_cell_border", "#E2E8F0")

        row = 0
        col = first_weekday

        for day in range(1, num_days + 1):
            is_weekend = (col >= 5)
            stat = day_marks.get(day, None)

            # Determine styling and label text
            if stat == "Present":
                bg_color = theme.get("cal_present_bg", "#DCFCE7")
                fg_color = theme.get("cal_present_fg", "#15803D")
                marker_text = "● Present [P]" if not is_hc else "P - PRESENT"
            elif stat == "Absent":
                bg_color = theme.get("cal_absent_bg", "#FEE2E2")
                fg_color = theme.get("cal_absent_fg", "#B91C1C")
                marker_text = "● Absent [A]" if not is_hc else "A - ABSENT"
            elif stat == "Late":
                bg_color = theme.get("cal_late_bg", "#FEF3C7")
                fg_color = theme.get("cal_late_fg", "#92400E")
                marker_text = "● Late [L]" if not is_hc else "L - LATE"
            else:
                bg_color = theme.get("cal_neutral_bg", "#F8FAFC") if is_weekend else cal_cell_bg
                fg_color = theme.get("cal_neutral_fg", "#94A3B8")
                marker_text = "Weekend" if is_weekend else "—"

            tile = ctk.CTkFrame(
                self.grid_container,
                corner_radius=8,
                border_width=1,
                border_color=cal_border if not is_hc else "#FFFF00",
                fg_color=bg_color
            )
            tile.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
            self.day_tiles.append(tile)

            # Top label: Day Number
            lbl_day = ctk.CTkLabel(
                tile,
                text=str(day),
                font=("SF Pro Display", 11, "bold"),
                text_color=theme.get("fg", "#0F172A"),
                anchor="nw"
            )
            lbl_day.pack(side=tk.TOP, fill=tk.X, padx=6, pady=(3, 0))

            # Bottom label: Status marker
            lbl_status = ctk.CTkLabel(
                tile,
                text=marker_text,
                font=("SF Pro Display", 9, "bold"),
                text_color=fg_color,
                anchor="s"
            )
            lbl_status.pack(side=tk.BOTTOM, fill=tk.X, padx=4, pady=(0, 4))

            col += 1
            if col > 6:
                col = 0
                row += 1

    def handle_export_pdf(self):
        if not self.selected_roll:
            messagebox.showinfo("Select Student", "Please select a student from the dropdown first.")
            return

        student = self.db.get_student(self.selected_roll)
        if not student:
            return

        student_info = {"roll_no": student[0], "name": student[1], "section": student[2]}
        stats = self.db.get_student_history(self.selected_roll)
        records = stats["records"]

        filename = f"report_card_{self.selected_roll}.pdf"
        filepath = filedialog.asksaveasfilename(
            title="Save Student Attendance Report Card (PDF)",
            initialfile=filename,
            defaultextension=".pdf",
            filetypes=[("PDF Documents", "*.pdf")]
        )
        if not filepath:
            return

        success = generate_student_report_card(student_info, stats, records, filepath)
        if success:
            if messagebox.askyesno("PDF Generated", f"Report card successfully saved to:\n{filepath}\n\nWould you like to open it now?"):
                try:
                    import subprocess
                    subprocess.run(["open", filepath], check=False)
                except Exception:
                    pass
        else:
            messagebox.showerror("Error", "Failed to generate PDF report card.")

    def apply_theme(self, theme_or_key="light", font_scale_or_cfg="normal"):
        theme = get_theme(theme_or_key)
        font_cfg = get_fonts(font_scale_or_cfg)
        self.current_theme = theme
        self.current_font_cfg = font_cfg

        card_bg = theme["card_bg"]
        card_border = theme["card_border"]
        fg = theme["fg"]

        self.lbl_title.configure(text_color=fg, font=font_cfg.get("page_title", font_cfg["header_bold"]))
        self.lbl_badge.configure(text_color=theme["fg_muted"], font=font_cfg.get("badge_font", font_cfg["title_bold"]))

        self.control_bar.configure(fg_color=card_bg, border_color=card_border)
        self.kpi_bar.configure(fg_color=card_bg, border_color=card_border)
        self.cal_card.configure(fg_color=card_bg, border_color=card_border)

        self.lbl_sel_student.configure(text_color=fg, font=font_cfg.get("form_label", font_cfg["body_bold"]))
        self.lbl_month_display.configure(text_color=fg, font=font_cfg.get("section_title", font_cfg["title_bold"]))

        pad_x = font_cfg["btn_pad_x"]
        pad_y = font_cfg["btn_pad_y"]

        for btn in [self.btn_prev_month, self.btn_next_month, self.btn_today_month]:
            btn.apply_style(
                bg=theme["btn_secondary_bg"],
                fg=theme["btn_secondary_fg"],
                font=font_cfg.get("btn_font", ("SF Pro Display", font_cfg["body"])),
                focus_ring=theme["focus_ring"],
                border_color=theme["btn_secondary_border"],
                padx=pad_x - 2,
                pady=pad_y - 2
            )

        self.btn_export_pdf.apply_style(
            bg=theme["btn_primary_bg"],
            fg=theme["btn_primary_fg"],
            font=font_cfg.get("btn_bold", ("SF Pro Display", font_cfg["body"], "bold")),
            focus_ring=theme["focus_ring"],
            padx=pad_x,
            pady=pad_y
        )

        for lbl in self.weekday_labels:
            lbl.configure(text_color=theme["fg_muted"], font=font_cfg.get("form_label", font_cfg["body_bold"]))

        self.refresh_calendar()

    def select_student(self, roll_no):
        """Programmatically select student by roll number and refresh the calendar view."""
        self.populate_students()
        for idx, text in enumerate(self.student_combo["values"]):
            if text.startswith(f"{roll_no} -"):
                self.student_combo.current(idx)
                self.selected_roll = roll_no
                self.refresh_calendar()
                break

    def update_role_permissions(self, role: str):
        """Feature 4: Update role permission context."""
        self.current_role = role
