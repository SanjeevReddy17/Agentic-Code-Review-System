from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Preformatted
)
from reportlab.lib.enums import TA_CENTER
from xml.sax.saxutils import escape
from datetime import datetime
import os


def generate_pdf_report(results, source_code):

    os.makedirs("reports", exist_ok=True)

    filename = (
        f"code_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    filepath = os.path.abspath(os.path.join("reports", filename))

    document = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=22,
        textColor=colors.HexColor("#172554"),
        alignment=TA_CENTER,
        spaceAfter=15
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#3730a3"),
        spaceBefore=15,
        spaceAfter=10
    )

    normal_style = styles["BodyText"]

    story = []

    # PROJECT TITLE

    story.append(
        Paragraph("AGENTIC CODE REVIEW SYSTEM", title_style)
    )

    story.append(
        Paragraph(
            "AI-Powered Automated Code Analysis Report",
            ParagraphStyle(
                "Subtitle",
                parent=normal_style,
                alignment=TA_CENTER
            )
        )
    )

    story.append(Spacer(1, 20))

    # DATE

    story.append(
        Paragraph(
            f"<b>Report Generated:</b> {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
            normal_style
        )
    )

    story.append(Spacer(1, 20))

    # EXTRACT RESULTS

    code_analysis = results.get("code_analysis", {})
    security_analysis = results.get("security_analysis", {})

    code_issues = code_analysis.get("total_issues", 0)
    security_issues = security_analysis.get(
        "total_security_issues", 0
    )

    syntax_status = code_analysis.get(
        "syntax_status", "Unknown"
    )

    quality_score = max(
        0,
        min(100, 100 - code_issues * 10 - security_issues * 15)
    )

    # SUMMARY

    story.append(
        Paragraph("1. Code Quality Summary", heading_style)
    )

    summary_data = [
        ["Metric", "Result"],
        ["Code Quality Score", f"{quality_score}/100"],
        ["Programming Issues", str(code_issues)],
        ["Security Vulnerabilities", str(security_issues)],
        ["Syntax Status", str(syntax_status)]
    ]

    summary_table = Table(
        summary_data,
        colWidths=[3 * inch, 2.5 * inch]
    )

    summary_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#172554")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 9),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f1f5f9"))
        ])
    )

    story.append(summary_table)

    # SECURITY ISSUES

    story.append(
        Paragraph("2. Security Analysis", heading_style)
    )

    security_list = security_analysis.get(
        "security_issues", []
    )

    if security_list:
        for issue in security_list:
            message = escape(str(issue.get("message", "No description")))
            severity = escape(str(issue.get("severity", "Unknown")))
            line = escape(str(issue.get("line", "Unknown")))

            story.append(
                Paragraph(
                    f"<b>Severity:</b> {severity}<br/>"
                    f"<b>Line:</b> {line}<br/>"
                    f"<b>Issue:</b> {message}",
                    normal_style
                )
            )
            story.append(Spacer(1, 10))
    else:
        story.append(
            Paragraph("No security issues detected.", normal_style)
        )

    # CODE ANALYSIS

    story.append(
        Paragraph("3. Programming Code Analysis", heading_style)
    )

    issues = code_analysis.get("issues", [])

    if issues:
        for issue in issues:
            story.append(
                Paragraph(escape(str(issue)), normal_style)
            )
    else:
        story.append(
            Paragraph("No programming issues detected.", normal_style)
        )

    # SOURCE CODE

    story.append(
        Paragraph("4. Submitted Source Code", heading_style)
    )

    code_style = ParagraphStyle(
        "CodeStyle",
        parent=styles["Code"],
        fontSize=8,
        leading=11,
        backColor=colors.HexColor("#f1f5f9"),
        borderPadding=8
    )

    story.append(
        Preformatted(
            escape(source_code),
            code_style
        )
    )

    # AI REVIEW

    story.append(
        Paragraph("5. Gemini AI-Powered Review", heading_style)
    )

    ai_review = results.get(
        "ai_review",
        "No AI review available."
    )

    for paragraph in str(ai_review).split("\n"):
        if paragraph.strip():
            story.append(
                Paragraph(
                    escape(paragraph),
                    normal_style
                )
            )
            story.append(Spacer(1, 5))

    # FOOTER

    story.append(Spacer(1, 25))

    story.append(
        Paragraph(
            "Generated by Agentic Code Review System",
            ParagraphStyle(
                "Footer",
                parent=normal_style,
                alignment=TA_CENTER,
                textColor=colors.grey
            )
        )
    )

    document.build(story)

    return filename