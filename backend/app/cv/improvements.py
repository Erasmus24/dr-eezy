"""
Generate practical, rule-based CV improvement suggestions.
"""
from typing import List
from app.cv.parser import ParsedCV


def generate_cv_improvements(cv: ParsedCV) -> List[str]:
    suggestions = []

    # 1. Experience
    if cv.experience_years == 0:
        suggestions.append(
            "Add your total years of experience clearly (e.g. '6 years of clinical experience'). "
            "Many job filters look for this number."
        )
    elif cv.experience_years < 2:
        suggestions.append(
            "You have limited experience listed. Emphasize any internships, community service, "
            "or relevant rotations to strengthen your profile."
        )

    # 2. Skills
    if len(cv.skills) < 4:
        suggestions.append(
            "Your CV currently shows few technical skills. Add more specialty-specific skills "
            "(e.g. ventilator management, echocardiography, sterile technique, etc.)."
        )
    elif len(cv.skills) >= 8:
        suggestions.append(
            "Great skill coverage! Consider grouping them under clear headings "
            "(Clinical Skills / Technical Skills / Soft Skills) for better readability."
        )

    # 3. Registration
    if not cv.registration:
        suggestions.append(
            "Include your professional registration number (HPCSA for doctors or SANC for nurses). "
            "This is often a hard requirement for South African hospital roles."
        )

    # 4. Job title clarity
    if not cv.job_title:
        suggestions.append(
            "Make your current or most recent job title very clear near the top of the CV. "
            "Recruiters and AI systems look for this first."
        )

    # 5. Name detection
    if not cv.candidate_name or len(cv.candidate_name.split()) < 2:
        suggestions.append(
            "Ensure your full name appears clearly at the top of the first page."
        )

    # 6. Generic encouragement if the CV is already strong
    if len(suggestions) == 0:
        suggestions.append(
            "Your CV looks solid! To stand out further, quantify achievements "
            "(e.g. 'Managed a 12-bed ICU' or 'Reduced average triage time by 18%')."
        )

    return suggestions