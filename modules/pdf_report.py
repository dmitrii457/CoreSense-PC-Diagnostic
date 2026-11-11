"""Paginated Unicode PDF export for a saved diagnostic session."""
import os
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer


def register_font():
    if "FixAIReport" in pdfmetrics.getRegisteredFontNames():
        return "FixAIReport"
    candidates = [
        Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts/arial.ttf",
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            pdfmetrics.registerFont(TTFont("FixAIReport", str(candidate)))
            return "FixAIReport"
    raise RuntimeError("Для русского текста нужен шрифт Arial или DejaVu Sans.")


def export_session_pdf(session, destination):
    path = Path(destination)
    font = register_font()
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=48, leftMargin=48,
                            topMargin=48, bottomMargin=48, title="FixAI - отчёт диагностики", author="FixAI")
    body = ParagraphStyle("Body", fontName=font, fontSize=10, leading=15, textColor=colors.HexColor("#25324A"),
                          spaceAfter=5, alignment=TA_LEFT, splitLongWords=True)
    title = ParagraphStyle("Title", parent=body, fontSize=25, leading=31, textColor=colors.HexColor("#6940C6"), spaceAfter=16)
    heading = ParagraphStyle("Heading", parent=body, fontSize=12, leading=18, spaceBefore=12, spaceAfter=7,
                             textColor=colors.HexColor("#6940C6"), keepWithNext=True)
    story = [Paragraph("FixAI / Отчёт диагностики", title),
             Paragraph("Дата создания сессии (UTC): " + escape(session.created[:19].replace("T", " ")), body),
             Paragraph("Идентификатор: " + escape(session.id), body), Spacer(1, 12)]
    for line in session.report_text().splitlines():
        if not line.strip():
            story.append(Spacer(1, 6))
            continue
        is_heading = line.isupper() and len(line) < 80
        safe = line.replace("→", " / ").replace("—", "-").replace("–", "-").replace("•", "-")
        story.append(Paragraph(escape(safe), heading if is_heading else body))

    def footer(canvas, document):
        canvas.setFont(font, 8)
        canvas.setFillColor(colors.HexColor("#68748B"))
        canvas.drawString(48, 27, "FixAI / Предварительная диагностика")
        canvas.drawRightString(A4[0] - 48, 27, str(document.page))

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return path
