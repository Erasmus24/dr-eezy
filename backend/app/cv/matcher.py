"""
Matches a parsed CV against open job postings.

Strategy: build a short natural-language query from the candidate's job title,
specialty, and skills, then run it through the RAG retriever — filtered to
`doc_type="job"` AND the candidate's own `profession` (Doctor/Nurse), so a nurse's
CV is never matched against doctor vacancies or vice versa (see
data/knowledge_base/job_title_glossary.md).
"""
from typing import List

from app.cv.parser import ParsedCV
from app.rag.retriever import retrieve


def build_match_query(cv: ParsedCV) -> str:
    parts = [cv.job_title or "", f"{cv.experience_years} years experience"]
    if cv.skills:
        parts.append("skills: " + ", ".join(cv.skills))
    return ". ".join(p for p in parts if p)


def match_jobs(cv: ParsedCV, k: int = 5) -> List[dict]:
    if not cv.profession:
        return []

    query = build_match_query(cv)
    hits = retrieve(query, k=k, doc_type="job", profession=cv.profession)

    results = []
    for hit in hits:
        meta = hit["metadata"]
        # distance is cosine/L2 depending on backend; convert to a rough 0-100 "match score"
        score = max(0.0, min(100.0, (1 - hit["distance"]) * 100)) if hit["distance"] is not None else None
        results.append({
            "job_id": meta.get("job_id"),
            "title": meta.get("title"),
            "specialty": meta.get("specialty"),
            "profession": meta.get("profession"),
            "match_score": round(score, 1) if score is not None else None,
            "description_snippet": hit["text"][:220],
        })
    return results
