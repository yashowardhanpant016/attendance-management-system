"""
BBAT104 Theme Configuration Module
Supports: Light Mode (Modern SaaS EduAttend), Dark Mode (Slate), High Contrast (WCAG 2.1 AAA)
Quality Goal: Q12 - Improve Accessibility
Provides full dual-compatibility for modern tokens and legacy view keys.
"""

THEMES = {
    "light": {
        "name": "Light Mode",
        # Modern SaaS tokens
        "canvas_bg": "#F8FAFC",
        "card_bg": "#FFFFFF",
        "card_border": "#E2E8F0",
        "card_border_width": 1,
        "text_primary": "#0F172A",
        "text_secondary": "#64748B",
        "text_muted": "#94A3B8",

        # Sidebar
        "sidebar_bg": "#0F172A",
        "sidebar_text": "#94A3B8",
        "sidebar_active_bg": "#2563EB",
        "sidebar_active_text": "#FFFFFF",
        "sidebar_hover_bg": "#1E293B",

        # Form Controls
        "entry_bg": "#F8FAFC",
        "entry_border": "#CBD5E1",
        "entry_text": "#0F172A",
        "entry_focus_border": "#3B82F6",

        # Action Buttons
        "btn_primary_bg": "#2563EB",
        "btn_primary_hover": "#1D4ED8",
        "btn_primary_text": "#FFFFFF",
        "btn_secondary_bg": "#F1F5F9",
        "btn_secondary_hover": "#E2E8F0",
        "btn_secondary_text": "#334155",
        "btn_danger_bg": "#FEE2E2",
        "btn_danger_hover": "#FCA5A5",
        "btn_danger_text": "#991B1B",

        # Table & Treeview Styling
        "table_bg": "#FFFFFF",
        "table_alt_bg": "#F8FAFC",
        "table_text": "#1E293B",
        "table_header_bg": "#F1F5F9",
        "table_header_text": "#475569",
        "table_select_bg": "#EFF6FF",
        "table_select_text": "#1D4ED8",

        # Badges & Status Pills
        "pill_present_bg": "#DCFCE7",
        "pill_present_text": "#166534",
        "pill_absent_bg": "#FEE2E2",
        "pill_absent_text": "#991B1B",
        "pill_warning_bg": "#FEF3C7",
        "pill_warning_text": "#92400E",

        # Q12 Focus Ring
        "focus_ring": "#2563EB",

        # Legacy Compatibility Keys
        "bg": "#F8FAFC",
        "fg": "#0F172A",
        "fg_muted": "#64748B",
        "header_bg": "#FFFFFF",
        "header_fg": "#0F172A",
        "sidebar_fg": "#94A3B8",
        "sidebar_active_fg": "#FFFFFF",
        "btn_primary_fg": "#FFFFFF",
        "btn_secondary_fg": "#334155",
        "btn_secondary_border": "#CBD5E1",
        "btn_danger_fg": "#991B1B",

        "status_present": "#10B981",
        "status_present_bg": "#DCFCE7",
        "status_present_fg": "#166534",
        "status_absent": "#EF4444",
        "status_absent_bg": "#FEE2E2",
        "status_absent_fg": "#991B1B",
        "status_late": "#F59E0B",
        "status_late_bg": "#FEF3C7",
        "status_late_fg": "#92400E",
        "status_unmarked": "#94A3B8",
        "status_unmarked_bg": "#F1F5F9",
        "status_unmarked_fg": "#64748B",
        "status_warning": "#F59E0B",
        "status_critical": "#EF4444",

        "role_admin_bg": "#FEF3C7",
        "role_admin_fg": "#92400E",
        "role_faculty_bg": "#EFF6FF",
        "role_faculty_fg": "#1D4ED8",

        "cal_cell_bg": "#FFFFFF",
        "cal_cell_border": "#E2E8F0",
        "cal_present_bg": "#DCFCE7",
        "cal_present_fg": "#166534",
        "cal_absent_bg": "#FEE2E2",
        "cal_absent_fg": "#991B1B",
        "cal_late_bg": "#FEF3C7",
        "cal_late_fg": "#92400E",
        "cal_neutral_bg": "#F8FAFC",
        "cal_neutral_fg": "#94A3B8",

        "tree_bg": "#FFFFFF",
        "tree_fg": "#1E293B",
        "tree_head_bg": "#F1F5F9",
        "tree_head_fg": "#475569",
        "select_bg": "#EFF6FF",
        "select_fg": "#1D4ED8",

        "chart_bg": "#FFFFFF",
        "chart_fg": "#0F172A",
        "chart_grid": "#E2E8F0",
        "chart_line": "#2563EB",

        "is_high_contrast": False,
    },

    "dark": {
        "name": "Dark Mode",
        # Modern Slate tokens
        "canvas_bg": "#0F172A",
        "card_bg": "#1E293B",
        "card_border": "#334155",
        "card_border_width": 1,
        "text_primary": "#F8FAFC",
        "text_secondary": "#94A3B8",
        "text_muted": "#64748B",

        # Sidebar
        "sidebar_bg": "#0B0F19",
        "sidebar_text": "#CBD5E1",
        "sidebar_active_bg": "#2563EB",
        "sidebar_active_text": "#FFFFFF",
        "sidebar_hover_bg": "#1E293B",

        # Form Controls
        "entry_bg": "#0F172A",
        "entry_border": "#334155",
        "entry_text": "#F8FAFC",
        "entry_focus_border": "#60A5FA",

        # Action Buttons
        "btn_primary_bg": "#2563EB",
        "btn_primary_hover": "#3B82F6",
        "btn_primary_text": "#FFFFFF",
        "btn_secondary_bg": "#334155",
        "btn_secondary_hover": "#475569",
        "btn_secondary_text": "#F8FAFC",
        "btn_danger_bg": "#7F1D1D",
        "btn_danger_hover": "#991B1B",
        "btn_danger_text": "#FEE2E2",

        # Table & Treeview Styling
        "table_bg": "#1E293B",
        "table_alt_bg": "#162032",
        "table_text": "#F8FAFC",
        "table_header_bg": "#0F172A",
        "table_header_text": "#94A3B8",
        "table_select_bg": "#2563EB",
        "table_select_text": "#FFFFFF",

        # Badges & Status Pills
        "pill_present_bg": "#064E3B",
        "pill_present_text": "#6EE7B7",
        "pill_absent_bg": "#7F1D1D",
        "pill_absent_text": "#FCA5A5",
        "pill_warning_bg": "#78350F",
        "pill_warning_text": "#FCD34D",

        # Q12 Focus Ring
        "focus_ring": "#60A5FA",

        # Legacy Compatibility Keys
        "bg": "#0F172A",
        "fg": "#F8FAFC",
        "fg_muted": "#94A3B8",
        "header_bg": "#1E293B",
        "header_fg": "#F8FAFC",
        "sidebar_fg": "#CBD5E1",
        "sidebar_active_fg": "#FFFFFF",
        "btn_primary_fg": "#FFFFFF",
        "btn_secondary_fg": "#F8FAFC",
        "btn_secondary_border": "#475569",
        "btn_danger_fg": "#FEE2E2",

        "status_present": "#34D399",
        "status_present_bg": "#064E3B",
        "status_present_fg": "#6EE7B7",
        "status_absent": "#F87171",
        "status_absent_bg": "#7F1D1D",
        "status_absent_fg": "#FCA5A5",
        "status_late": "#FBBF24",
        "status_late_bg": "#78350F",
        "status_late_fg": "#FCD34D",
        "status_unmarked": "#64748B",
        "status_unmarked_bg": "#1E293B",
        "status_unmarked_fg": "#94A3B8",
        "status_warning": "#FBBF24",
        "status_critical": "#F87171",

        "role_admin_bg": "#78350F",
        "role_admin_fg": "#FDE68A",
        "role_faculty_bg": "#1E3A8A",
        "role_faculty_fg": "#93C5FD",

        "cal_cell_bg": "#1E293B",
        "cal_cell_border": "#334155",
        "cal_present_bg": "#064E3B",
        "cal_present_fg": "#6EE7B7",
        "cal_absent_bg": "#7F1D1D",
        "cal_absent_fg": "#FCA5A5",
        "cal_late_bg": "#78350F",
        "cal_late_fg": "#FCD34D",
        "cal_neutral_bg": "#0F172A",
        "cal_neutral_fg": "#64748B",

        "tree_bg": "#1E293B",
        "tree_fg": "#F8FAFC",
        "tree_head_bg": "#0F172A",
        "tree_head_fg": "#94A3B8",
        "select_bg": "#2563EB",
        "select_fg": "#FFFFFF",

        "chart_bg": "#1E293B",
        "chart_plot_bg": "#1E293B",
        "chart_fg": "#F8FAFC",
        "chart_text": "#F8FAFC",
        "chart_grid": "#334155",
        "chart_line": "#06B6D4",
        "chart_accent": "#06B6D4",
        "chart_fill": "#06B6D4",

        "is_high_contrast": False,
    },

    "high_contrast": {
        "name": "High Contrast (WCAG AAA)",
        # High Contrast tokens
        "canvas_bg": "#000000",
        "card_bg": "#000000",
        "card_border": "#FFFF00",
        "card_border_width": 2,
        "text_primary": "#FFFF00",
        "text_secondary": "#FFFFFF",
        "text_muted": "#FFFF00",

        # Sidebar
        "sidebar_bg": "#000000",
        "sidebar_text": "#FFFFFF",
        "sidebar_active_bg": "#FFFF00",
        "sidebar_active_text": "#000000",
        "sidebar_hover_bg": "#222222",

        # Form Controls
        "entry_bg": "#000000",
        "entry_border": "#FFFF00",
        "entry_text": "#FFFF00",
        "entry_focus_border": "#FFFFFF",

        # Action Buttons
        "btn_primary_bg": "#FFFF00",
        "btn_primary_hover": "#FFFFFF",
        "btn_primary_text": "#000000",
        "btn_secondary_bg": "#000000",
        "btn_secondary_hover": "#1A1A1A",
        "btn_secondary_text": "#FFFFFF",
        "btn_danger_bg": "#000000",
        "btn_danger_hover": "#1A1A1A",
        "btn_danger_text": "#FF5555",

        # Table & Treeview Styling
        "table_bg": "#000000",
        "table_alt_bg": "#0A0A0A",
        "table_text": "#FFFF00",
        "table_header_bg": "#000000",
        "table_header_text": "#FFFFFF",
        "table_select_bg": "#FFFFFF",
        "table_select_text": "#000000",

        # Badges & Status Pills
        "pill_present_bg": "#000000",
        "pill_present_text": "#00FF66",
        "pill_absent_bg": "#000000",
        "pill_absent_text": "#FF5555",
        "pill_warning_bg": "#000000",
        "pill_warning_text": "#FFFF00",

        # Q12 Focus Ring
        "focus_ring": "#FFFFFF",

        # Legacy Compatibility Keys
        "bg": "#000000",
        "fg": "#FFFF00",
        "fg_muted": "#FFFF00",
        "header_bg": "#000000",
        "header_fg": "#FFFF00",
        "sidebar_fg": "#FFFF00",
        "sidebar_active_fg": "#000000",
        "btn_primary_fg": "#000000",
        "btn_secondary_fg": "#FFFFFF",
        "btn_secondary_border": "#FFFF00",
        "btn_danger_fg": "#FF5555",

        "status_present": "#00FF66",
        "status_present_bg": "#000000",
        "status_present_fg": "#00FF66",
        "status_absent": "#FF3333",
        "status_absent_bg": "#000000",
        "status_absent_fg": "#FF5555",
        "status_late": "#FFAA00",
        "status_late_bg": "#000000",
        "status_late_fg": "#FFFF00",
        "status_unmarked": "#FFFF00",
        "status_unmarked_bg": "#000000",
        "status_unmarked_fg": "#FFFF00",
        "status_warning": "#FFFF00",
        "status_critical": "#FF3333",

        "role_admin_bg": "#000000",
        "role_admin_fg": "#FFFF00",
        "role_faculty_bg": "#000000",
        "role_faculty_fg": "#FFFFFF",

        "cal_cell_bg": "#000000",
        "cal_cell_border": "#FFFF00",
        "cal_present_bg": "#000000",
        "cal_present_fg": "#00FF66",
        "cal_absent_bg": "#000000",
        "cal_absent_fg": "#FF5555",
        "cal_late_bg": "#000000",
        "cal_late_fg": "#FFFF00",
        "cal_neutral_bg": "#000000",
        "cal_neutral_fg": "#FFFF00",

        "tree_bg": "#000000",
        "tree_fg": "#FFFF00",
        "tree_head_bg": "#000000",
        "tree_head_fg": "#FFFFFF",
        "select_bg": "#FFFFFF",
        "select_fg": "#000000",

        "chart_bg": "#000000",
        "chart_fg": "#FFFF00",
        "chart_grid": "#333333",
        "chart_line": "#FFFF00",

        "is_high_contrast": True,
    }
}

