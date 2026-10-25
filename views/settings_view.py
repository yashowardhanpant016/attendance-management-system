"""
Settings and System Administration View.
Matches EduAttend / CampusEdge modern white-card SaaS educational ERP aesthetic.
Handles theme configuration (EduAttend Light SaaS, Slate Dark, High Contrast WCAG AAA),
dynamic font scaling, database backup/restore operations, and the keyboard shortcuts guide.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk

from widgets import AccessibleButton, CardFrame
from theme import get_theme, get_fonts


class SettingsView(ctk.CTkFrame):
    def __init__(self, master, db=None, app_controller=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.db = db
        self.app = app_controller

        self.build_ui()

    def build_ui(self):
        # Header banner
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill=tk.X, pady=(0, 12))

        self.lbl_title = ctk.CTkLabel(
            self.header_frame,
            text="System Configuration, Accessibility & Maintenance",
            font=("SF Pro Display", 15, "bold"),
            text_color="#0F172A",
            anchor="w"
        )
        self.lbl_title.pack(side=tk.LEFT)

        self.lbl_badge = ctk.CTkLabel(
            self.header_frame,
            text="High-Contrast & Low-Strain Display Options",
            font=("SF Pro Display", 11),
            text_color="#64748B",
            anchor="e"
        )
        self.lbl_badge.pack(side=tk.RIGHT)

        # -----------------------------------------------------
        # Grid containing Settings Cards
        # -----------------------------------------------------
        self.cards_grid = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_grid.pack(fill=tk.BOTH, expand=True)
        self.cards_grid.columnconfigure(0, weight=1)
        self.cards_grid.columnconfigure(1, weight=1)

        # -----------------------------------------------------
        # Card 1: Appearance & Accessibility (Floating White Card)
        # -----------------------------------------------------
        self.card_theme = CardFrame(self.cards_grid, corner_radius=14, border_width=1, border_color="#E2E8F0", fg_color="#FFFFFF")
        self.card_theme.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 10))

        self.lbl_theme_head = ctk.CTkLabel(
            self.card_theme,
            text="🎨 Appearance & Visual Accessibility",
            font=("SF Pro Display", 13, "bold"),
            text_color="#0F172A",
            anchor="w"
        )
        self.lbl_theme_head.pack(fill=tk.X, padx=16, pady=(14, 6))

        self.lbl_theme_desc = ctk.CTkLabel(
            self.card_theme,
            text="Choose an ergonomic visual theme engineered to mitigate ocular strain or deliver maximum contrast for low-vision environments.",
            font=("SF Pro Display", 11),
            text_color="#64748B",
            wraplength=420,
            justify=tk.LEFT,
            anchor="w"
        )
        self.lbl_theme_desc.pack(fill=tk.X, padx=16, pady=(0, 10))

        # Theme Buttons (Rounded Pills)
        self.btn_light = AccessibleButton(
            self.card_theme, text="☀️ EduAttend Light Palette (Default)",
            command=lambda: self.app.set_theme("light"),
            corner_radius=10
        )
        self.btn_light.pack(fill=tk.X, padx=16, pady=3)

        self.btn_dark = AccessibleButton(
            self.card_theme, text="🌙 Low-Strain Dark Slate [Ctrl+D]",
            command=lambda: self.app.set_theme("dark"),
            corner_radius=10
        )
        self.btn_dark.pack(fill=tk.X, padx=16, pady=3)

        self.btn_contrast = AccessibleButton(
            self.card_theme, text="⚡ High Contrast Mode [Ctrl+H]",
            command=lambda: self.app.set_theme("high_contrast"),
            corner_radius=10
        )
        self.btn_contrast.pack(fill=tk.X, padx=16, pady=3)

        self.sep_theme = ctk.CTkFrame(self.card_theme, height=1, fg_color="#E2E8F0")
        self.sep_theme.pack(fill=tk.X, padx=16, pady=10)

        # Dynamic Font Scale
        self.lbl_font_head = ctk.CTkLabel(
            self.card_theme,
            text="🔍 Dynamic Font Resizing Engine",
            font=("SF Pro Display", 11, "bold"),
            text_color="#0F172A",
            anchor="w"
        )
        self.lbl_font_head.pack(fill=tk.X, padx=16, pady=(0, 6))

        self.font_btn_row = ctk.CTkFrame(self.card_theme, fg_color="transparent")
        self.font_btn_row.pack(fill=tk.X, padx=16, pady=(0, 14))

        self.btn_font_normal = AccessibleButton(self.font_btn_row, text="Normal", command=lambda: self.app.set_font_scale("normal"), corner_radius=8)
        self.btn_font_normal.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        self.btn_font_large = AccessibleButton(self.font_btn_row, text="Large", command=lambda: self.app.set_font_scale("large"), corner_radius=8)
        self.btn_font_large.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        self.btn_font_xlarge = AccessibleButton(self.font_btn_row, text="X-Large", command=lambda: self.app.set_font_scale("xlarge"), corner_radius=8)
        self.btn_font_xlarge.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))

        # -----------------------------------------------------
        # Card 2: Database Persistence & Backup Tools (Floating White Card)
        # -----------------------------------------------------
        self.card_db = CardFrame(self.cards_grid, corner_radius=14, border_width=1, border_color="#E2E8F0", fg_color="#FFFFFF")
        self.card_db.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 10))

        self.lbl_db_head = ctk.CTkLabel(
            self.card_db,
            text="💾 Database Persistence & Disaster Recovery",
            font=("SF Pro Display", 13, "bold"),
            text_color="#0F172A",
            anchor="w"
        )
        self.lbl_db_head.pack(fill=tk.X, padx=16, pady=(14, 6))

        self.lbl_db_desc = ctk.CTkLabel(
            self.card_db,
            text="All student records and attendance dates are securely persisted in SQLite. Perform atomic online backups or restore safe snapshots without service interruption.",
            font=("SF Pro Display", 11),
            text_color="#64748B",
            wraplength=420,
            justify=tk.LEFT,
            anchor="w"
        )
        self.lbl_db_desc.pack(fill=tk.X, padx=16, pady=(0, 10))

        self.btn_backup = AccessibleButton(
            self.card_db, text="📦 Create Database Backup File (.db)",
            command=self.handle_backup_db,
            corner_radius=10
        )
        self.btn_backup.pack(fill=tk.X, padx=16, pady=3)

        self.btn_restore = AccessibleButton(
            self.card_db, text="♻️ Restore Database from Backup",
            command=self.handle_restore_db,
            corner_radius=10
        )
        self.btn_restore.pack(fill=tk.X, padx=16, pady=3)

        self.btn_reseed = AccessibleButton(
            self.card_db, text="🔄 Reset / Re-seed Default Sample Data",
            command=self.handle_reseed_db,
            corner_radius=10
        )
        self.btn_reseed.pack(fill=tk.X, padx=16, pady=3)

        self.btn_audit_log = AccessibleButton(
            self.card_db, text="📜 View System Audit Trail",
            command=self.handle_show_audit,
            corner_radius=10
        )
        self.btn_audit_log.pack(fill=tk.X, padx=16, pady=3)

        self.sep_db = ctk.CTkFrame(self.card_db, height=1, fg_color="#E2E8F0")
        self.sep_db.pack(fill=tk.X, padx=16, pady=10)

        self.lbl_db_path = ctk.CTkLabel(
            self.card_db,
            text=f"Active Database File: {self.db.db_name}",
            font=("SF Pro Display", 10, "italic"),
            text_color="#64748B",
            anchor="w"
        )
        self.lbl_db_path.pack(fill=tk.X, padx=16, pady=(0, 14))

        # -----------------------------------------------------
        # Card 3: Keyboard Shortcuts Cheat Sheet (Spans across bottom)
        # -----------------------------------------------------
        self.card_keys = CardFrame(self.cards_grid, corner_radius=14, border_width=1, border_color="#E2E8F0", fg_color="#FFFFFF")
        self.card_keys.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(6, 0))

        self.lbl_keys_head = ctk.CTkLabel(
            self.card_keys,
            text="⌨️ Comprehensive Keyboard Navigation & Hotkey Index",
            font=("SF Pro Display", 13, "bold"),
            text_color="#0F172A",
            anchor="w"
        )
        self.lbl_keys_head.pack(fill=tk.X, padx=16, pady=(12, 6))

        # Shortcut table
        self.tree_shortcuts_container = tk.Frame(self.card_keys, relief=tk.FLAT, bd=0)
        self.tree_shortcuts_container.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 14))

        self.tree_shortcuts = ttk.Treeview(
            self.tree_shortcuts_container,
            columns=("Key", "Action", "Context / Ergonomic Benefit"),
            show="headings",
            height=6
        )
        self.tree_shortcuts.heading("Key", text="Shortcut Key")
        self.tree_shortcuts.heading("Action", text="Triggered Action")
        self.tree_shortcuts.heading("Context / Ergonomic Benefit", text="Ergonomic Benefit / TQM Standard")

        self.tree_shortcuts.column("Key", width=120, minwidth=100, stretch=False, anchor="center")
        self.tree_shortcuts.column("Action", width=220, minwidth=160, stretch=False, anchor="w")
        self.tree_shortcuts.column("Context / Ergonomic Benefit", width=380, minwidth=240, stretch=True, anchor="w")

        self.tree_shortcuts_scroll_y = ttk.Scrollbar(self.tree_shortcuts_container, orient="vertical", command=self.tree_shortcuts.yview)
        self.tree_shortcuts_scroll_x = ttk.Scrollbar(self.tree_shortcuts_container, orient="horizontal", command=self.tree_shortcuts.xview)
        self.tree_shortcuts.configure(yscrollcommand=self.tree_shortcuts_scroll_y.set, xscrollcommand=self.tree_shortcuts_scroll_x.set)

        self.tree_shortcuts_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_shortcuts_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree_shortcuts.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        shortcuts_data = [
            ("Ctrl + 1", "Jump to Dashboard", "Instant overview of metrics and trends"),
            ("Ctrl + 2", "Jump to Manage Students", "Direct registration and directory search"),
            ("Ctrl + 3", "Jump to Daily Attendance", "One-click access to roll call ledger"),
            ("Ctrl + 4", "Jump to Monthly Calendar", "7x5 Day-grid with P/A/L status markers"),
            ("Ctrl + 5", "Jump to Reports & Analytics", "Access statistical reports and PDF/CSV export"),
            ("Ctrl + 6", "Jump to Settings & Backup", "Appearance, database recovery & audit log"),
            ("Ctrl + H", "Toggle High Contrast", "Yellow on pure black contrast (>19:1 ratio)"),
            ("Ctrl + D", "Toggle Dark Mode", "Low-luminance palette mitigating ocular strain"),
            ("Ctrl + T", "Cycle Font Scale", "Normal ➜ Large ➜ X-Large with auto rowheight scaling"),
            ("Ctrl + A", "Focus Add Student Input", "Immediate data entry without mouse reliance"),
            ("Ctrl + M", "Quick Mark Present", "One-key attendance marking for selected student"),
            ("Ctrl + Z", "Undo Last Attendance Change", "Instant mistake-proofing (Poka-Yoke) rollback"),
            ("Space Bar", "Quick Mark Absent", "Rapid single-key absent toggle on table rows"),
            ("P Key", "Export Student PDF Report Card", "Formal institutional report card with shortfall analysis"),
            ("Tab / Shift+Tab", "Traverse Focus Loop", "Seamless keyboard focus cycle with 3px visible outline"),
            ("F1", "Accessibility Modal Guide", "On-screen quick reference cheat sheet")
        ]

        for s in shortcuts_data:
            self.tree_shortcuts.insert("", tk.END, values=s)

    def update_role_permissions(self, role: str):
        """Feature 4: Update settings permissions based on Admin vs. Faculty role."""
        self.current_role = role
        is_admin = (role.lower() == "admin")

        if is_admin:
            self.btn_restore.configure(state="normal", text="♻️ Restore Database from Backup")
            self.btn_reseed.configure(state="normal", text="🔄 Reset / Re-seed Default Sample Data")
        else:
            self.btn_restore.configure(state="normal", text="♻️ Restore [Admin Role Required]")
            self.btn_reseed.configure(state="normal", text="🔄 Re-seed [Admin Role Required]")

    def handle_show_audit(self):
        """Feature 7: Launch System Audit Trail Viewer Modal."""
        from views.audit_dialog import AuditLogDialog
        AuditLogDialog(
            parent=self,
            db=self.db,
            theme=getattr(self.app, "current_theme_key", "light"),
            font_cfg=FONT_SIZES.get(getattr(self.app, "current_font_scale", "normal"))
        )

    def handle_backup_db(self):
        filepath = filedialog.asksaveasfilename(
            title="Save Database Backup As",
            initialfile="attendance_backup.db",
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        try:
            self.db.backup_database(filepath, user_role=getattr(self, "current_role", "Faculty"))
            messagebox.showinfo("Backup Completed", f"Atomic database backup successfully saved to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Backup Failed", f"Failed to create backup: {str(e)}")

    def handle_restore_db(self):
        # Feature 4: Role-Based Protection
        if getattr(self, "current_role", "Faculty").lower() != "admin":
            messagebox.showwarning(
                "Access Denied",
                "Database restore operations require 'Admin' privileges.\n"
                "Please switch to Admin Mode via the top header bar."
            )
            return

        filepath = filedialog.askopenfilename(
            title="Select Database Backup to Restore",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        if messagebox.askyesno(
            "Confirm Restore",
            "Restoring will overwrite current database records with the selected backup snapshot.\nAre you sure you want to proceed?"
        ):
            try:
                self.db.restore_database(filepath, user_role=getattr(self, "current_role", "Admin"))
                messagebox.showinfo("Database Restored", "Database was restored successfully from backup.")
                self.app.notify_data_updated()
            except Exception as e:
                messagebox.showerror("Restore Failed", f"Failed to restore database: {str(e)}")

    def handle_reseed_db(self):
        # Feature 4: Role-Based Protection
        if getattr(self, "current_role", "Faculty").lower() != "admin":
            messagebox.showwarning(
                "Access Denied",
                "Database re-seeding operations require 'Admin' privileges.\n"
                "Please switch to Admin Mode via the top header bar."
            )
            return

        if messagebox.askyesno(
            "Confirm Sample Reseed",
            "This will re-insert default sample student records.\nExisting records will not be deleted."
        ):
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                self.db._seed_sample_data(cursor, conn)
            self.db.log_audit_event("DB_RESEED", "Sample students re-seeded", getattr(self, "current_role", "Admin"))
            messagebox.showinfo("Reseed Complete", "Sample student records confirmed and restored.")
            self.app.notify_data_updated()

    def apply_theme(self, theme_or_key="light", font_scale_or_cfg="normal"):
        theme = get_theme(theme_or_key)
        font_cfg = get_fonts(font_scale_or_cfg)
        card_bg = theme["card_bg"]
        card_border = theme["card_border"]
        fg = theme["fg"]
        muted_fg = theme["fg_muted"]

        self.lbl_title.configure(text_color=fg, font=font_cfg.get("page_title", font_cfg["header_bold"]))
        self.lbl_badge.configure(text_color=muted_fg, font=font_cfg.get("badge_font", font_cfg["title_bold"]))

        # Cards
        for card in [self.card_theme, self.card_db, self.card_keys]:
            card.configure(fg_color=card_bg, border_color=card_border)

        self.lbl_theme_head.configure(text_color=fg, font=font_cfg.get("section_title", font_cfg["title_bold"]))
        self.lbl_theme_desc.configure(text_color=muted_fg, font=font_cfg.get("body_font", ("SF Pro Display", font_cfg["body"])))
        self.lbl_font_head.configure(text_color=fg, font=font_cfg.get("section_title", font_cfg["title_bold"]))
        self.sep_theme.configure(fg_color=card_border)

        self.lbl_db_head.configure(text_color=fg, font=font_cfg.get("section_title", font_cfg["title_bold"]))
        self.lbl_db_desc.configure(text_color=muted_fg, font=font_cfg.get("body_font", ("SF Pro Display", font_cfg["body"])))
        self.sep_db.configure(fg_color=card_border)
        family = font_cfg.get("family", "SF Pro Display")
        self.lbl_db_path.configure(text_color=muted_fg, font=(family, font_cfg["body"], "italic"))

        self.lbl_keys_head.configure(text_color=fg, font=font_cfg.get("section_title", font_cfg["title_bold"]))

        pad_x = font_cfg["btn_pad_x"]
        pad_y = font_cfg["btn_pad_y"]

        # Action Buttons
        for btn in [self.btn_light, self.btn_dark, self.btn_contrast,
                    self.btn_font_normal, self.btn_font_large, self.btn_font_xlarge,
                    self.btn_backup, self.btn_restore, self.btn_reseed, self.btn_audit_log]:
            btn.apply_style(
                bg=theme["btn_secondary_bg"],
                fg=theme["btn_secondary_fg"],
                font=font_cfg.get("btn_font", ("SF Pro Display", font_cfg["body"])),
                focus_ring=theme["focus_ring"],
                border_color=theme["btn_secondary_border"],
                padx=pad_x,
                pady=pad_y
            )

        # Highlight current font scale
        current_scale = self.app.current_font_scale
        scale_map = {
            "normal": self.btn_font_normal,
            "large": self.btn_font_large,
            "xlarge": self.btn_font_xlarge
        }
        if current_scale in scale_map:
            scale_map[current_scale].apply_style(
                bg=theme["btn_primary_bg"],
                fg=theme["btn_primary_fg"],
                font=font_cfg.get("btn_bold", ("SF Pro Display", font_cfg["body"], "bold")),
                focus_ring=theme["focus_ring"],
                padx=pad_x,
                pady=pad_y
            )

        # Style shortcuts table with 38px row height baseline
        self.tree_shortcuts_container.configure(bg=card_bg)
        rowheight = font_cfg.get("tree_row", 38)
        style = ttk.Style()
        style.configure(
            "Shortcuts.Treeview",
            background=theme["tree_bg"],
            foreground=theme["tree_fg"],
            fieldbackground=theme["tree_bg"],
            rowheight=rowheight,
            font=font_cfg.get("tree_row_font", ("SF Pro Display", font_cfg["body"]))
        )
        style.configure(
            "Shortcuts.Treeview.Heading",
            background=theme["tree_head_bg"],
            foreground=theme["tree_head_fg"],
            font=font_cfg.get("tree_head_font", ("SF Pro Display", font_cfg["tree_head"], "bold"))
        )
        style.map(
            "Shortcuts.Treeview",
            background=[("selected", theme["select_bg"])],
            foreground=[("selected", theme["select_fg"])]
        )
        self.tree_shortcuts.configure(style="Shortcuts.Treeview")

        # Configure columns and headings
        self.tree_shortcuts.column("Key", width=max(120, int(font_cfg["col_widths"]["Roll"] * 0.9)), stretch=False, anchor="center")
        self.tree_shortcuts.column("Action", width=max(200, int(font_cfg["col_widths"]["Name"] * 0.9)), stretch=False, anchor="w")
        self.tree_shortcuts.column("Context / Ergonomic Benefit", width=380, stretch=True, anchor="w")
        self.tree_shortcuts.heading("Key", anchor="center")
        self.tree_shortcuts.heading("Action", anchor="w")
        self.tree_shortcuts.heading("Context / Ergonomic Benefit", anchor="w")
