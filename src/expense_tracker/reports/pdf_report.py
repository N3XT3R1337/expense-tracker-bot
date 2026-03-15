import io
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from ..models.expense import Expense
from .charts import generate_bar_chart, generate_pie_chart


def generate_pdf_report(
    expenses: list[Expense],
    by_category: list[tuple[str, str, Decimal]],
    total: Decimal,
    month_name: str,
    username: str,
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=24,
        spaceAfter=12,
        textColor=colors.HexColor("#2C3E50"),
    )
    subtitle_style = ParagraphStyle(
        "CustomSubtitle",
        parent=styles["Normal"],
        fontSize=14,
        spaceAfter=20,
        textColor=colors.HexColor("#7F8C8D"),
    )
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=10,
        textColor=colors.HexColor("#2C3E50"),
    )

    elements = []

    elements.append(Paragraph("Expense Report", title_style))
    elements.append(Paragraph(f"{month_name} | {username}", subtitle_style))
    elements.append(Spacer(1, 10))

    summary_data = [
        ["Total Expenses", f"${total:,.2f}"],
        ["Number of Transactions", str(len(expenses))],
        ["Categories Used", str(len(by_category))],
    ]
    if expenses:
        avg = total / len(expenses)
        summary_data.append(["Average per Transaction", f"${avg:,.2f}"])

    summary_table = Table(summary_data, colWidths=[200, 200])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#ECF0F1")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#2C3E50")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("PADDING", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    if by_category:
        elements.append(Paragraph("Category Breakdown", heading_style))
        cat_data = [["Category", "Amount", "Percentage"]]
        for name, emoji, amount in by_category:
            pct = (amount / total * 100) if total > 0 else Decimal("0")
            cat_data.append([f"{name}", f"${amount:,.2f}", f"{pct:.1f}%"])

        cat_table = Table(cat_data, colWidths=[180, 120, 100])
        cat_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498DB")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
        ]))
        elements.append(cat_table)
        elements.append(Spacer(1, 20))

        pie_bytes = generate_pie_chart(by_category)
        if pie_bytes:
            pie_img = Image(io.BytesIO(pie_bytes), width=5 * inch, height=3.75 * inch)
            elements.append(pie_img)
            elements.append(Spacer(1, 20))

    if expenses:
        elements.append(Paragraph("Recent Transactions", heading_style))
        tx_data = [["Date", "Category", "Amount", "Description"]]
        for exp in expenses[:30]:
            tx_data.append([
                exp.created_at.strftime("%Y-%m-%d"),
                exp.category.name if exp.category else "N/A",
                f"${exp.amount:,.2f}",
                (exp.description or "")[:40],
            ])

        tx_table = Table(tx_data, colWidths=[80, 100, 80, 160])
        tx_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2ECC71")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
            ("ALIGN", (2, 0), (2, -1), "RIGHT"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
        ]))
        elements.append(tx_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()
