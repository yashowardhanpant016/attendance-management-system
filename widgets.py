"""
BBAT104 Custom Modern Accessible Widgets
Built with CustomTkinter & Tkinter for a modern SaaS educational ERP dashboard.
Quality Goal: Q12 - Improve Accessibility (WCAG 2.1 AAA focus rings, scalable typography)
Exports:
  - ModernCard / CardFrame
  - ModernButton / AccessibleButton
  - ModernEntry / FocusRingEntry / AccessibleEntry
  - KPICard
  - AccessibleLabel
  - PillBadge
  - AutoScrollbar
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from theme import get_theme, get_fonts


def _filter_tk_kwargs(kwargs):
    """Filters out legacy Tkinter kwargs that CustomTkinter widgets do not accept."""
    tk_only_keys = [
        "relief", "bd", "highlightthickness", "highlightbackground",
        "highlightcolor", "takefocus", "cursor", "padx", "pady",
        "insertbackground", "selectbackground", "selectforeground",
        "focus_ring", "border_color"
    ]
    extracted = {}
    for k in tk_only_keys:
        if k in kwargs:
            extracted[k] = kwargs.pop(k)
    return extracted


class ModernCard(
    """Accessible container card supporting dynamic theme switching and borders."""
ctk.CTkFrame):
    """Floating Card container with rounded corners and adaptive borders."""
    def __init__(self, master, theme_key="light", corner_radius=14, **kwargs):
        self.theme = get_theme(theme_key)
        
        # Translate legacy kwargs
        if "bg" in kwargs:
            kwargs["fg_color"] = kwargs.pop("bg")
        if "bd" in kwargs:
            kwargs["border_width"] = kwargs.pop("bd")
        _filter_tk_kwargs(kwargs)

        super().__init__(
            master,
            corner_radius=corner_radius,
            fg_color=kwargs.pop("fg_color", self.theme.get("card_bg", "#FFFFFF")),
            border_width=kwargs.pop("border_width", self.theme.get("card_border_width", 1)),
            border_color=kwargs.pop("border_color", self.theme.get("card_border", "#E2E8F0")),
            **kwargs
        )

    def apply_theme(self, theme_or_key="light", font_scale_or_cfg="normal"):
        self.theme = get_theme(theme_or_key)
        self.configure(
            fg_color=self.theme.get("card_bg", "#FFFFFF"),
            border_width=self.theme.get("card_border_width", 1),
            border_color=self.theme.get("card_border", "#E2E8F0")
        )

    def configure(self, cnf=None, **kwargs):
        if cnf:
            kwargs.update(cnf)
        if "bg" in kwargs:
            kwargs["fg_color"] = kwargs.pop("bg")
        if "bd" in kwargs:
            kwargs["border_width"] = kwargs.pop("bd")
        _filter_tk_kwargs(kwargs)
        super().configure(**kwargs)


class ModernButton(ctk.CTkButton):
    """
    Modern action button supporting role styles, keyboard activation,
    and WCAG 2.1 AAA high-visibility focus ring navigation.
    """
    def __init__(self, master, text="", command=None, style="primary", theme_key="light",
                 font_scale="normal", corner_radius=8, height=36, **kwargs):
        self.theme = get_theme(theme_key)
        self.font_cfg = get_fonts(font_scale)
        self.style_type = style
        self.btn_command = command
        self.is_focused = False

        # Extract legacy kwargs
        legacy = _filter_tk_kwargs(kwargs)
        if "bg" in kwargs:
            kwargs["fg_color"] = kwargs.pop("bg")
        if "fg" in kwargs:
            kwargs["text_color"] = kwargs.pop("fg")

        self.normal_bg, self.hover_bg, self.normal_fg = self._resolve_colors()
        self.normal_border_color = legacy.get("border_color", self.theme.get("card_border", "#CBD5E1"))
        self.focus_ring_color = legacy.get("focus_ring", self.theme.get("focus_ring", "#2563EB"))
        self.normal_border_width = 1 if self.style_type == "secondary" else 0

        fg_col = kwargs.pop("fg_color", self.normal_bg)
        txt_col = kwargs.pop("text_color", self.normal_fg)
        hov_col = kwargs.pop("hover_color", self.hover_bg)

        super().__init__(
            master,
            text=text,
            command=self._on_activate,
            height=height,
            corner_radius=corner_radius,
            fg_color=fg_col,
            hover_color=hov_col,
            text_color=txt_col,
            border_width=self.normal_border_width,
            border_color=self.normal_border_color,
            font=("SF Pro Display", self.font_cfg.get("body", 11), "bold"),
            **kwargs
        )

        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        self.bind("<Return>", lambda e: self._on_activate())
        self.bind("<space>", lambda e: self._on_activate())

    def _on_activate(self):
        if self.cget("state") == "disabled":
            return
        if self.btn_command:
            self.btn_command()

    def _resolve_colors(self):
        if self.style_type == "primary":
            return (
                self.theme.get("btn_primary_bg", "#2563EB"),
                self.theme.get("btn_primary_hover", "#1D4ED8"),
                self.theme.get("btn_primary_text", self.theme.get("btn_primary_fg", "#FFFFFF"))
            )
        elif self.style_type == "danger":
            return (
                self.theme.get("btn_danger_bg", "#FEE2E2"),
                self.theme.get("btn_danger_hover", "#FCA5A5"),
                self.theme.get("btn_danger_text", self.theme.get("btn_danger_fg", "#991B1B"))
            )
        else:  # secondary / neutral
            return (
                self.theme.get("btn_secondary_bg", "#F1F5F9"),
                self.theme.get("btn_secondary_hover", "#E2E8F0"),
                self.theme.get("btn_secondary_text", self.theme.get("btn_secondary_fg", "#334155"))
            )

    def _on_focus_in(self, event=None):
        self.is_focused = True
        super().configure(border_color=self.focus_ring_color, border_width=2)

    def _on_focus_out(self, event=None):
        self.is_focused = False
        super().configure(border_color=self.normal_border_color, border_width=self.normal_border_width)

    def apply_style(self, bg=None, fg=None, font=None, focus_ring=None, border_color=None,
                    padx=None, pady=None, relief=None, bd=None, hover=None, **kwargs):
        """Dynamic styling hook matching legacy AccessibleButton callers."""
        if bg is not None:
            self.normal_bg = bg
        if fg is not None:
            self.normal_fg = fg
        if hover is not None:
            self.hover_bg = hover
        if focus_ring is not None:
            self.focus_ring_color = focus_ring
        if border_color is not None:
            self.normal_border_color = border_color if border_color != "transparent" else (bg if bg != "transparent" else "#1E293B")

        b_color = self.focus_ring_color if self.is_focused else self.normal_border_color
        if b_color == "transparent":
            b_color = "#1E293B"

        updates = {
            "fg_color": self.normal_bg,
            "text_color": self.normal_fg,
            "border_color": b_color,
            "border_width": 2 if self.is_focused else (1 if (border_color and border_color != "transparent" and bd != 0) else 0)
        }
        if font is not None:
            updates["font"] = font
        if hover is not None:
            updates["hover_color"] = hover
        if "corner_radius" in kwargs:
            updates["corner_radius"] = kwargs["corner_radius"]

        super().configure(**updates)

    def apply_theme(self, theme_or_key="light", font_scale_or_cfg="normal"):
        self.theme = get_theme(theme_or_key)
        self.font_cfg = get_fonts(font_scale_or_cfg)
        self.focus_ring_color = self.theme.get("focus_ring", "#2563EB")
        bg, hover, fg = self._resolve_colors()
        self.normal_bg = bg
        self.hover_bg = hover
        self.normal_fg = fg
        self.normal_border_color = self.theme.get("btn_secondary_border", self.theme.get("card_border", "#CBD5E1"))
        self.normal_border_width = 1 if self.style_type == "secondary" else 0

        super().configure(
            fg_color=bg,
            hover_color=hover,
            text_color=fg,
            border_color=self.focus_ring_color if self.is_focused else self.normal_border_color,
            border_width=2 if self.is_focused else self.normal_border_width,
            font=("SF Pro Display", self.font_cfg.get("body", 11), "bold")
        )

    def configure(self, cnf=None, **kwargs):
        if cnf:
            kwargs.update(cnf)
        if "command" in kwargs:
            self.btn_command = kwargs.pop("command")
        if "bg" in kwargs:
            kwargs["fg_color"] = kwargs.pop("bg")
            self.normal_bg = kwargs["fg_color"]
        if "fg" in kwargs:
            kwargs["text_color"] = kwargs.pop("fg")
            self.normal_fg = kwargs["text_color"]
        if "border_color" in kwargs:
            self.normal_border_color = kwargs.pop("border_color")
            kwargs["border_color"] = self.normal_border_color
        if "focus_ring" in kwargs:
            self.focus_ring_color = kwargs.pop("focus_ring")
        _filter_tk_kwargs(kwargs)
        super().configure(**kwargs)


class ModernEntry(ctk.CTkEntry):
    """Modern rounded text entry with focus border highlights."""
    def __init__(self, master, theme_key="light", font_scale="normal", placeholder_text="", **kwargs):
        self.theme = get_theme(theme_key)
        self.font_cfg = get_fonts(font_scale)
        self.is_focused = False

        # Scale width if character units passed
        if "width" in kwargs and kwargs["width"] is not None:
            w = kwargs["width"]
            if w <= 35:
                kwargs["width"] = max(80, int(w * 10))

        legacy = _filter_tk_kwargs(kwargs)
        self.normal_border = legacy.get("border_color", self.theme.get("entry_border", self.theme.get("card_border", "#CBD5E1")))
        self.focus_ring = legacy.get("focus_ring", self.theme.get("entry_focus_border", self.theme.get("focus_ring", "#3B82F6")))

        super().__init__(
            master,
            height=36,
            corner_radius=8,
            fg_color=self.theme.get("entry_bg", self.theme.get("card_bg", "#F8FAFC")),
            text_color=self.theme.get("entry_text", self.theme.get("fg", "#0F172A")),
            placeholder_text_color=self.theme.get("text_muted", self.theme.get("fg_muted", "#94A3B8")),
            border_width=1,
            border_color=self.normal_border,
            placeholder_text=placeholder_text,
            font=("SF Pro Display", self.font_cfg.get("body", 11)),
            **kwargs
        )
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

    def _on_focus_in(self, event=None):
        self.is_focused = True
        self.configure(border_color=self.focus_ring, border_width=2)

    def _on_focus_out(self, event=None):
        self.is_focused = False
        self.configure(border_color=self.normal_border, border_width=1)

    def apply_theme(self, theme_or_key="light", font_scale_or_cfg="normal"):
        self.theme = get_theme(theme_or_key)
        self.font_cfg = get_fonts(font_scale_or_cfg)
        self.normal_border = self.theme.get("entry_border", self.theme.get("card_border", "#CBD5E1"))
        self.focus_ring = self.theme.get("entry_focus_border", self.theme.get("focus_ring", "#3B82F6"))

        self.configure(
            fg_color=self.theme.get("entry_bg", self.theme.get("card_bg", "#F8FAFC")),
            text_color=self.theme.get("entry_text", self.theme.get("fg", "#0F172A")),
            border_color=self.focus_ring if self.is_focused else self.normal_border,
            placeholder_text_color=self.theme.get("text_muted", self.theme.get("fg_muted", "#94A3B8")),
            font=("SF Pro Display", self.font_cfg.get("body", 11))
        )

    def configure(self, cnf=None, **kwargs):
        if cnf:
            kwargs.update(cnf)
        if "bg" in kwargs:
            kwargs["fg_color"] = kwargs.pop("bg")
        if "fg" in kwargs:
            kwargs["text_color"] = kwargs.pop("fg")
        _filter_tk_kwargs(kwargs)
        super().configure(**kwargs)


class KPICard(ctk.CTkFrame):
    """
    Summary KPI Card Widget for displaying executive metrics:
    Features:
      - Floating card container with rounded corners
      - Top 6px vibrant accent bar indicator
      - Category title label
      - Prominent 32pt bold metric number with custom color support
      - Optional subtitle description
    """
    def __init__(self, master, title="Metric", value="0", subtitle="", accent_color="#2563EB",
                 value_color=None, theme_key="light", corner_radius=14, **kwargs):
        self.theme = get_theme(theme_key)
        self.title_text = title
        self.value_text = str(value)
        self.subtitle_text = subtitle
        self.accent_color = accent_color
        self.value_color = value_color

        # Strip legacy Tk Frame kwargs
        if "bg" in kwargs:
            kwargs["fg_color"] = kwargs.pop("bg")
        _filter_tk_kwargs(kwargs)

        super().__init__(
            master,
            corner_radius=corner_radius,
            fg_color=self.theme.get("card_bg", "#FFFFFF"),
            border_width=self.theme.get("card_border_width", 1),
            border_color=self.theme.get("card_border", "#E2E8F0"),
            **kwargs
        )

        # Top Accent Bar (6px height with vibrant glow)
        self.accent_bar = ctk.CTkFrame(self, height=6, corner_radius=3, fg_color=self.accent_color)
        self.accent_bar.pack(fill="x", padx=14, pady=(10, 8))

        # Title Label
        self.lbl_title = ctk.CTkLabel(
            self,
            text=self.title_text,
            font=("SF Pro Display", 11, "bold"),
            text_color=self.theme.get("text_secondary", self.theme.get("fg_muted", "#64748B")),
            anchor="w"
        )
        self.lbl_title.pack(fill="x", padx=16, pady=(0, 2))

        # Prominent Value Label (32pt bold)
        initial_val_color = self.value_color if self.value_color else self.theme.get("text_primary", self.theme.get("fg", "#0F172A"))
        self.lbl_val = ctk.CTkLabel(
            self,
            text=self.value_text,
            font=("SF Pro Display", 32, "bold"),
            text_color=initial_val_color,
            anchor="w"
        )
        self.lbl_val.pack(fill="x", padx=16, pady=(0, 8))

        # Optional Subtitle
        self.lbl_sub = ctk.CTkLabel(
            self,
            text=self.subtitle_text,
            font=("SF Pro Display", 10),
            text_color=self.theme.get("text_muted", self.theme.get("fg_muted", "#94A3B8")),
            anchor="w"
        )
        if self.subtitle_text:
            self.lbl_sub.pack(fill="x", padx=16, pady=(0, 10))

    def update_value(self, new_val, title=None, subtitle=None):
        """Dynamically updates the displayed value and optional labels."""
        self.value_text = str(new_val)
        self.lbl_val.configure(text=self.value_text)
        if title is not None:
            self.title_text = title
            self.lbl_title.configure(text=self.title_text)
        if subtitle is not None:
            self.subtitle_text = subtitle
            self.lbl_sub.configure(text=self.subtitle_text)
            if not self.lbl_sub.winfo_ismapped() and subtitle:
                self.lbl_sub.pack(fill="x", padx=16, pady=(0, 10))

    def apply_theme(self, theme_or_key="light", font_scale_or_cfg="normal"):
        self.theme = get_theme(theme_or_key)
        font_cfg = get_fonts(font_scale_or_cfg)

        card_bg = self.theme.get("card_bg", "#FFFFFF")
        card_border = self.theme.get("card_border", "#E2E8F0")
        border_w = self.theme.get("card_border_width", 1)

        super().configure(fg_color=card_bg, border_color=card_border, border_width=border_w)

        self.lbl_title.configure(
            text_color=self.theme.get("text_secondary", self.theme.get("fg_muted", "#64748B")),
            font=font_cfg.get("form_label", ("SF Pro Display", font_cfg.get("body", 11), "bold"))
        )

        # In High Contrast mode, respect WCAG AAA yellow, otherwise preserve distinct metric color
        is_hc = self.theme.get("is_high_contrast", False)
        if is_hc:
            val_col = "#FFFF00"
        elif self.value_color:
            val_col = self.value_color
        else:
            val_col = self.theme.get("text_primary", self.theme.get("fg", "#0F172A"))

        self.lbl_val.configure(
            text_color=val_col,
            font=("SF Pro Display", 32, "bold")
        )
        self.lbl_sub.configure(
            text_color=self.theme.get("text_muted", self.theme.get("fg_muted", "#94A3B8"))
        )


class AccessibleLabel(ctk.CTkLabel):
    """Accessible label widget with dynamic theme and font adaptation."""
    def __init__(self, master, text="", **kwargs):
        if "bg" in kwargs:
            kwargs["fg_color"] = kwargs.pop("bg")
        if "fg" in kwargs:
            kwargs["text_color"] = kwargs.pop("fg")
        _filter_tk_kwargs(kwargs)
        super().__init__(master, text=text, **kwargs)

    def apply_theme(self, theme_or_key="light", font_scale_or_cfg="normal"):
        theme = get_theme(theme_or_key)
        self.configure(text_color=theme.get("text_primary", theme.get("fg", "#0F172A")))


class PillBadge(ctk.CTkFrame):
    """Rounded Pill Status Badge (e.g. Present, Absent, Warning)."""
    def __init__(self, master, text="", bg="#DCFCE7", fg="#166534", corner_radius=10, **kwargs):
        super().__init__(master, fg_color=bg, corner_radius=corner_radius, **kwargs)
        self.lbl = ctk.CTkLabel(
            self,
            text=text,
            font=("SF Pro Display", 10, "bold"),
            text_color=fg
        )
        self.lbl.pack(padx=8, pady=2)

    def set_status(self, text, bg=None, fg=None):
        self.lbl.configure(text=text)
        if bg:
            self.configure(fg_color=bg)
        if fg:
            self.lbl.configure(text_color=fg)


class AutoScrollbar(ttk.Scrollbar):
    """Scrollbar that automatically conceals itself when content fits inside container."""
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.pack_forget()
        else:
            self.pack(side=tk.RIGHT, fill=tk.Y)
        super().set(lo, hi)


# =========================================================
# BACKWARD COMPATIBILITY ALIASES (Needed across app.py & views)
# =========================================================
CardFrame = ModernCard
AccessibleButton = ModernButton
FocusRingEntry = ModernEntry
AccessibleEntry = ModernEntry
# Accessibility helper for programmatic click dispatch
