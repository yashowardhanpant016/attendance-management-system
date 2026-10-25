"""
Audit Log Viewer Dialog.
Feature 7: Displays the operational audit log history:
(id, timestamp, action_type, details, user_role).
Allows administrative verification of all attendance and student operations.
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

from widgets import AccessibleButton, CardFrame, FocusRingEntry
from theme import THEMES, get_theme, get_fonts, FONT_SIZES


class AuditLogDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, theme, font_cfg):
        super().__init__(parent)
        self.title("Operational Audit Trail & Action History")
        self.geometry("820x540")
        self.minsize(720, 440)
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self.db = db
        self.theme = theme
        self.font_cfg = font_cfg

        self.build_ui()
        self.apply_theme()
        self.load_logs()

    def build_ui(self):
        self.card = CardFrame(self, corner_radius=14, border_width=1, border_color="#E2E8F0", fg_color="#FFFFFF")
        self.card.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        # Header Title
        self.lbl_head = ctk.CTkLabel(
            self.card,
            text="Institutional Audit Trail & Operational Log",
            font=("SF Pro Display", 14, "bold"),
            text_color="#0F172A",
            anchor="w"
        )
        self.lbl_head.pack(fill=tk.X, padx=16, pady=(14, 4))

        self.lbl_sub = ctk.CTkLabel(
            self.card,
            text="Immutable SQLite transaction records tracking attendance marks, enrollments, and deletions.",
            font=("SF Pro Display", 10),
            text_color="#64748B",
            anchor="w"
        )
        self.lbl_sub.pack(fill=tk.X, padx=16, pady=(0, 10))

        # Filter Bar
        self.filter_bar = ctk.CTkFrame(self.card, fg_color="transparent")
        self.filter_bar.pack(fill=tk.X, padx=16, pady=(0, 10))

        self.lbl_filter = ctk.CTkLabel(self.filter_bar, text="Search Logs:", font=("SF Pro Display", 11, "bold"), text_color="#0F172A")
        self.lbl_filter.pack(side=tk.LEFT, padx=(0, 6))

        self.ent_search = FocusRingEntry(self.filter_bar, width=240)
        self.ent_search.pack(side=tk.LEFT, padx=(0, 10))
        self.ent_search.bind("<KeyRelease>", lambda e: self.load_logs())

        self.btn_refresh = AccessibleButton(self.filter_bar, text="🔄 Refresh", command=self.load_logs, corner_radius=8)
        self.btn_refresh.pack(side=tk.LEFT)

        # Audit Table
        self.tree_container = tk.Frame(self.card, relief=tk.FLAT, bd=0)
        self.tree_container.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 12))

        self.tree_style = ttk.Style()
        self.tree = ttk.Treeview(
            self.tree_container,
            columns=("ID", "Timestamp", "Action", "Role", "Details"),
            show="headings",
            selectmode="browse",
            takefocus=True
        )
        self.tree.heading("ID", text="ID")
        self.tree.heading("Timestamp", text="Timestamp")
        self.tree.heading("Action", text="Action Type")
        self.tree.heading("Role", text="Role")
        self.tree.heading("Details", text="Transaction Details")

        self.tree.column("ID", width=50, minwidth=40, stretch=False, anchor="center")
        self.tree.column("Timestamp", width=145, minwidth=120, stretch=False, anchor="center")
        self.tree.column("Action", width=160, minwidth=130, stretch=False, anchor="w")
        self.tree.column("Role", width=85, minwidth=70, stretch=False, anchor="center")
        self.tree.column("Details", width=340, minwidth=220, stretch=True, anchor="w")

        self.tree_scroll_y = ttk.Scrollbar(self.tree_container, orient="vertical", command=self.tree.yview)
        self.tree_scroll_x = ttk.Scrollbar(self.tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.tree_scroll_y.set, xscrollcommand=self.tree_scroll_x.set)

        self.tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bottom Bar
        self.bottom_bar = ctk.CTkFrame(self.card, fg_color="transparent")
        self.bottom_bar.pack(fill=tk.X, padx=16, pady=(0, 14))

        self.lbl_log_count = ctk.CTkLabel(self.bottom_bar, text="Showing 0 events", font=("SF Pro Display", 11), text_color="#64748B")
        self.lbl_log_count.pack(side=tk.LEFT)

        self.btn_close = AccessibleButton(self.bottom_bar, text="Close", command=self.destroy, corner_radius=10)
        self.btn_close.pack(side=tk.RIGHT)

        self.bind("<Escape>", lambda e: self.destroy())

    def load_logs(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        logs = self.db.get_recent_audit_logs(limit=100)
        q = self.ent_search.get().strip().lower()

        matched = 0
        for entry in logs:
            log_id, ts, act, det, role = entry
            line = f"{act} {det} {role}".lower()
            if q and q not in line:
                continue

            tag = "admin" if role.lower() == "admin" else "faculty"
            self.tree.insert("", tk.END, values=(log_id, ts, act, role, det), tags=(tag,))
            matched += 1

        self.lbl_log_count.configure(text=f"Showing {matched} logged events")

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
        self.lbl_filter.configure(text_color=fg)
        self.lbl_log_count.configure(text_color=theme["fg_muted"])
        self.tree_container.configure(bg=card_bg)

        self.ent_search.apply_theme(theme, font_cfg)

        pad_x = font_cfg["btn_pad_x"]
        pad_y = font_cfg["btn_pad_y"]

        self.btn_refresh.apply_style(
            bg=theme["btn_secondary_bg"],
            fg=theme["btn_secondary_fg"],
            font=font_cfg.get("btn_font", ("SF Pro Display", font_cfg["body"])),
            focus_ring=theme["focus_ring"],
            border_color=theme["btn_secondary_border"],
            padx=pad_x - 2,
            pady=pad_y - 2
        )
        self.btn_close.apply_style(
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

        self.tree.tag_configure("admin", foreground=theme["status_warning"])
        self.tree.tag_configure("faculty", foreground=theme["status_present"])
