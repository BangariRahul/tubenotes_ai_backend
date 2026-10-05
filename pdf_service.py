import re
from html import escape
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    KeepTogether,
)


def _inline_markdown_to_reportlab(text: str) -> str:
    """Small safe formatter for bold and inline-code Markdown."""
    safe = escape(text, quote=False)
    safe = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", safe)
    safe = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", safe)
    safe = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', safe)
    return safe


def create_notes_pdf(notes_markdown: str, video_id: str, note_type: str) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=19 * mm,
        leftMargin=19 * mm,
        topMargin=20 * mm,
        bottomMargin=18 * mm,
        title=f"YouTube {note_type.title()} Notes",
        author="TubeNotes AI",
        subject=f"Notes for YouTube video {video_id}",
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=21, leading=26, textColor=colors.HexColor("#4338CA"),
        alignment=TA_LEFT, spaceAfter=7 * mm,
    ))
    styles.add(ParagraphStyle(
        name="SubtitleCustom", parent=styles["Normal"], fontSize=9,
        leading=13, textColor=colors.HexColor("#64748B"), spaceAfter=2 * mm,
    ))
    styles.add(ParagraphStyle(
        name="SectionCustom", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=14, leading=18, textColor=colors.HexColor("#3730A3"),
        spaceBefore=5 * mm, spaceAfter=2 * mm, keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        name="SubsectionCustom", parent=styles["Heading3"], fontName="Helvetica-Bold",
        fontSize=11, leading=14, textColor=colors.HexColor("#1E293B"),
        spaceBefore=3 * mm, spaceAfter=1.5 * mm, keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        name="BodyCustom", parent=styles["BodyText"], fontName="Helvetica",
        fontSize=9.5, leading=14, textColor=colors.HexColor("#273244"),
        spaceAfter=2.2 * mm, splitLongWords=True,
    ))
    styles.add(ParagraphStyle(
        name="BulletCustom", parent=styles["BodyCustom"], leftIndent=5 * mm,
        firstLineIndent=-3 * mm, bulletIndent=0, spaceAfter=1.5 * mm,
    ))
    styles.add(ParagraphStyle(
        name="SmallCustom", parent=styles["Normal"], fontSize=8,
        leading=10, textColor=colors.HexColor("#64748B"),
    ))

    story = [
        Paragraph("TubeNotes AI", styles["CoverTitle"]),
        Paragraph(f"{escape(note_type.title())} · English notes", styles["SubtitleCustom"]),
        Paragraph(f"YouTube video ID: {escape(video_id)}", styles["SubtitleCustom"]),
        Spacer(1, 3 * mm),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#C7D2FE")),
        Spacer(1, 4 * mm),
    ]

    in_code_block = False
    for raw_line in notes_markdown.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if not stripped:
            story.append(Spacer(1, 1.2 * mm))
            continue
        if in_code_block:
            story.append(Paragraph(_inline_markdown_to_reportlab(stripped), styles["Code"]))
            continue

        if stripped.startswith("### "):
            story.append(Paragraph(_inline_markdown_to_reportlab(stripped[4:]), styles["SubsectionCustom"]))
        elif stripped.startswith("## "):
            story.append(Paragraph(_inline_markdown_to_reportlab(stripped[3:]), styles["SectionCustom"]))
        elif stripped.startswith("# "):
            story.append(Paragraph(_inline_markdown_to_reportlab(stripped[2:]), styles["SectionCustom"]))
        elif re.match(r"^\s*[-*]\s+", line):
            item = re.sub(r"^\s*[-*]\s+", "", line)
            story.append(Paragraph("• " + _inline_markdown_to_reportlab(item), styles["BulletCustom"]))
        elif re.match(r"^\s*\d+[.)]\s+", line):
            story.append(Paragraph(_inline_markdown_to_reportlab(stripped), styles["BulletCustom"]))
        elif stripped.startswith("> "):
            story.append(Paragraph(_inline_markdown_to_reportlab(stripped[2:]), styles["Italic"]))
        else:
            story.append(Paragraph(_inline_markdown_to_reportlab(stripped), styles["BodyCustom"]))

    def add_page_number(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#E2E8F0"))
        canvas.line(19 * mm, 14 * mm, A4[0] - 19 * mm, 14 * mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#64748B"))
        canvas.drawString(19 * mm, 9 * mm, "Generated by TubeNotes AI")
        canvas.drawRightString(A4[0] - 19 * mm, 9 * mm, f"Page {document.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    return buffer.getvalue()