FONT_SIZES = {
    "normal": {
        "family": "SF Pro Display",
        "caption": 10,
        "body": 11,
        "body_bold": ("SF Pro Display", 11, "bold"),
        "subheading": 13,
        "title": 13,
        "title_bold": ("SF Pro Display", 13, "bold"),
        "header": 16,
        "header_bold": ("SF Pro Display", 16, "bold"),
        "app_title": ("SF Pro Display", 15, "bold"),
        "page_title": ("SF Pro Display", 15, "bold"),
        "section_title": ("SF Pro Display", 13, "bold"),
        "form_label": ("SF Pro Display", 11, "bold"),
        "input_font": ("SF Pro Display", 11),
        "btn_font": ("SF Pro Display", 11),
        "btn_bold": ("SF Pro Display", 11, "bold"),
        "tree_head": 12,
        "tree_head_font": ("SF Pro Display", 12, "bold"),
        "tree_row": 36,
        "tree_row_font": ("SF Pro Display", 11),
        "status_font": ("SF Pro Display", 10),
        "badge": 10,
        "badge_font": ("SF Pro Display", 10, "bold"),
        "kpi_num": 24,
        "kpi_num_bold": ("SF Pro Display", 24, "bold"),
        "row_height": 38,
        "btn_pad_x": 10,
        "btn_pad_y": 6,
        "sidebar_width": 230,
        "col_widths": {"Roll": 120, "Name": 220, "Section": 100, "Status": 130, "Rate": 110}
    },
    "large": {
        "family": "SF Pro Display",
        "caption": 12,
        "body": 13,
        "body_bold": ("SF Pro Display", 13, "bold"),
        "subheading": 15,
        "title": 15,
        "title_bold": ("SF Pro Display", 15, "bold"),
        "header": 18,
        "header_bold": ("SF Pro Display", 18, "bold"),
        "app_title": ("SF Pro Display", 17, "bold"),
        "page_title": ("SF Pro Display", 17, "bold"),
        "section_title": ("SF Pro Display", 15, "bold"),
        "form_label": ("SF Pro Display", 13, "bold"),
        "input_font": ("SF Pro Display", 13),
        "btn_font": ("SF Pro Display", 13),
        "btn_bold": ("SF Pro Display", 13, "bold"),
        "tree_head": 14,
        "tree_head_font": ("SF Pro Display", 14, "bold"),
        "tree_row": 42,
        "tree_row_font": ("SF Pro Display", 13),
        "status_font": ("SF Pro Display", 12),
        "badge": 11,
        "badge_font": ("SF Pro Display", 11, "bold"),
        "kpi_num": 28,
        "kpi_num_bold": ("SF Pro Display", 28, "bold"),
        "row_height": 46,
        "btn_pad_x": 12,
        "btn_pad_y": 8,
        "sidebar_width": 265,
        "col_widths": {"Roll": 140, "Name": 260, "Section": 120, "Status": 150, "Rate": 130}
    },
    "xlarge": {
        "family": "SF Pro Display",
        "caption": 14,
        "body": 15,
        "body_bold": ("SF Pro Display", 15, "bold"),
        "subheading": 17,
        "title": 18,
        "title_bold": ("SF Pro Display", 18, "bold"),
        "header": 20,
        "header_bold": ("SF Pro Display", 20, "bold"),
        "app_title": ("SF Pro Display", 19, "bold"),
        "page_title": ("SF Pro Display", 19, "bold"),
        "section_title": ("SF Pro Display", 17, "bold"),
        "form_label": ("SF Pro Display", 15, "bold"),
        "input_font": ("SF Pro Display", 15),
        "btn_font": ("SF Pro Display", 14),
        "btn_bold": ("SF Pro Display", 14, "bold"),
        "tree_head": 15,
        "tree_head_font": ("SF Pro Display", 15, "bold"),
        "tree_row": 48,
        "tree_row_font": ("SF Pro Display", 15),
        "status_font": ("SF Pro Display", 13),
        "badge": 12,
        "badge_font": ("SF Pro Display", 12, "bold"),
        "kpi_num": 32,
        "kpi_num_bold": ("SF Pro Display", 32, "bold"),
        "row_height": 54,
        "btn_pad_x": 14,
        "btn_pad_y": 9,
        "sidebar_width": 295,
        "col_widths": {"Roll": 160, "Name": 290, "Section": 130, "Status": 160, "Rate": 140}
    }
}

def get_theme(theme_name_or_dict=None):
    """
    Safely retrieves the theme dictionary.
    Handles None, strings, or existing dictionaries without raising KeyError or TypeError.
    """
    if isinstance(theme_name_or_dict, dict):
        return theme_name_or_dict
    if isinstance(theme_name_or_dict, str):
        return THEMES.get(theme_name_or_dict, THEMES["light"])
    return THEMES["light"]

def get_fonts(scale_key_or_dict=None):
    """
    Safely retrieves the font configuration dictionary.
    Handles None, strings, or existing dictionaries without raising KeyError or TypeError.
    """
    if isinstance(scale_key_or_dict, dict):
        return scale_key_or_dict
    if isinstance(scale_key_or_dict, str):
        return FONT_SIZES.get(scale_key_or_dict, FONT_SIZES["normal"])
    return FONT_SIZES["normal"]

def get_treeview_rowheight(font_size=12):
    """Dynamically calculates balanced row height for treeview rows."""
    return max(32, int(font_size * 2.3))