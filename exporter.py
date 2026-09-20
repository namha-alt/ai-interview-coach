"""Export utilities for generating Markdown and PDF interview reports."""

import io
import datetime
import pandas as pd
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from utils import sanitize_text_for_pdf


class PDFReport(FPDF):
    """Custom FPDF2 class with header, footer, and styling helpers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        # Header banner
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(100, 116, 139)
        self.set_x(self.l_margin)
        self.cell(0, 8, "AI INTERVIEW COACH  |  ASSESSMENT REPORT", border=0, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)
        # Subtle horizontal divider
        self.set_draw_color(226, 232, 240)
        self.line(self.l_margin, 18, self.w - self.r_margin, 18)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(148, 163, 184)
        self.cell(
            0,
            10,
            f"Page {self.page_no()} of {{nb}}  |  Generated on {datetime.date.today().strftime('%B %d, %Y')}",
            align="C",
            new_x=XPos.RIGHT,
            new_y=YPos.TOP,
        )


def build_markdown(
    report_md: str,
    score_df: pd.DataFrame | None = None,
    gap_data: dict | None = None,
    avg_scores: dict[str, float] | None = None,
    metadata: dict | None = None,
) -> str:
    """
    Constructs a comprehensive Markdown report ready for download.
    """
    metadata = metadata or {}
    avg_scores = avg_scores or {}
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md_lines = [
        "# AI Interview Coach - Final Assessment Report",
        "",
        f"**Date:** {timestamp}  ",
        f"**Mode:** {metadata.get('mode', 'General')}  ",
        f"**Difficulty Level:** {metadata.get('level', 'Standard')}  ",
        f"**Questions Completed:** {metadata.get('n_questions', 0)}  ",
        "",
        "---",
        "",
        "## Performance Score Summary",
        "",
        f"- **Overall Average:** {avg_scores.get('overall', 0)} / 10",
        f"- **Relevance:** {avg_scores.get('relevance', 0)} / 10",
        f"- **Depth:** {avg_scores.get('depth', 0)} / 10",
        f"- **Structure:** {avg_scores.get('structure', 0)} / 10",
        f"- **Clarity:** {avg_scores.get('clarity', 0)} / 10",
        "",
    ]

    if score_df is not None and not score_df.empty:
        md_lines.append("### Question-by-Question Score Table")
        md_lines.append("")
        try:
            table_md = score_df.to_markdown(index=False)
            md_lines.append(table_md)
        except Exception:
            # Fallback table formatting if tabulate isn't installed
            cols = list(score_df.columns)
            md_lines.append("| " + " | ".join(cols) + " |")
            md_lines.append("| " + " | ".join(["---"] * len(cols)) + " |")
            for _, row in score_df.iterrows():
                md_lines.append("| " + " | ".join(str(val) for val in row.values) + " |")
        md_lines.append("")

    md_lines.extend(["---", "", report_md])
    return "\n".join(md_lines)


def build_pdf(
    report_md: str,
    radar_png: bytes | None = None,
    score_df: pd.DataFrame | None = None,
    gap_data: dict | None = None,
    avg_scores: dict[str, float] | None = None,
    metadata: dict | None = None,
) -> bytes:
    """
    Constructs a formatted PDF report with embedded radar chart, score table, and markdown text.
    """
    metadata = metadata or {}
    avg_scores = avg_scores or {}

    pdf = PDFReport()
    pdf.add_page()
    epw = pdf.epw  # Effective page width (total width - left_margin - right_margin)

    # --- Title Section ---
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(15, 23, 42)  # Slate 900
    pdf.set_x(pdf.l_margin)
    pdf.cell(epw, 10, "Interview Assessment & Coaching Report", align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)

    # Metadata Badges / Info
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(71, 85, 105)  # Slate 600
    meta_info = (
        f"Mode: {metadata.get('mode', 'N/A')}  |  "
        f"Level: {metadata.get('level', 'N/A')}  |  "
        f"Questions: {metadata.get('n_questions', 'N/A')}  |  "
        f"Date: {datetime.date.today().strftime('%b %d, %Y')}"
    )
    pdf.set_x(pdf.l_margin)
    pdf.cell(epw, 6, sanitize_text_for_pdf(meta_info), align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    # --- Score Summary Cards ---
    pdf.set_fill_color(241, 245, 249)  # Slate 100
    pdf.set_draw_color(203, 213, 225)  # Slate 300
    box_y = pdf.get_y()
    pdf.rect(pdf.l_margin, box_y, epw, 20, style="FD")
    
    pdf.set_xy(pdf.l_margin + 4, box_y + 3)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(30, 6, "Overall Average: ", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(37, 99, 235)  # Blue 600
    pdf.cell(20, 6, f"{avg_scores.get('overall', 0)}/10", new_x=XPos.RIGHT, new_y=YPos.TOP)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(51, 65, 85)
    pdf.cell(32, 6, f"Relevance: {avg_scores.get('relevance', 0)}/10", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(26, 6, f"Depth: {avg_scores.get('depth', 0)}/10", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(32, 6, f"Structure: {avg_scores.get('structure', 0)}/10", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(26, 6, f"Clarity: {avg_scores.get('clarity', 0)}/10", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(12)

    # --- Radar Chart Image ---
    if radar_png:
        try:
            chart_stream = io.BytesIO(radar_png)
            chart_w = min(115, epw)
            chart_x = pdf.l_margin + (epw - chart_w) / 2.0
            pdf.image(chart_stream, x=chart_x, y=pdf.get_y(), w=chart_w)
            pdf.ln(chart_w + 5)
        except Exception as e:
            pdf.set_font("Helvetica", "I", 9)
            pdf.set_text_color(220, 38, 38)
            pdf.cell(epw, 6, f"[Chart insertion skipped: {str(e)}]", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(4)

    # --- Score Table ---
    if score_df is not None and not score_df.empty:
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(epw, 8, "Per-Question Score Breakdown", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2)

        # Calculate proportional table columns based on available epw
        col_w_num = 10
        col_w_metrics = 18
        col_w_avg = 16
        col_w_q = epw - (col_w_num + (col_w_metrics * 4) + col_w_avg)

        headers = ["#", "Question", "Relevance", "Depth", "Structure", "Clarity", "Avg"]
        widths = [col_w_num, col_w_q, col_w_metrics, col_w_metrics, col_w_metrics, col_w_metrics, col_w_avg]
        
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_fill_color(226, 232, 240)
        pdf.set_text_color(30, 41, 59)
        for i, header in enumerate(headers):
            pdf.cell(widths[i], 7, header, border=1, align="C", fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.ln(7)

        # Table Rows
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(51, 65, 85)
        for _, row in score_df.iterrows():
            pdf.set_x(pdf.l_margin)
            q_num = str(row.get("#", ""))
            q_text = str(row.get("Question", ""))
            if len(q_text) > 45:
                q_text = q_text[:42] + "..."
            
            rel = str(row.get("Relevance", ""))
            depth = str(row.get("Depth", ""))
            struct = str(row.get("Structure", ""))
            clar = str(row.get("Clarity", ""))
            avg_val = str(row.get("Avg", ""))

            pdf.cell(widths[0], 6, sanitize_text_for_pdf(q_num), border=1, align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.cell(widths[1], 6, sanitize_text_for_pdf(q_text), border=1, align="L", new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.cell(widths[2], 6, sanitize_text_for_pdf(rel), border=1, align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.cell(widths[3], 6, sanitize_text_for_pdf(depth), border=1, align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.cell(widths[4], 6, sanitize_text_for_pdf(struct), border=1, align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.cell(widths[5], 6, sanitize_text_for_pdf(clar), border=1, align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.cell(widths[6], 6, sanitize_text_for_pdf(avg_val), border=1, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(8)

    # --- Full Coaching Report (Markdown Parsing) ---
    pdf.add_page()
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(epw, 8, "Detailed Evaluation & Action Plan", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    raw_lines = report_md.split("\n")
    for line in raw_lines:
        s_line = sanitize_text_for_pdf(line.strip())
        if not s_line:
            pdf.ln(2)
            continue

        if s_line.startswith("# "):
            pdf.ln(4)
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(30, 58, 138)  # Blue 900
            clean_h = s_line[2:].replace("**", "")
            pdf.multi_cell(epw, 6, clean_h, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(2)
        elif s_line.startswith("## "):
            pdf.ln(3)
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(37, 99, 235)  # Blue 600
            clean_h = s_line[3:].replace("**", "")
            pdf.multi_cell(epw, 5.5, clean_h, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(1)
        elif s_line.startswith("### "):
            pdf.ln(2)
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(71, 85, 105)  # Slate 600
            clean_h = s_line[4:].replace("**", "")
            pdf.multi_cell(epw, 5, clean_h, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(1)
        elif s_line.startswith("- ") or s_line.startswith("* "):
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(30, 41, 59)
            clean_item = s_line[2:].replace("**", "")
            pdf.set_x(pdf.l_margin + 4)
            pdf.multi_cell(epw - 4, 4.5, f"- {clean_item}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(30, 41, 59)
            clean_p = s_line.replace("**", "")
            pdf.multi_cell(epw, 4.5, clean_p, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    return bytes(pdf.output())
