"""
report_generator.py
--------------------
Generates a downloadable PDF "Resume Report" summarizing a candidate's
resume analysis (skills, strength score, recommendations) using reportlab.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_resume_report(output_path, candidate_name, resume):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle", parent=styles["Title"], textColor=colors.HexColor("#2563eb")
    )
    heading_style = ParagraphStyle(
        "HeadingStyle", parent=styles["Heading2"], textColor=colors.HexColor("#1e293b")
    )

    doc = SimpleDocTemplate(output_path, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    elements = []

    elements.append(Paragraph("SmartHire AI — Resume Analysis Report", title_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Candidate: {candidate_name}", styles["Normal"]))
    elements.append(Paragraph(f"Resume File: {resume.filename}", styles["Normal"]))
    elements.append(Spacer(1, 16))

    elements.append(Paragraph("Resume Strength Score", heading_style))
    elements.append(Paragraph(f"{resume.match_score} / 100", styles["Normal"]))
    elements.append(Spacer(1, 16))

    elements.append(Paragraph("Extracted Skills", heading_style))
    skills = resume.skills_list()
    if skills:
        data = [["#", "Skill"]] + [[str(i + 1), s.title()] for i, s in enumerate(skills)]
        table = Table(data, colWidths=[2 * cm, 10 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                ]
            )
        )
        elements.append(table)
    else:
        elements.append(Paragraph("No skills detected.", styles["Normal"]))

    doc.build(elements)
    return output_path
