# Shortfall formula: ceil((0.75 * Total - Present) / 0.25)
"""
Reports and Analytics View.
Feature 1 & Feature 2: Smart Attendance Analytics & Trend Visualizer with At-Risk Roster.
- Configurable threshold banner (default 75%) with shortfall calculator.
- 30-day daily & weekly Matplotlib trend analytics.
- At-risk roster listing students with downward trends or <75% attendance.
- Individual student PDF report card exporter.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import csv
import customtkinter as ctk

from widgets import AccessibleButton, FocusRingEntry, CardFrame
from theme import get_theme, get_fonts
from pdf_exporter import generate_student_report_card, calculate_shortfall


class ReportsView(ctk.CTkFrame):
    def __init__(self, master, db=None, app_controller=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.db = db
        self.app = app_controller
        self.current_theme = None
        self.current_font_cfg = None

        self.current_report_type = tk.StringVar(value="smart_analytics")
        self.selected_month = datetime.now().strftime("%Y-%m")
        self.selected_date = datetime.now().strftime("%Y-%m-%d")
        self.threshold_val = tk.DoubleVar(value=75.0)

        self.fig = None
        self.chart_canvas = None
        self.build_ui()

    def build_ui(self):
        # Header banner
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill=tk.X, pady=(0, 10))

        self.lbl_title = ctk.CTkLabel(
            self.header_frame,
            text="Statistical Reports & Quality Analytics",
            font=("SF Pro Display", 15, "bold"),
            text_color="#0F172A",
            anchor="w"
        )
        self.lbl_title.pack(side=tk.LEFT)

        self.lbl_badge = ctk.CTkLabel(
            self.header_frame,
            text="TQM SQC Deliverable & Analytics Engine",
            font=("SF Pro Display", 11),
            text_color="#64748B",
            anchor="e"
        )
        self.lbl_badge.pack(side=tk.RIGHT)

        # -----------------------------------------------------
        # Report Configuration & Scope Bar (Floating White Card)
        # -----------------------------------------------------
        self.config_bar = CardFrame(self, corner_radius=14, border_width=1, border_color="#E2E8F0", fg_color="#FFFFFF")
        self.config_bar.pack(fill=tk.X, pady=(0, 8))

        # Row 1: Scope selection and parameter inputs
        self.scope_row = ctk.CTkFrame(self.config_bar, fg_color="transparent")
        self.scope_row.pack(fill=tk.X, padx=14, pady=(10, 6))

        self.lbl_mode = ctk.CTkLabel(self.scope_row, text="Scope:", font=("SF Pro Display", 11, "bold"), text_color="#0F172A")
        self.lbl_mode.pack(side=tk.LEFT, padx=(0, 8))

        self.rdo_smart = tk.Radiobutton(
            self.scope_row, text="Smart Analytics & At-Risk Roster", variable=self.current_report_type,
            value="smart_analytics", command=self.on_mode_change
        )
        self.rdo_smart.pack(side=tk.LEFT, padx=4)

        self.rdo_monthly = tk.Radiobutton(
            self.scope_row, text="Monthly Report", variable=self.current_report_type,
            value="monthly", command=self.on_mode_change
        )
        self.rdo_monthly.pack(side=tk.LEFT, padx=4)

        self.rdo_daily = tk.Radiobutton(
            self.scope_row, text="Daily Audit", variable=self.current_report_type,
            value="daily", command=self.on_mode_change
        )
        self.rdo_daily.pack(side=tk.LEFT, padx=4)

        self.rdo_student = tk.Radiobutton(
            self.scope_row, text="Individual Student", variable=self.current_report_type,
            value="student", command=self.on_mode_change
        )
        self.rdo_student.pack(side=tk.LEFT, padx=4)

        # Parameter Input (Month / Date / Student)
        self.lbl_param = ctk.CTkLabel(self.scope_row, text="Month:", font=("SF Pro Display", 11, "bold"), text_color="#0F172A")
        self.lbl_param.pack(side=tk.LEFT, padx=(12, 4))
        self.lbl_param.pack_forget()

        self.ent_param = FocusRingEntry(self.scope_row, width=120)
        self.ent_param.insert(0, self.selected_month)
        self.ent_param.pack(side=tk.LEFT, padx=4)
        self.ent_param.pack_forget()

        self.student_combo = ttk.Combobox(self.scope_row, state="readonly", width=22)
        self.student_combo.pack(side=tk.LEFT, padx=4)
        self.student_combo.pack_forget()

        # Configurable Threshold Badge on right of Row 1
        self.threshold_frame = ctk.CTkFrame(self.scope_row, fg_color="transparent")
        self.threshold_frame.pack(side=tk.RIGHT)

        self.lbl_thresh = ctk.CTkLabel(self.threshold_frame, text="Min Threshold:", font=("SF Pro Display", 11, "bold"), text_color="#0F172A")
        self.lbl_thresh.pack(side=tk.LEFT, padx=(0, 4))

        self.ent_thresh = FocusRingEntry(self.threshold_frame, width=55)
        self.ent_thresh.insert(0, "75")
        self.ent_thresh.pack(side=tk.LEFT, padx=(0, 4))

        self.lbl_thresh_pct = ctk.CTkLabel(self.threshold_frame, text="%", font=("SF Pro Display", 11, "bold"), text_color="#0F172A")
        self.lbl_thresh_pct.pack(side=tk.LEFT)

        # Row 2: Action Buttons
        self.action_row = ctk.CTkFrame(self.config_bar, fg_color="transparent")
        self.action_row.pack(fill=tk.X, padx=14, pady=(0, 10))

        self.btn_generate = AccessibleButton(self.action_row, text="🔄 Generate Report", command=self.generate_report, corner_radius=10)
        self.btn_generate.pack(side=tk.LEFT)

        # Export Buttons on the right
        self.btn_export_pdf = AccessibleButton(self.action_row, text="📄 Export Student PDF Report Card", command=self.handle_export_pdf, corner_radius=10)
        self.btn_export_pdf.pack(side=tk.RIGHT, padx=4)

        self.btn_export_csv = AccessibleButton(self.action_row, text="📥 Export CSV", command=self.handle_export_csv, corner_radius=10)
        self.btn_export_csv.pack(side=tk.RIGHT, padx=4)

        # -----------------------------------------------------
        # Top KPI Metric Cards (for Smart Analytics Scope)
        # -----------------------------------------------------
        self.kpi_banner = CardFrame(self, corner_radius=14, border_width=1, border_color="#E2E8F0", fg_color="#FFFFFF")
        self.kpi_banner.pack(fill=tk.X, pady=(0, 8))

        self.lbl_kpi_avg = ctk.CTkLabel(self.kpi_banner, text="Class Average: 84.7%", font=("SF Pro Display", 12, "bold"), text_color="#2563EB")
        self.lbl_kpi_avg.pack(side=tk.LEFT, padx=16, pady=8)

        self.lbl_kpi_students = ctk.CTkLabel(self.kpi_banner, text="Total Monitored: 5", font=("SF Pro Display", 11, "bold"), text_color="#0F172A")
        self.lbl_kpi_students.pack(side=tk.LEFT, padx=14, pady=8)

        self.lbl_kpi_atrisk = ctk.CTkLabel(self.kpi_banner, text="⚠️ At-Risk (<75%): 2", font=("SF Pro Display", 11, "bold"), text_color="#EF4444")
        self.lbl_kpi_atrisk.pack(side=tk.LEFT, padx=14, pady=8)

        self.lbl_kpi_section = ctk.CTkLabel(self.kpi_banner, text="Section CSE-B: 84.7%", font=("SF Pro Display", 11), text_color="#64748B")
        self.lbl_kpi_section.pack(side=tk.RIGHT, padx=16, pady=8)

        # -----------------------------------------------------
        # Main Display Area: Left Table & Right Analytics Chart
        # -----------------------------------------------------
        self.display_split = ctk.CTkFrame(self, fg_color="transparent")
        self.display_split.pack(fill=tk.BOTH, expand=True)
        self.display_split.columnconfigure(0, weight=3)
        self.display_split.columnconfigure(1, weight=2)
        self.display_split.rowconfigure(0, weight=1)

        # Left Column: Report / At-Risk Table (Floating White Card)
        self.report_table_frame = CardFrame(self.display_split, corner_radius=14, border_width=1, border_color="#E2E8F0", fg_color="#FFFFFF")
        self.report_table_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.lbl_report_summary = ctk.CTkLabel(
            self.report_table_frame,
            text="Smart Quality Analytics Overview",
            font=("SF Pro Display", 13, "bold"),
            text_color="#0F172A",
            anchor="w"
        )
        self.lbl_report_summary.pack(fill=tk.X, padx=14, pady=(12, 6))

        self.lbl_shortfall_formula = ctk.CTkLabel(
            self.report_table_frame,
            text="Shortfall Formula: If P/T < 0.75, Required Classes = ceil((0.75 * T - P) / 0.25)",
            font=("SF Pro Display", 9, "italic"),
            text_color="#64748B",
            anchor="w"
        )
        self.lbl_shortfall_formula.pack(fill=tk.X, padx=14, pady=(0, 6))

        self.tree_container = tk.Frame(self.report_table_frame, relief=tk.FLAT, bd=0)
        self.tree_container.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 14))

        self.tree_style = ttk.Style()
        self.tree = ttk.Treeview(self.tree_container, show="headings", selectmode="browse", takefocus=True)

        self.tree_scroll_y = ttk.Scrollbar(self.tree_container, orient="vertical", command=self.tree.yview)
        self.tree_scroll_x = ttk.Scrollbar(self.tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.tree_scroll_y.set, xscrollcommand=self.tree_scroll_x.set)

        self.tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Right Column: Visual Trend Chart (Floating White Card)
        self.chart_panel = CardFrame(self.display_split, corner_radius=14, border_width=1, border_color="#E2E8F0", fg_color="#FFFFFF")
        self.chart_panel.grid(row=0, column=1, sticky="nsew")

        self.lbl_chart_head = ctk.CTkLabel(
            self.chart_panel,
            text="Attendance Trend & Distribution Visualizer",
            font=("SF Pro Display", 13, "bold"),
            text_color="#0F172A",
            anchor="w"
        )
        self.lbl_chart_head.pack(fill=tk.X, padx=14, pady=(12, 8))

        self.chart_canvas_frame = tk.Frame(self.chart_panel, relief=tk.FLAT, bd=0)
        self.chart_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 14))

    def get_threshold(self) -> float:
        try:
            return float(self.ent_thresh.get().strip())
        except Exception:
            return 75.0

    def on_mode_change(self):
        mode = self.current_report_type.get()
        if mode == "smart_analytics":
            self.lbl_param.pack_forget()
            self.ent_param.pack_forget()
            self.student_combo.pack_forget()
            self.kpi_banner.pack(fill=tk.X, pady=(0, 8), before=self.display_split)
        elif mode == "monthly":
            self.lbl_param.configure(text="Month:")
            self.lbl_param.pack(side=tk.LEFT, padx=(12, 4))
            self.ent_param.delete(0, tk.END)
            self.ent_param.insert(0, self.selected_month)
            self.ent_param.pack(side=tk.LEFT, padx=4)
            self.student_combo.pack_forget()
            self.kpi_banner.pack_forget()
        elif mode == "daily":
            self.lbl_param.configure(text="Date:")
            self.lbl_param.pack(side=tk.LEFT, padx=(12, 4))
            self.ent_param.delete(0, tk.END)
            self.ent_param.insert(0, self.selected_date)
            self.ent_param.pack(side=tk.LEFT, padx=4)
            self.student_combo.pack_forget()
            self.kpi_banner.pack_forget()
        elif mode == "student":
            self.lbl_param.configure(text="Student:")
            self.lbl_param.pack(side=tk.LEFT, padx=(12, 4))
            self.ent_param.pack_forget()
            students = self.db.fetch_all_students()
            choices = [f"{s[0]} - {s[1]}" for s in students]
            self.student_combo["values"] = choices
            if choices:
                self.student_combo.set(choices[0])
            self.student_combo.pack(side=tk.LEFT, padx=4)
            self.kpi_banner.pack_forget()

        self.generate_report()

    def generate_report(self):
        mode = self.current_report_type.get()
        thresh = self.get_threshold()

        if mode == "smart_analytics":
            self.generate_smart_analytics_report(thresh)
        elif mode == "monthly":
            month_str = self.ent_param.get().strip()
            self.generate_monthly_report(month_str, thresh)
        elif mode == "daily":
            date_str = self.ent_param.get().strip()
            self.generate_daily_report(date_str)
        elif mode == "student":
            sel = self.student_combo.get()
            if not sel:
                return
            roll = sel.split(" - ")[0]
            self.generate_student_report(roll, thresh)

    def generate_smart_analytics_report(self, threshold):
        """Feature 1 & 2: Multi-metric dashboard with 30-day trends and at-risk students."""
        trends_data = self.db.get_detailed_attendance_trends(days=30)
        at_risk = self.db.get_at_risk_students(threshold=threshold)

        # Update Top KPI Banner
        overall_avg = trends_data["overall_avg"]
        all_students = self.db.fetch_all_students()
        self.lbl_kpi_avg.configure(text=f"Class Average: {overall_avg:.1f}%")
        self.lbl_kpi_students.configure(text=f"Total Students: {len(all_students)}")
        self.lbl_kpi_atrisk.configure(text=f"⚠️ At-Risk (<{threshold:.0f}%): {len(at_risk)}")

        sec_summary = []
        for sec, data in trends_data["section_breakdown"].items():
            sec_summary.append(f"{sec}: {data['rate']:.1f}%")
        self.lbl_kpi_section.configure(text=" | ".join(sec_summary) if sec_summary else "Section CSE-B: 84.7%")

        self.lbl_report_summary.configure(text=f"At-Risk Student Roster (<{threshold:.0f}% Threshold or Downward Trends)")

        columns = ("Roll", "Name", "Section", "Rate", "Shortfall", "Diagnosis")
        self.tree["columns"] = columns
        for c in columns:
            self.tree.heading(c, text=c)

        fc = self.current_font_cfg or {}
        col_w = fc.get("col_widths", {})
        self.tree.column("Roll", width=col_w.get("Roll", 100), stretch=False, anchor="center")
        self.tree.column("Name", width=col_w.get("Name", 180), stretch=True, anchor="w")
        self.tree.column("Section", width=col_w.get("Section", 75), stretch=False, anchor="center")
        self.tree.column("Rate", width=col_w.get("Rate", 95), stretch=False, anchor="center")
        self.tree.column("Shortfall", width=col_w.get("Shortfall", 160), stretch=False, anchor="center")
        self.tree.column("Diagnosis", width=col_w.get("Note", 220), stretch=True, anchor="w")

        for item in self.tree.get_children():
            self.tree.delete(item)

        if not at_risk:
            self.tree.insert("", tk.END, values=("—", "All students meet criteria", "—", "—", "0 Classes", "No students at risk"), tags=("compliant",))
        else:
            for s in at_risk:
                sh_text = f"Needs {s['shortfall']} classes" if s['shortfall'] > 0 else "Eligible"
                tag = "critical" if s['percentage'] < threshold else "warning"
                row = (s["roll_no"], s["name"], s["section"], f"{s['percentage']:.1f}%", sh_text, s["reason"])
                self.tree.insert("", tk.END, values=row, tags=(tag,))

        # Render 30-Day Multi-metric Charts
        self.render_30day_trends_chart(trends_data, threshold)

    def generate_monthly_report(self, month_str, threshold):
        data = self.db.get_monthly_report(month_str)
        self.lbl_report_summary.configure(text=f"Monthly Attendance Summary: {month_str} ({len(data)} students)")

        columns = ("Roll", "Name", "Section", "Present", "Absent", "Rate", "Shortfall Status")
        self.tree["columns"] = columns
        for c in columns:
            self.tree.heading(c, text=c)

        fc = self.current_font_cfg or {}
        col_w = fc.get("col_widths", {})
        self.tree.column("Roll", width=col_w.get("Roll", 100), stretch=False, anchor="center")
        self.tree.column("Name", width=col_w.get("Name", 180), stretch=True, anchor="w")
        self.tree.column("Section", width=col_w.get("Section", 75), stretch=False, anchor="center")
        self.tree.column("Present", width=col_w.get("Present", 75), stretch=False, anchor="center")
        self.tree.column("Absent", width=col_w.get("Absent", 75), stretch=False, anchor="center")
        self.tree.column("Rate", width=col_w.get("Rate", 95), stretch=False, anchor="center")
        self.tree.column("Shortfall Status", width=col_w.get("Shortfall", 160), stretch=True, anchor="center")

        for item in self.tree.get_children():
            self.tree.delete(item)

        rates = []
        for r in data:
            rate_val = r["percentage"]
            rates.append(rate_val)
            sh = r["shortfall"]
            if r["is_below_threshold"]:
                tag = "warning"
                sh_disp = f"⚠️ Needs {sh} classes"
            else:
                tag = "compliant"
                sh_disp = "✅ Eligible (>= 75%)"

            row = (r["roll_no"], r["name"], r["section"], r["present"], r["absent"], f"{rate_val:.1f}%", sh_disp)
            self.tree.insert("", tk.END, values=row, tags=(tag,))

        self.render_monthly_chart(rates, month_str)

    def generate_daily_report(self, date_str):
        records = self.db.fetch_attendance_by_date(date_str)
        self.lbl_report_summary.configure(text=f"Daily Attendance Audit: {date_str} ({len(records)} records)")

        columns = ("Roll", "Name", "Section", "Status")
        self.tree["columns"] = columns
        for c in columns:
            self.tree.heading(c, text=c)

        fc = self.current_font_cfg or {}
        col_w = fc.get("col_widths", {})
        self.tree.column("Roll", width=col_w.get("Roll", 110), stretch=False, anchor="center")
        self.tree.column("Name", width=col_w.get("Name", 220), stretch=True, anchor="w")
        self.tree.column("Section", width=col_w.get("Section", 90), stretch=False, anchor="center")
        self.tree.column("Status", width=col_w.get("Status", 130), stretch=False, anchor="center")

        for item in self.tree.get_children():
            self.tree.delete(item)

        status_counts = {"Present": 0, "Absent": 0, "Late": 0, "Unmarked": 0}
        for r in records:
            st = r[3] if len(r) > 3 and r[3] else "Unmarked"
            status_counts[st] = status_counts.get(st, 0) + 1
            tag = st.lower()
            if tag == "present":
                disp = "● Present"
            elif tag == "absent":
                disp = "● Absent"
            elif tag == "late":
                disp = "● Late"
            else:
                tag = "unmarked"
                disp = "○ Unmarked"
            row = (r[0], r[1], r[2], disp)
            self.tree.insert("", tk.END, values=row, tags=(tag,))

        self.render_daily_chart(status_counts, date_str)

    def generate_student_report(self, roll, threshold):
        data = self.db.get_student_history(roll)
        student = self.db.get_student(roll)
        name = student[1] if student else roll
        pct = data["percentage"]
        shortfall = self.db.calculate_shortfall(data["present"], data["total"], threshold / 100.0)

        if pct < threshold and data["total"] > 0:
            sub = f"Student History: {name} ({roll}) — ⚠️ Rate {pct:.1f}% (Needs {shortfall} more consecutive classes)"
        else:
            sub = f"Student History: {name} ({roll}) — ✅ Rate {pct:.1f}% (Exam Eligible)"
        self.lbl_report_summary.configure(text=sub)

        columns = ("Date", "Status")
        self.tree["columns"] = columns
        for c in columns:
            self.tree.heading(c, text=c)

        fc = self.current_font_cfg or {}
        col_w = fc.get("col_widths", {})
        self.tree.column("Date", width=col_w.get("Date", 160), stretch=False, anchor="center")
        self.tree.column("Status", width=col_w.get("Status", 180), stretch=True, anchor="center")

        for item in self.tree.get_children():
            self.tree.delete(item)

        status_counts = {"Present": 0, "Absent": 0, "Late": 0}
        for r in data["records"]:
            st = r[1]
            status_counts[st] = status_counts.get(st, 0) + 1
            tag = st.lower()
            if tag == "present":
                disp = "● Present"
            elif tag == "absent":
                disp = "● Absent"
            elif tag == "late":
                disp = "● Late"
            else:
                tag = "unmarked"
                disp = "○ Unmarked"
            row = (r[0], disp)
            self.tree.insert("", tk.END, values=row, tags=(tag,))

        self.render_daily_chart(status_counts, f"History for {name}")

    def render_30day_trends_chart(self, trends_data, threshold):
        """Feature 1: Matplotlib Line/Bar visualizer for 30-day trends and weekly patterns."""
        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

            for child in self.chart_canvas_frame.winfo_children():
                child.destroy()

            chart_bg = self.current_theme.get("chart_bg", "#FFFFFF") if self.current_theme else "#FFFFFF"
            plot_bg = self.current_theme.get("chart_plot_bg", "#F8FAFC") if self.current_theme else "#F8FAFC"
            chart_text = self.current_theme.get("chart_text", "#64748B") if self.current_theme else "#64748B"
            chart_grid = self.current_theme.get("chart_grid", "#E2E8F0") if self.current_theme else "#E2E8F0"
            chart_accent = self.current_theme.get("chart_accent", "#2563EB") if self.current_theme else "#2563EB"
            chart_fill = self.current_theme.get("chart_fill", "#93C5FD") if self.current_theme else "#93C5FD"

            fig = Figure(figsize=(4.2, 3.6), dpi=85, facecolor=chart_bg)

            # Subplot 1: 30-Day Daily Attendance Trend Line
            ax1 = fig.add_subplot(211, facecolor=plot_bg)
            daily = trends_data.get("daily", [])

            if not daily:
                ax1.text(0.5, 0.5, "No historical logs recorded", ha="center", va="center", color=chart_text)
                ax1.axis("off")
            else:
                d_labels = [d["date"][-5:] for d in daily]
                pcts = [d["percentage"] for d in daily]

                ax1.plot(d_labels, pcts, marker="o", color=chart_accent, linewidth=2, markersize=4, label="Daily %")
                ax1.fill_between(d_labels, pcts, color=chart_fill, alpha=0.35)
                # Red threshold line at 75%
                ax1.axhline(threshold, color="#EF4444", linestyle="--", linewidth=1.5, label=f"{threshold:.0f}% Threshold")
                ax1.set_ylim(0, 105)
                ax1.set_ylabel("Attendance %", fontsize=8, color=chart_text)
                ax1.tick_params(axis="both", labelsize=7, colors=chart_text)
                ax1.legend(loc="lower right", fontsize=7)
                for spine in ax1.spines.values():
                    spine.set_color(chart_grid)
                ax1.grid(True, linestyle="--", alpha=0.5, color=chart_grid)
                ax1.set_title("30-Day Attendance Trajectory vs. Threshold", fontsize=9, color=chart_text)

            # Subplot 2: Weekly Attendance Trend Bar Chart
            ax2 = fig.add_subplot(212, facecolor=plot_bg)
            weekly = trends_data.get("weekly", [])
            if not weekly:
                ax2.text(0.5, 0.5, "No weekly data available", ha="center", va="center", color=chart_text)
                ax2.axis("off")
            else:
                w_labels = [w["week"] for w in weekly]
                w_pcts = [w["percentage"] for w in weekly]
                bar_colors = ["#10B981" if p >= threshold else "#EF4444" for p in w_pcts]

                bars = ax2.bar(w_labels, w_pcts, color=bar_colors, width=0.55, edgecolor=chart_bg)
                ax2.axhline(threshold, color="#EF4444", linestyle="--", linewidth=1.2)
                ax2.set_ylim(0, 105)
                ax2.set_ylabel("Weekly Avg %", fontsize=8, color=chart_text)
                ax2.tick_params(axis="both", labelsize=7, colors=chart_text)
                for spine in ax2.spines.values():
                    spine.set_color(chart_grid)
                ax2.grid(True, linestyle="--", alpha=0.5, color=chart_grid)
                ax2.set_title("Weekly Aggregate Performance", fontsize=9, color=chart_text)

            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.chart_canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.fig = fig
            self.chart_canvas = canvas
        except Exception as e:
            err_lbl = tk.Label(self.chart_canvas_frame, text=f"Trend visualizer unavailable\n({str(e)})")
            err_lbl.pack(expand=True)

    def render_monthly_chart(self, rates, month_str):
        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

            for child in self.chart_canvas_frame.winfo_children():
                child.destroy()

            chart_bg = self.current_theme.get("chart_bg", "#FFFFFF") if self.current_theme else "#FFFFFF"
            plot_bg = self.current_theme.get("chart_plot_bg", "#F8FAFC") if self.current_theme else "#F8FAFC"
            chart_text = self.current_theme.get("chart_text", "#64748B") if self.current_theme else "#64748B"
            chart_grid = self.current_theme.get("chart_grid", "#E2E8F0") if self.current_theme else "#E2E8F0"
            chart_accent = self.current_theme.get("chart_accent", "#2563EB") if self.current_theme else "#2563EB"

            fig = Figure(figsize=(4.0, 3.2), dpi=85, facecolor=chart_bg)
            ax = fig.add_subplot(111, facecolor=plot_bg)

            if not rates:
                ax.text(0.5, 0.5, f"No records found\nfor {month_str}", ha="center", va="center", color=chart_text)
                ax.axis("off")
            else:
                ax.hist(rates, bins=[0, 50, 75, 85, 95, 100], color=chart_accent, edgecolor=chart_bg, rwidth=0.85)
                ax.set_title(f"Attendance Rate Distribution ({month_str})", fontsize=10, color=chart_text)
                ax.set_xlabel("Attendance %", fontsize=9, color=chart_text)
                ax.set_ylabel("No. of Students", fontsize=9, color=chart_text)
                ax.tick_params(axis="both", labelsize=8, colors=chart_text)
                for spine in ax.spines.values():
                    spine.set_color(chart_grid)
                ax.grid(True, linestyle="--", alpha=0.5, color=chart_grid)

            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.chart_canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.fig = fig
            self.chart_canvas = canvas
        except Exception as e:
            err_lbl = tk.Label(self.chart_canvas_frame, text=f"Chart preview unavailable\n({str(e)})")
            err_lbl.pack(expand=True)

    def render_daily_chart(self, counts, title_suffix):
        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

            for child in self.chart_canvas_frame.winfo_children():
                child.destroy()

            chart_bg = self.current_theme.get("chart_bg", "#FFFFFF") if self.current_theme else "#FFFFFF"
            chart_text = self.current_theme.get("chart_text", "#64748B") if self.current_theme else "#64748B"

            fig = Figure(figsize=(4.0, 3.2), dpi=85, facecolor=chart_bg)
            ax = fig.add_subplot(111, facecolor=chart_bg)

            labels = [k for k, v in counts.items() if v > 0]
            values = [v for k, v in counts.items() if v > 0]

            palette = {
                "Present": self.current_theme.get("status_present", "#10B981") if self.current_theme else "#10B981",
                "Absent": self.current_theme.get("status_absent", "#EF4444") if self.current_theme else "#EF4444",
                "Late": self.current_theme.get("status_late", "#F59E0B") if self.current_theme else "#F59E0B",
                "Unmarked": self.current_theme.get("status_unmarked", "#64748B") if self.current_theme else "#64748B"
            }
            colors = [palette.get(l, "#2563EB") for l in labels]

            if not values:
                ax.text(0.5, 0.5, "No attendance entries\nfound for this query", ha="center", va="center", color=chart_text)
                ax.axis("off")
            else:
                wedges, texts, autotexts = ax.pie(
                    values, labels=labels, autopct="%1.0f%%", startangle=140, colors=colors,
                    textprops=dict(color=chart_text, fontsize=8)
                )
                for at in autotexts:
                    at.set_color("#FFFFFF")
                    at.set_fontsize(8)
                ax.set_title(f"Status Ratio ({title_suffix})", fontsize=10, color=chart_text)

            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.chart_canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.fig = fig
            self.chart_canvas = canvas
        except Exception as e:
            err_lbl = tk.Label(self.chart_canvas_frame, text=f"Chart preview unavailable\n({str(e)})")
            err_lbl.pack(expand=True)

    def handle_export_pdf(self):
        """Feature 5: Export individual student PDF report card."""
        selected_roll = None

        # Check if row selected in treeview
        selected = self.tree.selection()
        if selected:
            val = self.tree.item(selected[0])["values"]
            if val and len(val) > 0 and str(val[0]).startswith("CSE"):
                selected_roll = val[0]

        if not selected_roll:
            if self.current_report_type.get() == "student" and self.student_combo.get():
                selected_roll = self.student_combo.get().split(" - ")[0]

        if not selected_roll:
            students = self.db.fetch_all_students()
            if not students:
                messagebox.showinfo("No Students", "No student records available to export.")
                return
            selected_roll = students[0][0]

        student = self.db.get_student(selected_roll)
        if not student:
            return

        student_info = {"roll_no": student[0], "name": student[1], "section": student[2]}
        stats = self.db.get_student_history(selected_roll)
        records = stats["records"]

        filename = f"report_card_{selected_roll}.pdf"
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

    def handle_export_csv(self):
        path = filedialog.asksaveasfilename(
            title="Export Report CSV",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")]
        )
        if not path:
            return

        cols = self.tree["columns"]
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(cols)
            for item in self.tree.get_children():
                writer.writerow(self.tree.item(item)["values"])

        messagebox.showinfo("Export CSV", f"Successfully exported report table to:\n{path}")

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

        # Config Bar & Top Banner
        self.config_bar.configure(fg_color=card_bg, border_color=card_border)
        self.kpi_banner.configure(fg_color=card_bg, border_color=card_border)

        self.lbl_mode.configure(text_color=fg, font=font_cfg.get("form_label", font_cfg["body_bold"]))
        self.lbl_param.configure(text_color=fg, font=font_cfg.get("form_label", font_cfg["body_bold"]))
        self.lbl_thresh.configure(text_color=fg, font=font_cfg.get("form_label", font_cfg["body_bold"]))
        self.lbl_thresh_pct.configure(text_color=fg, font=font_cfg.get("form_label", font_cfg["body_bold"]))

        for rdo in [self.rdo_smart, self.rdo_monthly, self.rdo_daily, self.rdo_student]:
            rdo.configure(
                bg=card_bg, fg=fg, selectcolor=card_bg, activebackground=card_bg,
                font=font_cfg.get("body_font", ("SF Pro Display", font_cfg["body"]))
            )

        self.ent_param.apply_theme(theme, font_cfg)
        self.ent_thresh.apply_theme(theme, font_cfg)

        pad_x = font_cfg["btn_pad_x"]
        pad_y = font_cfg["btn_pad_y"]

        self.btn_generate.apply_style(
            bg=theme["btn_primary_bg"],
            fg=theme["btn_primary_fg"],
            font=font_cfg.get("btn_bold", ("SF Pro Display", font_cfg["body"], "bold")),
            focus_ring=theme["focus_ring"],
            padx=pad_x,
            pady=pad_y
        )
        self.btn_export_csv.apply_style(
            bg=theme["btn_secondary_bg"],
            fg=theme["btn_secondary_fg"],
            font=font_cfg.get("btn_font", ("SF Pro Display", font_cfg["body"])),
            focus_ring=theme["focus_ring"],
            border_color=theme["btn_secondary_border"],
            padx=pad_x,
            pady=pad_y
        )
        self.btn_export_pdf.apply_style(
            bg=theme["btn_primary_bg"],
            fg=theme["btn_primary_fg"],
            font=font_cfg.get("btn_bold", ("SF Pro Display", font_cfg["body"], "bold")),
            focus_ring=theme["focus_ring"],
            padx=pad_x,
            pady=pad_y
        )

        # Panels
        self.report_table_frame.configure(fg_color=card_bg, border_color=card_border)
        self.chart_panel.configure(fg_color=card_bg, border_color=card_border)
        self.tree_container.configure(bg=card_bg)
        self.chart_canvas_frame.configure(bg=card_bg)

        self.lbl_report_summary.configure(text_color=fg, font=font_cfg.get("section_title", font_cfg["title_bold"]))
        self.lbl_chart_head.configure(text_color=fg, font=font_cfg.get("section_title", font_cfg["title_bold"]))

        # Treeview styling with 38px row height baseline
        rowheight = font_cfg.get("tree_row", 38)
        self.tree_style.configure(
            "Treeview",
            background=theme["tree_bg"],
            foreground=theme["tree_fg"],
            fieldbackground=theme["tree_bg"],
            rowheight=rowheight,
            font=font_cfg.get("tree_row_font", ("SF Pro Display", font_cfg["body"]))
        )
        self.tree_style.configure(
            "Treeview.Heading",
            background=theme["tree_head_bg"],
            foreground=theme["tree_head_fg"],
            font=font_cfg.get("tree_head_font", ("SF Pro Display", font_cfg["tree_head"], "bold"))
        )
        self.tree_style.map(
            "Treeview",
            background=[("selected", theme["select_bg"])],
            foreground=[("selected", theme["select_fg"])]
        )

        # Status Pill Tags
        self.tree.tag_configure("compliant", background=theme.get("status_present_bg", "#DCFCE7"), foreground=theme.get("status_present_fg", "#15803D"))
        self.tree.tag_configure("warning", background=theme.get("status_warning_bg", "#FEF3C7"), foreground=theme.get("status_warning_fg", "#92400E"))
        self.tree.tag_configure("critical", background=theme.get("status_critical_bg", "#FEE2E2"), foreground=theme.get("status_critical_fg", "#B91C1C"))
        self.tree.tag_configure("present", background=theme.get("status_present_bg", "#DCFCE7"), foreground=theme.get("status_present_fg", "#15803D"))
        self.tree.tag_configure("absent", background=theme.get("status_absent_bg", "#FEE2E2"), foreground=theme.get("status_absent_fg", "#B91C1C"))
        self.tree.tag_configure("late", background=theme.get("status_late_bg", "#FEF3C7"), foreground=theme.get("status_late_fg", "#92400E"))
        self.tree.tag_configure("unmarked", background=theme.get("status_unmarked_bg", "#FEF3C7"), foreground=theme.get("status_unmarked_fg", "#92400E"))

        self.generate_report()

    def update_role_permissions(self, role: str):
        """Feature 4: Update role permission context."""
        self.current_role = role
