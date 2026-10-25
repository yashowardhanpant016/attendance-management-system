"""
CSV Pre-Validation Staging Dialog (Poka-Yoke).
Feature 6: Previews uploaded student CSV rows before committing to SQLite.
Automatically highlights duplicate roll numbers or blank names in red/amber.
Ensures only sanitized, valid records are inserted.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk

from widgets import AccessibleButton, CardFrame
from theme import THEMES, get_theme, get_fonts, FONT_SIZES


class CSVImportStagingDialog(ctk.CTkToplevel):
    def __init__(self, parent, csv_filepath, db, on_commit_callback, theme, font_cfg, user_role="Admin"):
        super().__init__(parent)
        self.title("Smart CSV Import - Poka-Yoke Staging Preview")
        self.geometry("740x520")
        self.minsize(680, 440)
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self.csv_filepath = csv_filepath
        self.db = db
        self.on_commit = on_commit_callback
        self.theme = theme
        self.font_cfg = font_cfg
        self.user_role = user_role

        # Run Poka-Yoke Validation
        self.valid_rows, self.invalid_rows = self.db.validate_students_csv(self.csv_filepath)

        self.build_ui()
        self.apply_theme()

    def build_ui(self):
        self.card = CardFrame(self, corner_radius=14, border_width=1, border_color="#E2E8F0", fg_color="#FFFFFF")
        self.card.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        # Header Title
        self.lbl_head = ctk.CTkLabel(
            self.card,
            text="Smart CSV Pre-Validation Staging Table",
            font=("SF Pro Display", 14, "bold"),
            text_color="#0F172A",
            anchor="w"
        )
        self.lbl_head.pack(fill=tk.X, padx=16, pady=(14, 4))

        self.lbl_sub = ctk.CTkLabel(
            self.card,
            text=f"Inspecting file: {self.csv_filepath}",
            font=("SF Pro Display", 10),
            text_color="#64748B",
            anchor="w"
        )
        self.lbl_sub.pack(fill=tk.X, padx=16, pady=(0, 10))

        # KPI Summary Row
        self.summary_bar = ctk.CTkFrame(self.card, fg_color="transparent")
        self.summary_bar.pack(fill=tk.X, padx=16, pady=(0, 10))

        tot = len(self.valid_rows) + len(self.invalid_rows)
        val = len(self.valid_rows)
        inv = len(self.invalid_rows)

        self.lbl_stat_total = ctk.CTkLabel(self.summary_bar, text=f"Total Rows: {tot}", font=("SF Pro Display", 11, "bold"), text_color="#0F172A")
        self.lbl_stat_total.pack(side=tk.LEFT, padx=(0, 14))

        self.lbl_stat_valid = ctk.CTkLabel(self.summary_bar, text=f"● Ready to Commit: {val}", font=("SF Pro Display", 11, "bold"), text_color="#10B981")
        self.lbl_stat_valid.pack(side=tk.LEFT, padx=14)

        self.lbl_stat_invalid = ctk.CTkLabel(self.summary_bar, text=f"● Skipped / Conflicts: {inv}", font=("SF Pro Display", 11, "bold"), text_color="#EF4444")
        self.lbl_stat_invalid.pack(side=tk.LEFT, padx=14)

        # Staging Preview Treeview
        self.tree_container = tk.Frame(self.card, relief=tk.FLAT, bd=0)
        self.tree_container.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 12))

        self.tree_style = ttk.Style()
        self.tree = ttk.Treeview(
            self.tree_container,
            columns=("Row", "Roll", "Name", "Section", "Status", "Note"),
            show="headings",
            selectmode="browse",
            takefocus=True
        )
        self.tree.heading("Row", text="#")
        self.tree.heading("Roll", text="Roll No.")
        self.tree.heading("Name", text="Student Name")
        self.tree.heading("Section", text="Section")
        self.tree.heading("Status", text="Validation")
        self.tree.heading("Note", text="Poka-Yoke Diagnosis")

        self.tree.column("Row", width=45, minwidth=40, stretch=False, anchor="center")
        self.tree.column("Roll", width=105, minwidth=80, stretch=False, anchor="center")
        self.tree.column("Name", width=180, minwidth=140, stretch=True, anchor="w")
        self.tree.column("Section", width=80, minwidth=60, stretch=False, anchor="center")
        self.tree.column("Status", width=110, minwidth=90, stretch=False, anchor="center")
        self.tree.column("Note", width=200, minwidth=140, stretch=True, anchor="w")

        self.tree_scroll_y = ttk.Scrollbar(self.tree_container, orient="vertical", command=self.tree.yview)
        self.tree_scroll_x = ttk.Scrollbar(self.tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.tree_scroll_y.set, xscrollcommand=self.tree_scroll_x.set)

        self.tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Populate rows
        all_records = []
        for r in self.valid_rows:
            all_records.append((r["row_idx"], r["roll_no"], r["name"], r["section"], "● Ready", r["note"], "valid"))
        for r in self.invalid_rows:
            tag = "conflict" if "enrolled" in r["note"].lower() or "duplicate" in r["note"].lower() else "invalid"
            st_text = "⚠️ Duplicate" if tag == "conflict" else "❌ Invalid"
            all_records.append((r["row_idx"], r["roll_no"], r["name"], r["section"], st_text, r["note"], tag))

        all_records.sort(key=lambda x: x[0])

        for rec in all_records:
            row_vals = (rec[0], rec[1], rec[2], rec[3], rec[4], rec[5])
            self.tree.insert("", tk.END, values=row_vals, tags=(rec[6],))

        # Action Buttons Row
        self.btn_bar = ctk.CTkFrame(self.card, fg_color="transparent")
        self.btn_bar.pack(fill=tk.X, padx=16, pady=(0, 14))

        self.btn_commit = AccessibleButton(
            self.btn_bar,
            text=f"✅ Commit {val} Valid Records to SQLite",
            command=self.handle_commit,
            corner_radius=10,
            state="normal" if val > 0 else "disabled"
        )
        self.btn_commit.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_cancel = AccessibleButton(
            self.btn_bar,
            text="Cancel",
            command=self.destroy,
            corner_radius=10
        )
        self.btn_cancel.pack(side=tk.RIGHT)

        self.bind("<Escape>", lambda e: self.destroy())

    def handle_commit(self):
        if not self.valid_rows:
            messagebox.showinfo("No Valid Records", "There are no valid records to commit.", parent=self)
            return

        count = self.db.commit_validated_students(self.valid_rows, user_role=self.user_role)
        messagebox.showinfo(
            "CSV Commit Successful",
            f"Successfully inserted {count} sanitized student records into SQLite.\n"
            f"Skipped {len(self.invalid_rows)} conflicts/invalid rows.",
            parent=self
        )
        if self.on_commit:
            self.on_commit()
        self.destroy()

    def apply_theme(self, theme=None, font_cfg=None):
        if theme is not None:
            self.theme = theme
        if font_cfg is not None:
            self.font_cfg = font_cfg

        theme = get_theme(self.theme)
        font_cfg = get_fonts(self.font_cfg)

        card_bg = theme["card_bg"]
        card_border = theme["card_border"]
        fg = theme["fg"]

        self.configure(fg_color=theme["bg"])
        self.card.configure(fg_color=card_bg, border_color=card_border)
        self.lbl_head.configure(text_color=fg)
        self.lbl_sub.configure(text_color=theme["fg_muted"])
        self.tree_container.configure(bg=card_bg)

        pad_x = font_cfg["btn_pad_x"]
        pad_y = font_cfg["btn_pad_y"]

        self.btn_commit.apply_style(
            bg=theme["btn_primary_bg"],
            fg=theme["btn_primary_fg"],
            font=font_cfg.get("btn_bold", ("SF Pro Display", font_cfg["body"], "bold")),
            focus_ring=theme["focus_ring"],
            padx=pad_x,
            pady=pad_y
        )
        self.btn_cancel.apply_style(
            bg=theme["btn_secondary_bg"],
            fg=theme["btn_secondary_fg"],
            font=font_cfg.get("btn_font", ("SF Pro Display", font_cfg["body"])),
            focus_ring=theme["focus_ring"],
            border_color=theme["btn_secondary_border"],
            padx=pad_x,
            pady=pad_y
        )

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

        # Tags
        self.tree.tag_configure("valid", background=theme.get("status_present_bg", "#DCFCE7"), foreground=theme.get("status_present_fg", "#15803D"))
        self.tree.tag_configure("conflict", background=theme.get("status_warning_bg", "#FEF3C7"), foreground=theme.get("status_warning_fg", "#92400E"))
        self.tree.tag_configure("invalid", background=theme.get("status_absent_bg", "#FEE2E2"), foreground=theme.get("status_absent_fg", "#B91C1C"))
