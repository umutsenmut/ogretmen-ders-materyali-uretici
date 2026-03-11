import io
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    HRFlowable,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register DejaVu Sans which has full Unicode / Turkish character support
_FONT_REGISTERED = False
_FONT_NAME = "Helvetica"
_FONT_BOLD = "Helvetica-Bold"

def _register_unicode_font():
    global _FONT_REGISTERED, _FONT_NAME, _FONT_BOLD
    if _FONT_REGISTERED:
        return
    candidates = [
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
    ]
    for regular, bold in candidates:
        if os.path.exists(regular) and os.path.exists(bold):
            try:
                pdfmetrics.registerFont(TTFont("TurkishFont", regular))
                pdfmetrics.registerFont(TTFont("TurkishFont-Bold", bold))
                _FONT_NAME = "TurkishFont"
                _FONT_BOLD = "TurkishFont-Bold"
                break
            except Exception:
                pass
    _FONT_REGISTERED = True


def _build_styles():
    _register_unicode_font()
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontName=_FONT_BOLD,
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0d6efd"),
        spaceAfter=12,
        alignment=TA_CENTER,
    )
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontName=_FONT_BOLD,
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0d6efd"),
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontName=_FONT_NAME,
        fontSize=10,
        leading=14,
        spaceAfter=4,
        alignment=TA_LEFT,
    )
    justify_style = ParagraphStyle(
        "CustomJustify",
        parent=styles["Normal"],
        fontName=_FONT_NAME,
        fontSize=10,
        leading=14,
        spaceAfter=4,
        alignment=TA_JUSTIFY,
    )
    return title_style, heading_style, body_style, justify_style


