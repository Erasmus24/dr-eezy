"""
Renders a generated roster (see generator.py) to a clean, printable PDF using
ReportLab (open-source, BSD-license, no external service required).

The PDF groups shifts by job title (never mixing doctors and nurses on the same
table — see data/knowledge_base/job_title_glossary.md) and ends each group with a
totals table so a manager can visually confirm the workload is balanced.
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak


def export_roster_to_pdf(roster: dict, output_path: str, title: str = "Medics Online — Staff Roster") -> str:
    doc = SimpleDocTemplate(output_path, pagesize=landscape(A4),
                             topMargin=15 * mm, bottomMargin=15 * mm)
    styles = getSampleStyleSheet()
    story = [Paragraph(title, styles["Title"]), Spacer(1, 8 * mm)]

    job_titles = list(roster.keys())
    for idx, job_title in enumerate(job_titles):
        group = roster[job_title]
        story.append(Paragraph(job_title, styles["Heading2"]))
        story.append(Spacer(1, 4 * mm))

        # Determine which shift columns actually appear for this group.
        shift_cols = sorted({s for entry in group["dates"] for s in entry["shifts"].keys()})
        header = ["Date"] + shift_cols
        rows = [header]
        for entry in group["dates"]:
            row = [entry["date"]]
            for shift in shift_cols:
                names = entry["shifts"].get(shift, [])
                row.append(", ".join(names) if names else "—")
            rows.append(row)

        table = Table(rows, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(table)
        story.append(Spacer(1, 6 * mm))

        # Fairness summary
        story.append(Paragraph("Shift totals (fairness check)", styles["Heading4"]))
        totals_rows = [["Staff member", "Total shifts"]] + [
            [name, str(count)] for name, count in group["totals"].items()
        ]
        totals_table = Table(totals_rows, hAlign="LEFT", colWidths=[80 * mm, 30 * mm])
        totals_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#548235")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
        ]))
        story.append(totals_table)

        if group["warnings"]:
            story.append(Spacer(1, 4 * mm))
            for w in group["warnings"]:
                story.append(Paragraph(f"⚠ {w}", styles["Normal"]))

        if idx < len(job_titles) - 1:
            story.append(PageBreak())

    doc.build(story)
    return output_path
