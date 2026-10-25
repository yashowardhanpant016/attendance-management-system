"""
Dashboard View for Attendance Management System.
EduAttend / CampusEdge modern white-card SaaS educational ERP aesthetic.
Features:
  - 4 Modern Top KPI Metric Cards (Total Enrolled, Present Today, Absent Today, Attendance Rate)
  - Embedded Attendance Trend Chart Preview
  - Today's Roster Table with Soft Pill Status Badges (38px row height)
  - Quick action pill buttons
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import customtkinter as ctk

from widgets import AccessibleButton, KPICard, CardFrame
from theme import get_theme, get_fonts


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, db=None, navigate_callback=None, app_controller=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.db = db
        nav = navigate_callback or app_controller
        if hasattr(nav, "switch_view"):
            self.navigate = nav.switch_view
        elif callable(nav):
            self.navigate = nav
        else:
            self.navigate = lambda *args: None
        self.current_date = datetime.now().strftime("%Y-%m-%d")

        self.fig = None
        self.chart_canvas = None
        self.current_theme = None
        self.current_font_cfg = None

        self.build_ui()

    def build_ui(self):
        # Header banner inside dashboard
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill=tk.X, pady=(0, 12))

        self.lbl_welcome = ctk.CTkLabel(
            self.header_frame,
            text="System Overview & Operations Dashboard",
            font=("SF Pro Display", 15, "bold"),
            text_color="#0F172A",
            anchor="w"
        )
        self.lbl_welcome.pack(side=tk.LEFT)

        self.lbl_date_badge = ctk.CTkLabel(
            self.header_frame,
            text=f"Today: {self.current_date}",
            font=("SF Pro Display", 12),
            text_color="#64748B",
            anchor="e"
        )
        self.lbl_date_badge.pack(side=tk.RIGHT)

        # -----------------------------------------------------
        # 1. Metric KPI Cards (Top Row: 4 Separate Modern Cards)
        # Total Enrolled (Blue), Present Today (Emerald),
        # Absent Today (Rose), Attendance Rate (Amber)
        # -----------------------------------------------------
        self.kpi_container = ctk.CTkFrame(self, fg_color="transparent")
        self.kpi_container.pack(fill=tk.X, pady=(0, 14))

        for col in range(4):
            self.kpi_container.columnconfigure(col, weight=1)

        self.card_total = KPICard(
            self.kpi_container,
            title="Total Enrolled",
            value="0",
            accent_color="#2563EB",
            value_color="#60A5FA"
        )
        self.card_total.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.card_present = KPICard(
            self.kpi_container,
            title="Present Today",
            value="0",
            accent_color="#10B981",
            value_color="#34D399"
        )
        self.card_present.grid(row=0, column=1, sticky="ew", padx=6)

        self.card_absent = KPICard(
            self.kpi_container,
            title="Absent Today",
            value="0",
            accent_color="#EF4444",
            value_color="#F87171"
        )
        self.card_absent.grid(row=0, column=2, sticky="ew", padx=6)

        self.card_rate = KPICard(
            self.kpi_container,
            title="Attendance Rate",
            value="0.0%",
            accent_color="#F59E0B",
            value_color="#FBBF24"
        )
        self.card_rate.grid(row=0, column=3, sticky="ew", padx=(6, 0))

        # -----------------------------------------------------
        # 2. Main Split Area: Left Roster Preview & Right Chart Preview
        # -----------------------------------------------------
        self.split_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.split_frame.pack(fill=tk.BOTH, expand=True)
        self.split_frame.columnconfigure(0, weight=3)
        self.split_frame.columnconfigure(1, weight=2)
        self.split_frame.rowconfigure(0, weight=1)

        # Left Column: Today's Marked Roster Table (Floating White Card)
        self.left_col = CardFrame(self.split_frame, corner_radius=14, border_width=1, border_color="#E2E8F0", fg_color="#FFFFFF")
        self.left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.lbl_table_head = ctk.CTkLabel(
            self.left_col,
            text="Today's Attendance Roster",
            font=("SF Pro Display", 13, "bold"),
            text_color="#0F172A",
            anchor="w"
        )
        self.lbl_table_head.pack(fill=tk.X, padx=14, pady=(12, 8))

        self.tree_container = tk.Frame(self.left_col, relief=tk.FLAT, bd=0)
        self.tree_container.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 12))

        self.tree_style = ttk.Style()
        self.tree = ttk.Treeview(
            self.tree_container,
            columns=("Roll", "Name", "Section", "Status"),
            show="headings",
            selectmode="browse",
            takefocus=True
        )
        self.tree.heading("Roll", text="Roll No.")
        self.tree.heading("Name", text="Student Name")
        self.tree.heading("Section", text="Section")
        self.tree.heading("Status", text="Status")

        self.tree.column("Roll", width=95, minwidth=75, stretch=False, anchor="center")
        self.tree.column("Name", width=180, minwidth=140, stretch=True, anchor="w")
        self.tree.column("Section", width=75, minwidth=65, stretch=False, anchor="center")
        self.tree.column("Status", width=110, minwidth=90, stretch=False, anchor="center")

        self.tree_scroll_y = ttk.Scrollbar(self.tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scroll_y.set)

        self.tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Right Column: Chart & Quick Actions (Floating White Card)
        self.right_col = CardFrame(self.split_frame, corner_radius=14, border_width=1, border_color="#E2E8F0", fg_color="#FFFFFF")
        self.right_col.grid(row=0, column=1, sticky="nsew")

        self.lbl_chart_head = ctk.CTkLabel(
            self.right_col,
            text="Recent Attendance Trend",
            font=("SF Pro Display", 13, "bold"),
            text_color="#0F172A",
            anchor="w"
        )
        self.lbl_chart_head.pack(fill=tk.X, padx=14, pady=(12, 8))

        self.chart_frame = tk.Frame(self.right_col, relief=tk.FLAT, bd=0)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 10))

        # Quick Actions Section
        self.lbl_actions = ctk.CTkLabel(
            self.right_col,
            text="Quick Shortcuts & Operations",
            font=("SF Pro Display", 11, "bold"),
            text_color="#64748B",
            anchor="w"
        )
        self.lbl_actions.pack(fill=tk.X, padx=14, pady=(0, 6))

        self.btn_goto_att = AccessibleButton(
            self.right_col,
            text="📋 Open Daily Attendance Sheet",
            command=lambda: self.navigate("attendance"),
            corner_radius=10
        )
        self.btn_goto_att.pack(fill=tk.X, padx=14, pady=3)

        self.btn_goto_stu = AccessibleButton(
            self.right_col,
            text="👥 Register / Manage Students",
            command=lambda: self.navigate("students"),
            corner_radius=10
        )
        self.btn_goto_stu.pack(fill=tk.X, padx=14, pady=3)

        self.btn_goto_rep = AccessibleButton(
            self.right_col,
            text="📈 View Full Reports & Analytics",
            command=lambda: self.navigate("reports"),
            corner_radius=10
        )
        self.btn_goto_rep.pack(fill=tk.X, padx=14, pady=(3, 14))

    def refresh_data(self):
        """Fetches fresh data from DB, updates KPI cards, table, and trend chart."""
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.lbl_date_badge.configure(text=f"Today: {self.current_date}")

        # Update 4 Modern KPI Cards
        stats = self.db.get_dashboard_stats(self.current_date)
        self.card_total.update_value(stats["total"])
        self.card_present.update_value(stats["present"])
        self.card_absent.update_value(stats["absent"])
        self.card_rate.update_value(f"{stats['percentage']}%")

        # Update Roster Table with Soft Pill Badges
        for item in self.tree.get_children():
            self.tree.delete(item)

        records = self.db.fetch_attendance_by_date(self.current_date)
        for r in records:
            raw_status = str(r[3]).strip() if len(r) > 3 and r[3] else "Unmarked"
            status_lower = raw_status.lower()

            if "present" in status_lower:
                tag = "present"
                display_status = "● Present"
            elif "absent" in status_lower:
                tag = "absent"
                display_status = "● Absent"
            elif "late" in status_lower:
                tag = "late"
                display_status = "● Late"
            else:
                tag = "unmarked"
                display_status = "○ Unmarked"

            display_row = (r[0], r[1], r[2], display_status)
            self.tree.insert("", tk.END, values=display_row, tags=(tag,))

        # Update Chart Preview
        self.render_trend_chart()

    def render_trend_chart(self):
        """Renders embedded Matplotlib trend chart on the dashboard with sleek modern styling."""
        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

            trends = self.db.get_attendance_trends(limit_days=7)

            for child in self.chart_frame.winfo_children():
                child.destroy()

            # Dynamic theme colors
            is_hc = False
            card_bg = "#1E293B"
            if self.current_theme:
                is_hc = self.current_theme.get("is_high_contrast", False)
                card_bg = self.current_theme.get("card_bg", "#1E293B")

            # Determine colors - dark theme matches #1E293B
            fig_bg = card_bg
            ax_bg = card_bg
            line_color = "#FFFF00" if is_hc else "#06B6D4"
            fill_color = "#FFFF00" if is_hc else "#06B6D4"
            fill_alpha = 0.08 if is_hc else 0.18
            marker_face = "#000000" if is_hc else "#FFFFFF"
            marker_edge = "#FFFF00" if is_hc else "#0284C7"
            text_color = "#FFFF00" if is_hc else ("#F8FAFC" if card_bg in ["#1E293B", "#000000"] else "#0F172A")
            grid_color = "#333333" if is_hc else ("#334155" if card_bg == "#1E293B" else "#E2E8F0")
            spine_color = "#FFFF00" if is_hc else ("#475569" if card_bg == "#1E293B" else "#CBD5E1")

            fig = Figure(figsize=(4.2, 2.4), dpi=90, facecolor=fig_bg)
            fig.patch.set_facecolor(fig_bg)
            ax = fig.add_subplot(111, facecolor=ax_bg)
            ax.set_facecolor(ax_bg)

            if not trends:
                ax.text(0.5, 0.5, "No historical logs yet.\nMark attendance to view trends.",
                        ha="center", va="center", color=text_color, fontsize=10, weight="bold")
                ax.axis("off")
            else:
                dates = [t["date"][-5:] for t in trends]
                pcts = [t["percentage"] for t in trends]

                ax.plot(
                    dates,
                    pcts,
                    marker="o",
                    color=line_color,
                    linewidth=2.8,
                    markersize=7,
                    markerfacecolor=marker_face,
                    markeredgecolor=marker_edge,
                    markeredgewidth=2
                )
                ax.fill_between(dates, pcts, color=fill_color, alpha=fill_alpha)
                ax.set_ylim(0, 105)
                ax.set_ylabel("Attendance %", fontsize=10, fontweight="bold", color=text_color)
                ax.set_xlabel("Dates", fontsize=10, fontweight="bold", color=text_color, labelpad=4)
                ax.tick_params(axis="both", labelsize=10, colors=text_color)
                for label in ax.get_xticklabels() + ax.get_yticklabels():
                    label.set_color(text_color)
                    label.set_fontweight("bold")

                # Remove top and right spines, set bottom and left spine colors
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)
                ax.spines["bottom"].set_color(spine_color)
                ax.spines["left"].set_color(spine_color)
                ax.spines["bottom"].set_linewidth(1.2)
                ax.spines["left"].set_linewidth(1.2)

                # Subtle gridlines
                ax.grid(True, color=grid_color, linestyle="--", alpha=0.6)

            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.fig = fig
            self.chart_canvas = canvas
        except Exception as e:
            err_lbl = tk.Label(self.chart_frame, text=f"Trend Chart Preview\n({str(e)})")
            err_lbl.pack(expand=True)

    def apply_theme(self, theme_or_key="light", font_scale_or_cfg="normal"):
        theme = get_theme(theme_or_key)
        font_cfg = get_fonts(font_scale_or_cfg)
        self.current_theme = theme
        self.current_font_cfg = font_cfg

        card_bg = theme["card_bg"]
        card_border = theme["card_border"]
        fg = theme["fg"]

        self.lbl_welcome.configure(
            text_color=fg,
            font=font_cfg.get("page_title", font_cfg["header_bold"])
        )
        self.lbl_date_badge.configure(
            text_color=theme["fg_muted"],
            font=font_cfg.get("badge_font", font_cfg["title_bold"])
        )

        # 4 KPI Cards
        for card in [self.card_total, self.card_present, self.card_absent, self.card_rate]:
            card.apply_theme(theme, font_cfg)

        # Floating Cards
        self.left_col.configure(fg_color=card_bg, border_color=card_border)
        self.right_col.configure(fg_color=card_bg, border_color=card_border)
        self.tree_container.configure(bg=card_bg)
        self.chart_frame.configure(bg=card_bg)

        self.lbl_table_head.configure(text_color=fg, font=font_cfg.get("section_title", font_cfg["title_bold"]))
        self.lbl_chart_head.configure(text_color=fg, font=font_cfg.get("section_title", font_cfg["title_bold"]))
        self.lbl_actions.configure(text_color=theme["fg_muted"], font=font_cfg.get("form_label", font_cfg["body_bold"]))

        # Quick action buttons
        pad_x = font_cfg["btn_pad_x"]
        pad_y = font_cfg["btn_pad_y"]
        for btn in [self.btn_goto_att, self.btn_goto_stu, self.btn_goto_rep]:
            btn.apply_style(
                bg=theme["btn_secondary_bg"],
                fg=theme["btn_secondary_fg"],
                font=font_cfg.get("btn_bold", ("SF Pro Display", font_cfg["body"], "bold")),
                focus_ring=theme["focus_ring"],
                border_color=theme["btn_secondary_border"],
                padx=pad_x,
                pady=pad_y
            )

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
        # Modernize Treeview row selection with high-contrast text #FFFFFF on #2563EB
        self.tree_style.map(
            "Treeview",
            background=[("selected", "#2563EB")],
            foreground=[("selected", "#FFFFFF")]
        )

        col_specs = [
            ("Roll", 95, False, "center"),
            ("Name", 180, True, "w"),
            ("Section", 75, False, "center"),
            ("Status", 110, False, "center")
        ]
        for col, width, stretch, anchor in col_specs:
            self.tree.column(col, width=width, minwidth=max(50, width - 20), stretch=stretch, anchor=anchor)
            self.tree.heading(col, anchor=anchor)

        # Soft status pill badges:
        # Present: #DCFCE7 bg / #15803D text
        # Absent: #FEE2E2 bg / #B91C1C text
        # Late / Unmarked: #FEF3C7 bg / #92400E text
        self.tree.tag_configure(
            "present",
            background=theme.get("status_present_bg", "#DCFCE7"),
            foreground=theme.get("status_present_fg", "#15803D")
        )
        self.tree.tag_configure(
            "absent",
            background=theme.get("status_absent_bg", "#FEE2E2"),
            foreground=theme.get("status_absent_fg", "#B91C1C")
        )
        self.tree.tag_configure(
            "late",
            background=theme.get("status_late_bg", "#FEF3C7"),
            foreground=theme.get("status_late_fg", "#92400E")
        )
        self.tree.tag_configure(
            "unmarked",
            background=theme.get("status_unmarked_bg", "#FEF3C7"),
            foreground=theme.get("status_unmarked_fg", "#92400E")
        )

        # Re-render chart with new theme colors
        self.render_trend_chart()

    def update_role_permissions(self, role: str):
        """Feature 4: Update role permission context."""
        self.current_role = role

# Configuration: High-density rasterization parameters (macOS Retina Display)
DEFAULT_CHART_DPI = 110
