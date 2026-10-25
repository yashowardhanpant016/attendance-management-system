"""
Institutional Student Attendance Report Card Generator (PDF Exporter).
Feature 5: Generates formal, printable institutional report cards using ReportLab.
Includes institutional header, student information box, metric statistics,
exam eligibility status, shortfall consecutive classes calculator, and history.
"""

import os
from datetime import datetime
import math

from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def calculate_shortfall(present: int, total: int, target: float = 0.75) -> int:
    """Formula: If P/T < 0.75, Required Classes = ceil((0.75 * T - P) / 0.25)."""
    if total <= 0:
        return 0
    rate = present / total
    if rate >= target:
        return 0
    return max(0, math.ceil((target * total - present) / (1.0 - target)))


def generate_student_report_card(student_info: dict, attendance_stats: dict, history_records: list, output_filepath: str) -> bool:
    """
    Generates a professional institutional PDF report card for a student.
    
    Args:
        student_info: dict with 'roll_no', 'name', 'section'
        attendance_stats: dict with 'total', 'present', 'absent', 'late', 'percentage'
        history_records: list of (date, status) tuples
        output_filepath: path to save the generated PDF file
    
    Returns:
        True if generation succeeded, False otherwise.
    """
    try:
        doc = SimpleDocTemplate(
            output_filepath,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()

        # Custom Styles
        style_inst_title = ParagraphStyle(
            "InstTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            alignment=1, # Center
            textColor=colors.HexColor("#0F172A")
        )
        style_sub_title = ParagraphStyle(
            "SubTitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            alignment=1,
            textColor=colors.HexColor("#475569")
        )
        style_report_type = ParagraphStyle(
            "ReportType",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            alignment=1,
            textColor=colors.HexColor("#2563EB")
        )
        style_section_heading = ParagraphStyle(
            "SecHeading",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#0F172A")
        )
        style_body = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#1E293B")
        )
        style_body_bold = ParagraphStyle(
            "BodyBold",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#0F172A")
        )
        style_alert_eligible = ParagraphStyle(
            "AlertEligible",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=15,
            alignment=1,
            textColor=colors.HexColor("#15803D")
        )
        style_alert_shortfall = ParagraphStyle(
            "AlertShortfall",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=15,
            alignment=1,
            textColor=colors.HexColor("#B91C1C")
        )

        story = []

        # 1. Institutional Header
        story.append(Paragraph("BBAT104: FUNDAMENTALS OF TOTAL QUALITY MANAGEMENT", style_inst_title))
        story.append(Paragraph("Department of Computer Science & Engineering • BTech Submission Edition", style_sub_title))
        story.append(Spacer(1, 4))
        story.append(Paragraph("OFFICIAL STUDENT ATTENDANCE & QUALITY AUDIT REPORT CARD", style_report_type))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563EB"), spaceBefore=1, spaceAfter=12))

        # 2. Student Metadata Box
        if isinstance(student_info, (tuple, list)):
            roll = str(student_info[0]) if len(student_info) > 0 else "N/A"
            name = str(student_info[1]) if len(student_info) > 1 else "N/A"
            sec = str(student_info[2]) if len(student_info) > 2 else "N/A"
        elif isinstance(student_info, dict):
            roll = str(student_info.get("roll_no", "N/A"))
            name = str(student_info.get("name", "N/A"))
            sec = str(student_info.get("section", "N/A"))
        else:
            roll = str(student_info)
            name = "N/A"
            sec = "N/A"

        gen_date = datetime.now().strftime("%B %d, %Y (%H:%M)")

        meta_data = [
            [
                Paragraph("<b>Student Name:</b>", style_body),
                Paragraph(name, style_body_bold),
                Paragraph("<b>Academic Roll No:</b>", style_body),
                Paragraph(roll, style_body_bold)
            ],
            [
                Paragraph("<b>Course Section:</b>", style_body),
                Paragraph(sec, style_body_bold),
                Paragraph("<b>Audit Date:</b>", style_body),
                Paragraph(gen_date, style_body)
            ]
        ]
        meta_table = Table(meta_data, colWidths=[100, 165, 120, 145])
        meta_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 14))

        # 3. Overall Metric Statistics
        story.append(Paragraph("CUMULATIVE ATTENDANCE METRICS", style_section_heading))
        story.append(Spacer(1, 6))

        if isinstance(attendance_stats, dict):
            total = attendance_stats.get("total", 0)
            present = attendance_stats.get("present", 0)
            absent = attendance_stats.get("absent", 0)
            late = attendance_stats.get("late", 0)
            pct = attendance_stats.get("percentage", 0.0)
        else:
            total = int(attendance_stats[0]) if len(attendance_stats) > 0 else 0
            present = int(attendance_stats[1]) if len(attendance_stats) > 1 else 0
            absent = int(attendance_stats[2]) if len(attendance_stats) > 2 else 0
            late = int(attendance_stats[3]) if len(attendance_stats) > 3 else 0
            pct = float(attendance_stats[4]) if len(attendance_stats) > 4 else 0.0

        shortfall = calculate_shortfall(present, total, 0.75)
        is_eligible = (pct >= 75.0)

        stats_data = [
            ["Total Sessions", "Present", "Absent", "Late", "Final Rate (%)", "75% Threshold Status"],
            [
                str(total),
                str(present),
                str(absent),
                str(late),
                f"{pct:.1f}%",
                "MET (>= 75%)" if is_eligible else f"SHORTFALL (-{shortfall} Classes)"
            ]
        ]
        stats_table = Table(stats_data, colWidths=[85, 80, 80, 75, 95, 115])
        stats_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#FFFFFF")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#FFFFFF")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 1), (-1, 1), 10),
            ("TEXTCOLOR", (4, 1), (4, 1), colors.HexColor("#2563EB")),
            ("TEXTCOLOR", (5, 1), (5, 1), colors.HexColor("#15803D") if is_eligible else colors.HexColor("#B91C1C")),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 12))

        # 4. Eligibility & Shortfall Alert Banner
        if is_eligible:
            banner_bg = colors.HexColor("#DCFCE7")
            banner_border = colors.HexColor("#86EFAC")
            banner_text = (
                "<b>ELIGIBILITY STATUS: ELIGIBLE FOR SEMESTER EXAMINATIONS</b><br/>"
                f"Student '{name}' has fulfilled the institutional minimum attendance requirement with an aggregate of <b>{pct:.1f}%</b>."
            )
            banner_p = Paragraph(banner_text, style_alert_eligible)
        else:
            banner_bg = colors.HexColor("#FEE2E2")
            banner_border = colors.HexColor("#FCA5A5")
            banner_text = (
                "<b>ELIGIBILITY STATUS: SHORTFALL NOTICE ISSUED (&lt; 75% THRESHOLD)</b><br/>"
                f"Current Attendance: <b>{pct:.1f}%</b>. The student needs <b>{shortfall} more consecutive classes</b> "
                "to attain exam eligibility [Formula: ceil((0.75 * T - P) / 0.25)]."
            )
            banner_p = Paragraph(banner_text, style_alert_shortfall)

        alert_table = Table([[banner_p]], colWidths=[530])
        alert_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), banner_bg),
            ("BOX", (0, 0), (-1, -1), 1, banner_border),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 14),
            ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ]))
        story.append(alert_table)
        story.append(Spacer(1, 14))

        # 5. Recent Attendance Log Table (up to 12 recent sessions)
        story.append(Paragraph("RECENT CLASS ATTENDANCE HISTORY (AUDIT TRAIL)", style_section_heading))
        story.append(Spacer(1, 6))

        recent_records = history_records[:12] if history_records else []
        log_rows = [["Session Date", "Status Logged", "Audit Remark"]]

        if not recent_records:
            log_rows.append(["No records", "Unmarked", "No historical logs recorded"])
        else:
            for rec in recent_records:
                d_val = rec[0] if isinstance(rec, (tuple, list)) else rec.get("date", "N/A")
                s_val = rec[1] if isinstance(rec, (tuple, list)) else rec.get("status", "N/A")
                if s_val == "Present":
                    rem = "Present in lecture"
                elif s_val == "Absent":
                    rem = "Absent from session"
                elif s_val == "Late":
                    rem = "Late arrival recorded"
                else:
                    rem = "Unmarked"
                log_rows.append([d_val, s_val, rem])

        log_table = Table(log_rows, colWidths=[150, 150, 230])
        log_table_style = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("ALIGN", (0, 0), (1, -1), "CENTER"),
        ]

        # Color status column
        for row_idx, r in enumerate(log_rows[1:], start=1):
            st = r[1]
            if st == "Present":
                log_table_style.append(("TEXTCOLOR", (1, row_idx), (1, row_idx), colors.HexColor("#15803D")))
            elif st == "Absent":
                log_table_style.append(("TEXTCOLOR", (1, row_idx), (1, row_idx), colors.HexColor("#B91C1C")))
            elif st == "Late":
                log_table_style.append(("TEXTCOLOR", (1, row_idx), (1, row_idx), colors.HexColor("#92400E")))

        log_table.setStyle(TableStyle(log_table_style))
        story.append(log_table)
        story.append(Spacer(1, 24))

        # 6. Official Institutional Signature Block
        sig_data = [
            [
                Paragraph("<b>Verified By:</b>", style_body),
                "",
                Paragraph("<b>Approved By:</b>", style_body)
            ],
            [
                Spacer(1, 25),
                "",
                Spacer(1, 25)
            ],
            [
                Paragraph("__________________________<br/>Faculty In-Charge (CSE-B)", style_body),
                "",
                Paragraph("__________________________<br/>Head of Department (CSE)", style_body)
            ]
        ]
        sig_table = Table(sig_data, colWidths=[240, 50, 240])
        sig_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(sig_table)

        doc.build(story)
        return True
    except Exception as e:
        print(f"Error generating PDF report card: {e}")
        return False
