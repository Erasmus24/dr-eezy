"""
CV parsing module.

Extracts raw text from an uploaded CV (PDF) and infers structured fields that the
rest of the app needs: profession (Doctor / Nurse), job title / specialty, years of
experience, and a flat list of skill keywords.

This uses simple, transparent rule-based extraction (regex + keyword lists) rather
than an LLM call, so it's fast, free, deterministic, and easy to unit test — ideal
for a live demo. It can be swapped for an LLM-based extractor later without changing
the rest of the pipeline (the output shape stays the same).
"""
import io
import re
from dataclasses import dataclass, field
from typing import List, Optional

from pypdf import PdfReader

# Canonical job titles we recognise, grouped by profession.
DOCTOR_TITLES = [
    "General Practitioner", "Cardiologist", "Pediatrician", "Paediatrician",
    "Orthopedic Surgeon", "Orthopaedic Surgeon", "Anesthesiologist", "Anaesthesiologist",
    "Surgeon", "Physician",
]
NURSE_TITLES = [
    "Registered Nurse - ICU", "Registered Nurse - Pediatric Ward",
    "Registered Nurse - Paediatric Ward", "Theatre Nurse (Scrub Nurse)", "Theatre Nurse",
    "Scrub Nurse", "Midwife", "Nurse Practitioner", "Registered Nurse", "Staff Nurse",
]

ALL_SKILLS = [
    "echocardiography", "cardiac catheterization", "angiography", "patient consultation",
    "ecg interpretation", "diagnosis", "chronic disease management", "primary care",
    "minor procedures", "neonatal care", "child development assessment",
    "vaccination programs", "ventilator management", "critical care monitoring",
    "iv medication administration", "patient triage", "scrubbing and assisting in surgery",
    "sterile technique", "surgical instrument management", "orthopedic theatre experience",
    "labour and delivery care", "antenatal care", "postnatal care", "newborn assessment",
    "joint replacement surgery", "trauma surgery", "arthroscopy", "surgical planning",
    "general anesthesia", "regional anesthesia", "airway management",
    "medication administration", "family communication", "vital signs monitoring",
]

EXPERIENCE_PATTERN = re.compile(r"(\d+)\s*(?:\+)?\s*years?", re.IGNORECASE)
REGISTRATION_PATTERN = re.compile(r"\b(HPCSA|SANC)\b[^\n]*", re.IGNORECASE)


@dataclass
class ParsedCV:
    raw_text: str
    candidate_name: Optional[str] = None
    profession: Optional[str] = None          # "Doctor" | "Nurse" | None
    job_title: Optional[str] = None           # canonical matched title
    experience_years: int = 0
    skills: List[str] = field(default_factory=list)
    registration: Optional[str] = None


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    text_parts = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(text_parts)


def _find_title(text: str, titles: List[str]) -> Optional[str]:
    lowered = text.lower()
    # Sort longest-first so more specific titles match before generic ones
    # (e.g. "Registered Nurse - ICU" before "Registered Nurse").
    for title in sorted(titles, key=len, reverse=True):
        if title.lower() in lowered:
            return title
    return None


def _extract_name(text: str) -> Optional[str]:
    # Assume the candidate's name is the first non-empty line of the CV.
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line
    return None


def _extract_experience_years(text: str) -> int:
    matches = EXPERIENCE_PATTERN.findall(text)
    if not matches:
        return 0
    return max(int(m) for m in matches)


def _extract_skills(text: str) -> List[str]:
    lowered = text.lower()
    return [skill for skill in ALL_SKILLS if skill in lowered]


def _extract_registration(text: str) -> Optional[str]:
    match = REGISTRATION_PATTERN.search(text)
    return match.group(0).strip() if match else None


def parse_cv(file_bytes: bytes) -> ParsedCV:
    """Parse a CV PDF's bytes into structured fields."""
    text = extract_text_from_pdf(file_bytes)

    doctor_title = _find_title(text, DOCTOR_TITLES)
    nurse_title = _find_title(text, NURSE_TITLES)

    if doctor_title:
        profession, job_title = "Doctor", doctor_title
    elif nurse_title:
        profession, job_title = "Nurse", nurse_title
    else:
        profession, job_title = None, None

    return ParsedCV(
        raw_text=text,
        candidate_name=_extract_name(text),
        profession=profession,
        job_title=job_title,
        experience_years=_extract_experience_years(text),
        skills=_extract_skills(text),
        registration=_extract_registration(text),
    )
