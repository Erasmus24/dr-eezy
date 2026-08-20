"""
Generates realistic synthetic candidate CVs as PDF files for the Dr. Eezy demo.
Run with:  python scripts/generate_sample_cvs.py
Output:    backend/data/sample_cvs/*.pdf
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "backend", "data", "sample_cvs")
os.makedirs(OUT_DIR, exist_ok=True)

CANDIDATES = [
    {
        "file": "cv_thabo_nkosi.pdf",
        "name": "Dr. Thabo Nkosi",
        "profession": "Doctor",
        "title": "Cardiologist",
        "registration": "HPCSA MP0123456",
        "experience_years": 7,
        "skills": ["echocardiography", "cardiac catheterization", "angiography", "patient consultation", "ECG interpretation"],
        "summary": "Cardiologist with 7 years' experience in private and hospital cardiology practice, "
                   "specializing in non-invasive and invasive cardiac diagnostics.",
    },
    {
        "file": "cv_sarah_combrink.pdf",
        "name": "Dr. Sarah Combrink",
        "profession": "Doctor",
        "title": "General Practitioner",
        "registration": "HPCSA MP0234567",
        "experience_years": 4,
        "skills": ["patient consultation", "diagnosis", "chronic disease management", "primary care", "minor procedures"],
        "summary": "General Practitioner with 4 years' experience in busy outpatient clinics, "
                   "strong focus on chronic disease management and preventive care.",
    },
    {
        "file": "cv_amina_patel.pdf",
        "name": "Dr. Amina Patel",
        "profession": "Doctor",
        "title": "Pediatrician",
        "registration": "HPCSA MP0345678",
        "experience_years": 5,
        "skills": ["neonatal care", "child development assessment", "vaccination programs", "patient consultation"],
        "summary": "Pediatrician with 5 years' experience across neonatal and general pediatric care, "
                   "passionate about child development and preventive health.",
    },
    {
        "file": "cv_palesa_mokoena.pdf",
        "name": "Palesa Mokoena",
        "profession": "Nurse",
        "title": "Registered Nurse - ICU",
        "registration": "SANC NR1122334",
        "experience_years": 3,
        "skills": ["ventilator management", "critical care monitoring", "IV medication administration", "patient triage"],
        "summary": "Registered Nurse with 3 years' ICU experience in high-acuity hospital settings, "
                   "skilled in ventilator management and critical care monitoring.",
    },
    {
        "file": "cv_james_botha.pdf",
        "name": "James Botha",
        "profession": "Nurse",
        "title": "Theatre Nurse (Scrub Nurse)",
        "registration": "SANC NR2233445",
        "experience_years": 6,
        "skills": ["scrubbing and assisting in surgery", "sterile technique", "surgical instrument management", "orthopedic theatre experience"],
        "summary": "Theatre Nurse with 6 years' experience scrubbing for orthopedic and general surgery cases, "
                   "strong sterile technique and instrument management skills.",
    },
    {
        "file": "cv_lindiwe_zulu.pdf",
        "name": "Lindiwe Zulu",
        "profession": "Nurse",
        "title": "Midwife",
        "registration": "SANC NR3344556",
        "experience_years": 4,
        "skills": ["labour and delivery care", "antenatal care", "postnatal care", "newborn assessment"],
        "summary": "Qualified Midwife with 4 years' experience supporting labour, delivery, and postnatal "
                   "care in busy maternity units.",
    },
]


def draw_cv(path, c_data):
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    x = 20 * mm
    y = height - 25 * mm

    c.setFont("Helvetica-Bold", 16)
    c.drawString(x, y, c_data["name"])
    y -= 8 * mm

    c.setFont("Helvetica", 11)
    c.drawString(x, y, f"{c_data['title']}  |  {c_data['profession']}  |  {c_data['registration']}")
    y -= 10 * mm

    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "Professional Summary")
    y -= 6 * mm
    c.setFont("Helvetica", 10)
    for line in wrap_text(c_data["summary"], 95):
        c.drawString(x, y, line)
        y -= 5 * mm
    y -= 4 * mm

    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "Experience")
    y -= 6 * mm
    c.setFont("Helvetica", 10)
    c.drawString(x, y, f"{c_data['experience_years']} years of relevant clinical experience as a {c_data['title']}.")
    y -= 10 * mm

    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "Key Skills")
    y -= 6 * mm
    c.setFont("Helvetica", 10)
    for skill in c_data["skills"]:
        c.drawString(x + 4 * mm, y, f"- {skill}")
        y -= 5 * mm

    y -= 8 * mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "Registration")
    y -= 6 * mm
    c.setFont("Helvetica", 10)
    c.drawString(x, y, c_data["registration"])

    c.showPage()
    c.save()


def wrap_text(text, width):
    words = text.split()
    lines, current = [], ""
    for w in words:
        if len(current) + len(w) + 1 <= width:
            current = (current + " " + w).strip()
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


if __name__ == "__main__":
    for cand in CANDIDATES:
        out_path = os.path.join(OUT_DIR, cand["file"])
        draw_cv(out_path, cand)
        print(f"Generated {out_path}")
    print(f"\nDone. {len(CANDIDATES)} sample CVs written to {OUT_DIR}")