class PdfExporter:
    def export_flashcards(self, cards, subject, topic):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )
        title_style, heading_style, body_style, _ = _build_styles()
        story = []

        story.append(Paragraph("Bilgi Kartları", title_style))
        story.append(Paragraph(f"{subject} - {topic}", heading_style))
        story.append(Spacer(1, 0.5 * cm))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0d6efd")))
        story.append(Spacer(1, 0.5 * cm))

        for card in cards:
            card_id = card.get("id", "")
            front = card.get("front", "")
            back = card.get("back", "")

            table_data = [
                [
                    Paragraph(f"Kart {card_id} - Ön Yüz", body_style),
                    Paragraph(f"Kart {card_id} - Arka Yüz", body_style),
                ],
                [
                    Paragraph(self._safe(front), body_style),
                    Paragraph(self._safe(back), body_style),
                ],
            ]
            t = Table(table_data, colWidths=[8 * cm, 8 * cm])
            t.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#0d6efd")),
                        ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#198754")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTSIZE", (0, 0), (-1, -1), 10),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
                        ("PADDING", (0, 0), (-1, -1), 8),
                        ("MINROWHEIGHT", (0, 1), (-1, -1), 60),
                    ]
                )
            )
            story.append(t)
            story.append(Spacer(1, 0.4 * cm))

        doc.build(story)
        return buffer.getvalue()

    def export_presentation(self, slides, subject, topic):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )
        title_style, heading_style, body_style, _ = _build_styles()
        story = []

        story.append(Paragraph("Sunum İçeriği", title_style))
        story.append(Paragraph(f"{subject} - {topic}", heading_style))
        story.append(Spacer(1, 0.5 * cm))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0d6efd")))
        story.append(Spacer(1, 0.5 * cm))

        for slide in slides:
            num = slide.get("slide_number", "")
            s_title = slide.get("title", "")
            content = slide.get("content", [])
            visual = slide.get("visual_suggestion", "")

            story.append(Paragraph(f"Slayt {num}: {self._safe(s_title)}", heading_style))

            if isinstance(content, list):
                for item in content:
                    story.append(Paragraph(f"• {self._safe(str(item))}", body_style))
            else:
                story.append(Paragraph(self._safe(str(content)), body_style))

            if visual:
                story.append(
                    Paragraph(f"Görsel Öneri: {self._safe(visual)}", body_style)
                )
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
            story.append(Spacer(1, 0.3 * cm))

        doc.build(story)
        return buffer.getvalue()

    def export_test(self, test_data, subject, topic):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )
        title_style, heading_style, body_style, justify_style = _build_styles()
        story = []

        story.append(Paragraph("Test / Sınav", title_style))
        story.append(Paragraph(f"{subject} - {topic}", heading_style))
        story.append(Spacer(1, 0.3 * cm))
        story.append(
            Paragraph("Ad Soyad: ___________________________   Tarih: __________   Sınıf: _______", body_style)
        )
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0d6efd")))
        story.append(Spacer(1, 0.3 * cm))

        multiple_choice = test_data.get("multiple_choice", [])
        open_ended = test_data.get("open_ended", [])

        if multiple_choice:
            story.append(Paragraph("A BÖLÜMÜ - Çoktan Seçmeli Sorular", heading_style))
            for i, q in enumerate(multiple_choice, 1):
                question_text = self._safe(q.get("question", ""))
                story.append(Paragraph(f"{i}. {question_text}", body_style))
                opts = q.get("options", {})
                for opt_key in ["A", "B", "C", "D"]:
                    opt_val = self._safe(opts.get(opt_key, ""))
                    story.append(Paragraph(f"    {opt_key}) {opt_val}", body_style))
                story.append(Spacer(1, 0.2 * cm))

        if open_ended:
            story.append(PageBreak())
            story.append(Paragraph("B BÖLÜMÜ - Açık Uçlu Sorular", heading_style))
            for i, q in enumerate(open_ended, 1):
                question_text = self._safe(q.get("question", ""))
                story.append(Paragraph(f"{i}. {question_text}", body_style))
                for _ in range(4):
                    story.append(Paragraph("_" * 80, body_style))
                story.append(Spacer(1, 0.3 * cm))

        # Answer key
        if multiple_choice:
            story.append(PageBreak())
            story.append(Paragraph("CEVAP ANAHTARI", heading_style))
            answer_rows = []
            row = []
            for i, q in enumerate(multiple_choice, 1):
                row.append(f"{i}. {q.get('correct_answer', '-')}")
                if len(row) == 5:
                    answer_rows.append(row)
                    row = []
            if row:
                while len(row) < 5:
                    row.append("")
                answer_rows.append(row)
            if answer_rows:
                ans_table = Table(
                    answer_rows,
                    colWidths=[3 * cm] * 5,
                )
                ans_table.setStyle(
                    TableStyle(
                        [
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                            ("FONTSIZE", (0, 0), (-1, -1), 9),
                            ("PADDING", (0, 0), (-1, -1), 4),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ]
                    )
                )
                story.append(ans_table)

        doc.build(story)
        return buffer.getvalue()

    def export_notes(self, notes_data, subject, topic):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )
        title_style, heading_style, body_style, justify_style = _build_styles()
        story = []

        doc_title = notes_data.get("title", f"{subject} - {topic}")
        story.append(Paragraph(self._safe(doc_title), title_style))
        story.append(Spacer(1, 0.3 * cm))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0d6efd")))
        story.append(Spacer(1, 0.3 * cm))

        main_concepts = notes_data.get("main_concepts", [])
        if main_concepts:
            story.append(Paragraph("Ana Kavramlar", heading_style))
            for concept in main_concepts:
                story.append(Paragraph(f"• {self._safe(concept)}", body_style))
            story.append(Spacer(1, 0.3 * cm))

        detailed = notes_data.get("detailed_explanation", "")
        if detailed:
            story.append(Paragraph("Ayrıntılı Açıklama", heading_style))
            story.append(Paragraph(self._safe(detailed), justify_style))
            story.append(Spacer(1, 0.3 * cm))

        examples = notes_data.get("examples", [])
        if examples:
            story.append(Paragraph("Örnekler", heading_style))
            for ex in examples:
                story.append(Paragraph(f"• {self._safe(ex)}", body_style))
            story.append(Spacer(1, 0.3 * cm))

        warnings = notes_data.get("warnings", [])
        if warnings:
            story.append(Paragraph("Dikkat Edilmesi Gerekenler", heading_style))
            for w in warnings:
                story.append(Paragraph(f"⚠ {self._safe(w)}", body_style))
            story.append(Spacer(1, 0.3 * cm))

        tips = notes_data.get("tips", [])
        if tips:
            story.append(Paragraph("Öğretim İpuçları", heading_style))
            for tip in tips:
                story.append(Paragraph(f"✓ {self._safe(tip)}", body_style))

        doc.build(story)
        return buffer.getvalue()

    def _safe(self, text):
        """Escape XML special characters for use in ReportLab Paragraph markup."""
        if not text:
            return ""
        text = str(text)
        # Escape XML special chars used by ReportLab's Paragraph markup
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return text
