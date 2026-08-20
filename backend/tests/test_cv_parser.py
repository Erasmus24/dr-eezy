"""
Checkpoint test: verifies the CV parser correctly extracts profession, job title,
experience, and skills from each of the synthetic sample CVs.

Run with:  cd backend && source .venv/bin/activate && pytest tests/test_cv_parser.py -v
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.cv.parser import parse_cv

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "sample_cvs")

EXPECTED = {
    "cv_thabo_nkosi.pdf": {"profession": "Doctor", "job_title": "Cardiologist", "min_skills": 3},
    "cv_sarah_combrink.pdf": {"profession": "Doctor", "job_title": "General Practitioner", "min_skills": 3},
    "cv_amina_patel.pdf": {"profession": "Doctor", "job_title": "Pediatrician", "min_skills": 3},
    "cv_palesa_mokoena.pdf": {"profession": "Nurse", "job_title": "Registered Nurse - ICU", "min_skills": 3},
    "cv_james_botha.pdf": {"profession": "Nurse", "job_title": "Theatre Nurse (Scrub Nurse)", "min_skills": 3},
    "cv_lindiwe_zulu.pdf": {"profession": "Nurse", "job_title": "Midwife", "min_skills": 3},
}


def test_all_sample_cvs_parse_correctly():
    for filename, expected in EXPECTED.items():
        path = os.path.join(SAMPLE_DIR, filename)
        with open(path, "rb") as f:
            parsed = parse_cv(f.read())

        assert parsed.profession == expected["profession"], f"{filename}: profession mismatch"
        assert parsed.job_title == expected["job_title"], f"{filename}: job_title mismatch"
        assert len(parsed.skills) >= expected["min_skills"], f"{filename}: too few skills detected"
        assert parsed.experience_years > 0, f"{filename}: experience years not detected"
        assert parsed.registration is not None, f"{filename}: registration not detected"
        print(f"OK  {filename}: {parsed.profession} / {parsed.job_title} / "
              f"{parsed.experience_years}y / {len(parsed.skills)} skills")
