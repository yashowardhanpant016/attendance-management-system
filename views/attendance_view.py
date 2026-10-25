"""
Attendance Management View.
Matches EduAttend / CampusEdge modern white-card SaaS educational ERP aesthetic.
Features:
  - Date navigation bar inside floating white cards
  - Mini KPI metrics bar
  - Left single-touch action panel with rounded pill buttons
  - Right ledger table with 38px row height and soft status pill badges
  - Multi-level undo action history
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import customtkinter as ctk

from widgets import AccessibleButton, FocusRingEntry, CardFrame
from theme import get_theme, get_fonts


class AttendanceView(ctk.CTkFrame):
    def __init__(self, master, db=None, app_controller=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.db = db
        self.app = app_controller
        self.selected_date = datetime.now().strftime("%Y-%m-%d")
        self.undo_stack = []
        self.current_role = "Faculty"

        self.current_theme = None
        self.current_font_cfg = None

        self.build_ui()

    def build_ui(self):
        # Header banner
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill=tk.X, pady=(0, 10))

        self.lbl_title = ctk.CTkLabel(
            self.header_frame,
            text="Daily Attendance Logging & Verification",
            font=("SF Pro Display", 15, "bold"),
            text_color="#0F172A",
            anchor="w"
        )
        self.lbl_title.pack(side=tk.LEFT)

        self.lbl_badge = ctk.CTkLabel(
            self.header_frame,
            text="Single-Key Mark & Undo Enabled",
            font=("SF Pro Display", 11),
            text_color="#64748B",
            anchor="e"
        )
        self.lbl_badge.pack(side=tk.RIGHT)

        # -----------------------------------------------------
        # Date Navigation & Filter Control Bar (Floating White Card)
        # -----------------------------------------------------
        self.control_bar = CardFrame(self, corner_radius=14, border_width=1, border_color="#E2E8F0", fg_color="#FFFFFF")
        self.control_bar.pack(fill=tk.X, pady=(0, 8))

        # Left: Date Navigator controls
        self.ctrl_date_group = ctk.CTkFrame(self.control_bar, fg_color="transparent")
        self.ctrl_date_group.pack(side=tk.LEFT, padx=14, pady=8)

        self.lbl_date_tag = ctk.CTkLabel(self.ctrl_date_group, text="Logging Date:", font=("SF Pro Display", 11, "bold"), text_color="#0F172A")
        self.lbl_date_tag.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_prev_day = AccessibleButton(self.ctrl_date_group, text="◀ Prev", command=self.step_prev_day, corner_radius=8)
        self.btn_prev_day.pack(side=tk.LEFT, padx=(0, 4))

        self.ent_date = FocusRingEntry(self.ctrl_date_group, width=110)
        self.ent_date.insert(0, self.selected_date)
        self.ent_date.pack(side=tk.LEFT, padx=4)
        self.ent_date.bind("<Return>", lambda e: self.apply_custom_date())

        self.btn_next_day = AccessibleButton(self.ctrl_date_group, text="Next ▶", command=self.step_next_day, corner_radius=8)
        self.btn_next_day.pack(side=tk.LEFT, padx=4)

        self.btn_today = AccessibleButton(self.ctrl_date_group, text="Today", command=self.set_today, corner_radius=8)
        self.btn_today.pack(side=tk.LEFT, padx=(4, 12))

        # Right: Filter & Search controls
        self.ctrl_filter_group = ctk.CTkFrame(self.control_bar, fg_color="transparent")
        self.ctrl_filter_group.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=14, pady=8)

        self.search_box = FocusRingEntry(self.ctrl_filter_group)
        self.search_box.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 0))
        self.search_box.bind("<KeyRelease>", lambda e: self.refresh_table())

        self.lbl_search = ctk.CTkLabel(self.ctrl_filter_group, text="Filter:", font=("SF Pro Display", 11, "bold"), text_color="#0F172A")
        self.lbl_search.pack(side=tk.RIGHT, padx=(8, 4))

        self.sec_combo = ttk.Combobox(self.ctrl_filter_group, values=["ALL"], state="readonly", width=8)
        self.sec_combo.set("ALL")
        self.sec_combo.pack(side=tk.RIGHT, padx=(4, 8))
        self.sec_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())

        self.lbl_sec = ctk.CTkLabel(self.ctrl_filter_group, text="Section:", font=("SF Pro Display", 11, "bold"), text_color="#0F172A")
        self.lbl_sec.pack(side=tk.RIGHT, padx=(0, 4))

        # -----------------------------------------------------
        # Mini-KPI Metrics Row for Selected Date (Floating White Card)
        # -----------------------------------------------------
        self.kpi_bar = CardFrame(self, corner_radius=14, border_width=1, border_color="#E2E8F0", fg_color="#FFFFFF")
        self.kpi_bar.pack(fill=tk.X, pady=(0, 10))

        self.lbl_stat_present = ctk.CTkLabel(self.kpi_bar, text="Present: 0", font=("SF Pro Display", 11, "bold"), text_color="#10B981")
        self.lbl_stat_present.pack(side=tk.LEFT, padx=14, pady=8)

        self.lbl_stat_absent = ctk.CTkLabel(self.kpi_bar, text="Absent: 0", font=("SF Pro Display", 11, "bold"), text_color="#EF4444")
        self.lbl_stat_absent.pack(side=tk.LEFT, padx=14, pady=8)

        self.lbl_stat_late = ctk.CTkLabel(self.kpi_bar, text="Late: 0", font=("SF Pro Display", 11, "bold"), text_color="#F59E0B")
        self.lbl_stat_late.pack(side=tk.LEFT, padx=14, pady=8)

        self.lbl_stat_unmarked = ctk.CTkLabel(self.kpi_bar, text="Unmarked: 0", font=("SF Pro Display", 11, "bold"), text_color="#64748B")
        self.lbl_stat_unmarked.pack(side=tk.LEFT, padx=14, pady=8)

        self.lbl_stat_rate = ctk.CTkLabel(self.kpi_bar, text="Attendance Rate: 0.0%", font=("SF Pro Display", 12, "bold"), text_color="#2563EB")
        self.lbl_stat_rate.pack(side=tk.RIGHT, padx=14, pady=8)

        # -----------------------------------------------------
        # Main Split Workspace: Left Actions, Right Table
        # -----------------------------------------------------
        self.workspace = ctk.CTkFrame(self, fg_color="transparent")
        self.workspace.pack(fill=tk.BOTH, expand=True)
        self.workspace.columnconfigure(0, weight=0, minsize=270)
        self.workspace.columnconfigure(1, weight=1)
        self.workspace.rowconfigure(0, weight=1)

        # Left Action Panel (Floating White Card)
        self.action_panel = CardFrame(self.workspace, corner_radius=14, border_width=1, border_color="#E2E8F0", fg_color="#FFFFFF")
        self.action_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.lbl_act_head = ctk.CTkLabel(
            self.action_panel,
            text="Mark Selected Student",
            font=("SF Pro Display", 13, "bold"),
            text_color="#0F172A",
            anchor="w"
        )
        self.lbl_act_head.pack(fill=tk.X, padx=14, pady=(12, 8))

        self.btn_mark_p = AccessibleButton(
            self.action_panel,
            text="✅ Mark Present [Ctrl+M / Enter]",
            command=lambda: self.handle_mark("Present"),
            corner_radius=10
        )
        self.btn_mark_p.pack(fill=tk.X, padx=14, pady=3)

        self.btn_mark_a = AccessibleButton(
            self.action_panel,
            text="❌ Mark Absent [Space]",
            command=lambda: self.handle_mark("Absent"),
            corner_radius=10
        )
        self.btn_mark_a.pack(fill=tk.X, padx=14, pady=3)

        self.btn_mark_l = AccessibleButton(
            self.action_panel,
            text="⏱️ Mark Late [L]",
            command=lambda: self.handle_mark("Late"),
            corner_radius=10
        )
        self.btn_mark_l.pack(fill=tk.X, padx=14, pady=3)

        self.btn_mark_u = AccessibleButton(
            self.action_panel,
            text="⚪ Reset / Unmark [U]",
            command=lambda: self.handle_mark("Unmarked"),
            corner_radius=10
        )
        self.btn_mark_u.pack(fill=tk.X, padx=14, pady=3)

        self.sep_act = ctk.CTkFrame(self.action_panel, height=1, fg_color="#E2E8F0")
        self.sep_act.pack(fill=tk.X, padx=14, pady=10)

        self.lbl_batch_head = ctk.CTkLabel(
            self.action_panel,
            text="Batch & Undo Actions",
            font=("SF Pro Display", 11, "bold"),
            text_color="#64748B",
            anchor="w"
        )
        self.lbl_batch_head.pack(fill=tk.X, padx=14, pady=(0, 4))

        self.btn_bulk_present = AccessibleButton(
            self.action_panel,
            text="👥 Mark All Unmarked as Present",
            command=self.handle_bulk_mark_present,
            corner_radius=10
        )
        self.btn_bulk_present.pack(fill=tk.X, padx=14, pady=3)

        self.btn_undo = AccessibleButton(
            self.action_panel,
            text="↩️ Undo Last Mark [Ctrl+Z]",
            command=self.handle_undo,
            corner_radius=10
        )
        self.btn_undo.pack(fill=tk.X, padx=14, pady=3)

        self.btn_view_calendar = AccessibleButton(
            self.action_panel,
            text="📅 View Student Calendar",
            command=self.handle_open_calendar,
            corner_radius=10
        )
        self.btn_view_calendar.pack(fill=tk.X, padx=14, pady=3)

        self.btn_export_date = AccessibleButton(
            self.action_panel,
            text="📤 Export This Date to CSV",
            command=self.handle_export_date_csv,
            corner_radius=10
        )
        self.btn_export_date.pack(fill=tk.X, padx=14, pady=(3, 14))

        # Right Ledger Table Panel (Floating White Card)
        self.table_panel = CardFrame(self.workspace, corner_radius=14, border_width=1, border_color="#E2E8F0", fg_color="#FFFFFF")
        self.table_panel.grid(row=0, column=1, sticky="nsew")

        self.lbl_table_head = ctk.CTkLabel(
            self.table_panel,
            text="Daily Roll Call Roster",
            font=("SF Pro Display", 13, "bold"),
            text_color="#0F172A",
            anchor="w"
        )
        self.lbl_table_head.pack(fill=tk.X, padx=14, pady=(12, 8))

        self.tree_container = tk.Frame(self.table_panel, relief=tk.FLAT, bd=0)
        self.tree_container.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 14))

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
        self.tree.heading("Status", text="Attendance Status")

        self.tree.column("Roll", width=110, minwidth=80, stretch=False, anchor="center")
        self.tree.column("Name", width=220, minwidth=160, stretch=True, anchor="w")
        self.tree.column("Section", width=90, minwidth=70, stretch=False, anchor="center")
        self.tree.column("Status", width=130, minwidth=100, stretch=False, anchor="center")

        self.tree_scroll_y = ttk.Scrollbar(self.tree_container, orient="vertical", command=self.tree.yview)
        self.tree_scroll_x = ttk.Scrollbar(self.tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.tree_scroll_y.set, xscrollcommand=self.tree_scroll_x.set)

        self.tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Keyboard hotkeys on the Treeview
        self.tree.bind("<Return>", lambda e: self.handle_mark("Present"))
        self.tree.bind("<space>", lambda e: self.handle_mark("Absent"))
        self.tree.bind("<Key-l>", lambda e: self.handle_mark("Late"))
        self.tree.bind("<Key-L>", lambda e: self.handle_mark("Late"))
        self.tree.bind("<Key-u>", lambda e: self.handle_mark("Unmarked"))
        self.tree.bind("<Key-U>", lambda e: self.handle_mark("Unmarked"))

    def step_prev_day(self):
        try:
            dt = datetime.strptime(self.selected_date, "%Y-%m-%d") - timedelta(days=1)
            self.set_date(dt.strftime("%Y-%m-%d"))
        except ValueError:
            pass

    def step_next_day(self):
        try:
            dt = datetime.strptime(self.selected_date, "%Y-%m-%d") + timedelta(days=1)
            self.set_date(dt.strftime("%Y-%m-%d"))
        except ValueError:
            pass

    def set_today(self):
        self.set_date(datetime.now().strftime("%Y-%m-%d"))

    def set_date(self, date_str):
        self.selected_date = date_str
        self.ent_date.delete(0, tk.END)
        self.ent_date.insert(0, self.selected_date)
        self.refresh_table()

    def apply_custom_date(self):
        raw = self.ent_date.get().strip()
        try:
            valid_dt = datetime.strptime(raw, "%Y-%m-%d")
            self.set_date(valid_dt.strftime("%Y-%m-%d"))
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter date in format: YYYY-MM-DD")

    def handle_mark(self, status):
        selected = self.tree.selection()
        if not selected:
            # If nothing selected, select first row
            children = self.tree.get_children()
            if children:
                self.tree.selection_set(children[0])
                selected = (children[0],)
            else:
                return

        item = self.tree.item(selected[0])
        roll = item["values"][0]

        # Read previous status for Undo
        prev_record = self.db.get_single_attendance(roll, self.selected_date)
        prev_status = prev_record if prev_record else "Unmarked"

        self.db.record_attendance(roll, self.selected_date, status, user_role=self.current_role)
        self.undo_stack.append((roll, self.selected_date, prev_status))

        # Advance selection to next row automatically
        children = self.tree.get_children()
        idx = children.index(selected[0])
        self.refresh_table()

        updated_children = self.tree.get_children()
        if idx + 1 < len(updated_children):
            self.tree.selection_set(updated_children[idx + 1])
            self.tree.focus(updated_children[idx + 1])
            self.tree.see(updated_children[idx + 1])

        if hasattr(self.master.master, "notify_data_updated"):
            self.master.master.notify_data_updated()

    def handle_bulk_mark_present(self):
        count = self.db.mark_all_unmarked_present(self.selected_date, user_role=self.current_role)
        messagebox.showinfo("Bulk Marking", f"Marked {count} unmarked students as Present for {self.selected_date}.")
        self.refresh_table()
        if hasattr(self.master.master, "notify_data_updated"):
            self.master.master.notify_data_updated()

    def handle_undo(self):
        # Feature 7: Try atomic db undo first
        result = self.db.undo_last_mark(user_role=self.current_role)
        if result:
            self.refresh_table()
            messagebox.showinfo(
                "Undo Completed",
                f"Reverted {result['roll_no']} on {result['date']}\nFrom '{result['reverted_from']}' to '{result['restored_to']}'"
            )
            if hasattr(self.master.master, "notify_data_updated"):
                self.master.master.notify_data_updated()
            return

        if not self.undo_stack:
            messagebox.showinfo("Undo", "No remaining actions to undo.")
            return

        roll, date_str, prev_status = self.undo_stack.pop()
        self.db.record_attendance(roll, date_str, prev_status, user_role=self.current_role)
        self.refresh_table()
        messagebox.showinfo("Undo Completed", f"Reverted {roll} on {date_str} to: {prev_status}")
        if hasattr(self.master.master, "notify_data_updated"):
            self.master.master.notify_data_updated()

    def handle_open_calendar(self):
        """Feature 3: Open Monthly Attendance Calendar for selected student."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select Student", "Please select a student from the roster to view their monthly calendar.")
            return

        item = self.tree.item(selected[0])
        roll = item["values"][0]

        controller = self.master.master
        if hasattr(controller, "switch_view"):
            controller.switch_view("calendar")
            cal = controller.views.get("calendar")
            if cal and hasattr(cal, "select_student"):
                cal.select_student(roll)

    def update_role_permissions(self, role: str):
        """Feature 4: Update role permission context."""
        self.current_role = role

    def handle_export_date_csv(self):
        path = filedialog.asksaveasfilename(
            title=f"Export Attendance for {self.selected_date}",
            defaultextension=".csv",
            initialfile=f"attendance_{self.selected_date}.csv",
            filetypes=[("CSV Files", "*.csv")]
        )
        if not path:
            return

        count = self.db.export_attendance_by_date_csv(self.selected_date, path, user_role=self.current_role)
        messagebox.showinfo("Export Successful", f"Saved {count} records to:\n{path}")

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        search_query = self.search_box.get().strip() if hasattr(self, "search_box") else ""
        section_filter = self.sec_combo.get() if hasattr(self, "sec_combo") else "ALL"

        records = self.db.fetch_attendance_by_date(
            self.selected_date,
            search=search_query,
            section=section_filter
        )

        p_count = 0
        a_count = 0
        l_count = 0
        u_count = 0

        for r in records:
            raw_status = str(r[3]).strip() if len(r) > 3 and r[3] else "Unmarked"
            status_lower = raw_status.lower()

            if "present" in status_lower:
                tag = "present"
                display_status = "● Present"
                p_count += 1
            elif "absent" in status_lower:
                tag = "absent"
                display_status = "● Absent"
                a_count += 1
            elif "late" in status_lower:
                tag = "late"
                display_status = "● Late"
                l_count += 1
            else:
                tag = "unmarked"
                display_status = "○ Unmarked"
                u_count += 1

            display_row = (r[0], r[1], r[2], display_status)
            self.tree.insert("", tk.END, values=display_row, tags=(tag,))

        # Update Mini KPI Metrics
        total_marked = p_count + a_count + l_count
        rate = (p_count / total_marked * 100.0) if total_marked > 0 else 0.0

        self.lbl_stat_present.configure(text=f"Present: {p_count}")
        self.lbl_stat_absent.configure(text=f"Absent: {a_count}")
        self.lbl_stat_late.configure(text=f"Late: {l_count}")
        self.lbl_stat_unmarked.configure(text=f"Unmarked: {u_count}")
        self.lbl_stat_rate.configure(text=f"Attendance Rate: {rate:.1f}%")

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

        # Control Bar
        self.control_bar.configure(fg_color=card_bg, border_color=card_border)
        self.lbl_date_tag.configure(text_color=fg, font=font_cfg.get("form_label", font_cfg["body_bold"]))
        self.lbl_search.configure(text_color=fg, font=font_cfg.get("form_label", font_cfg["body_bold"]))
        self.lbl_sec.configure(text_color=fg, font=font_cfg.get("form_label", font_cfg["body_bold"]))

        # Mini KPI Bar
        self.kpi_bar.configure(fg_color=card_bg, border_color=card_border)
        self.lbl_stat_present.configure(font=font_cfg.get("body_bold", ("SF Pro Display", 11, "bold")))
        self.lbl_stat_absent.configure(font=font_cfg.get("body_bold", ("SF Pro Display", 11, "bold")))
        self.lbl_stat_late.configure(font=font_cfg.get("body_bold", ("SF Pro Display", 11, "bold")))
        self.lbl_stat_unmarked.configure(font=font_cfg.get("body_bold", ("SF Pro Display", 11, "bold")))
        self.lbl_stat_rate.configure(font=font_cfg.get("body_bold", ("SF Pro Display", 12, "bold")))

        for ent in [self.ent_date, self.search_box]:
            ent.apply_theme(theme, font_cfg)

        pad_x = font_cfg["btn_pad_x"]
        pad_y = font_cfg["btn_pad_y"]

        for btn in [self.btn_prev_day, self.btn_next_day, self.btn_today]:
            btn.apply_style(
                bg=theme["btn_secondary_bg"],
                fg=theme["btn_secondary_fg"],
                font=font_cfg.get("btn_font", ("SF Pro Display", font_cfg["body"])),
                focus_ring=theme["focus_ring"],
                border_color=theme["btn_secondary_border"],
                padx=pad_x - 2,
                pady=pad_y - 2
            )

        # Left Action Panel
        self.action_panel.configure(fg_color=card_bg, border_color=card_border)
        self.lbl_act_head.configure(text_color=fg, font=font_cfg.get("section_title", font_cfg["title_bold"]))
        self.lbl_batch_head.configure(text_color=theme["fg_muted"], font=font_cfg.get("form_label", font_cfg["body_bold"]))
        self.sep_act.configure(fg_color=card_border)

        is_hc = theme.get("is_high_contrast", False)

        self.btn_mark_p.apply_style(
            bg=theme["status_present"],
            fg="#000000" if is_hc else "#FFFFFF",
            font=font_cfg.get("btn_bold", ("SF Pro Display", font_cfg["body"], "bold")),
            focus_ring=theme["focus_ring"],
            padx=pad_x,
            pady=pad_y
        )
        self.btn_mark_a.apply_style(
            bg=theme["status_absent"],
            fg="#000000" if is_hc else "#FFFFFF",
            font=font_cfg.get("btn_bold", ("SF Pro Display", font_cfg["body"], "bold")),
            focus_ring=theme["focus_ring"],
            padx=pad_x,
            pady=pad_y
        )
        self.btn_mark_l.apply_style(
            bg=theme["status_late"],
            fg="#000000",
            font=font_cfg.get("btn_bold", ("SF Pro Display", font_cfg["body"], "bold")),
            focus_ring=theme["focus_ring"],
            padx=pad_x,
            pady=pad_y
        )
        self.btn_mark_u.apply_style(
            bg=theme["btn_secondary_bg"],
            fg=theme["btn_secondary_fg"],
            font=font_cfg.get("btn_font", ("SF Pro Display", font_cfg["body"])),
            focus_ring=theme["focus_ring"],
            border_color=theme["btn_secondary_border"],
            padx=pad_x,
            pady=pad_y - 1
        )
        self.btn_bulk_present.apply_style(
            bg=theme["btn_secondary_bg"],
            fg=theme["btn_secondary_fg"],
            font=font_cfg.get("btn_bold", ("SF Pro Display", font_cfg["body"], "bold")),
            focus_ring=theme["focus_ring"],
            border_color=theme["btn_secondary_border"],
            padx=pad_x,
            pady=pad_y
        )
        self.btn_undo.apply_style(
            bg=theme["btn_secondary_bg"],
            fg=theme["btn_secondary_fg"],
            font=font_cfg.get("btn_bold", ("SF Pro Display", font_cfg["body"], "bold")),
            focus_ring=theme["focus_ring"],
            border_color=theme["btn_secondary_border"],
            padx=pad_x,
            pady=pad_y
        )
        self.btn_view_calendar.apply_style(
            bg=theme["btn_secondary_bg"],
            fg=theme["btn_secondary_fg"],
            font=font_cfg.get("btn_font", ("SF Pro Display", font_cfg["body"])),
            focus_ring=theme["focus_ring"],
            border_color=theme["btn_secondary_border"],
            padx=pad_x,
            pady=pad_y - 1
        )
        self.btn_export_date.apply_style(
            bg=theme["btn_secondary_bg"],
            fg=theme["btn_secondary_fg"],
            font=font_cfg.get("btn_font", ("SF Pro Display", font_cfg["body"])),
            focus_ring=theme["focus_ring"],
            border_color=theme["btn_secondary_border"],
            padx=pad_x,
            pady=pad_y - 1
        )

        # Table panel
        self.table_panel.configure(fg_color=card_bg, border_color=card_border)
        self.lbl_table_head.configure(text_color=fg, font=font_cfg.get("section_title", font_cfg["title_bold"]))
        self.tree_container.configure(bg=card_bg)

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

        col_specs = [
            ("Roll", font_cfg["col_widths"]["Roll"], False, "center"),
            ("Name", font_cfg["col_widths"]["Name"], True, "w"),
            ("Section", font_cfg["col_widths"]["Section"], False, "center"),
            ("Status", font_cfg["col_widths"]["Status"], False, "center")
        ]
        for col, width, stretch, anchor in col_specs:
            self.tree.column(col, width=width, minwidth=max(60, width - 20), stretch=stretch, anchor=anchor)
            self.tree.heading(col, anchor=anchor)

        # Soft Status Pill Badges
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
