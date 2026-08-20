"""
Checkpoint test: verifies job matching logic and the Doctor/Nurse profession
guardrail, without requiring the real embedding model (retrieve() is mocked so
this test runs offline/instantly — the real semantic search is exercised by
running `python -m app.rag.ingest` + the manual query script, see GUIDE.md).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.cv.parser import ParsedCV
from app.cv import matcher

FAKE_NURSE_HITS = [
    {
        "text": "Job title: Registered Nurse - ICU ...",
        "metadata": {"job_id": "JOB-006", "title": "Registered Nurse - ICU",
                      "profession": "Nurse", "specialty": "Intensive Care"},
        "distance": 0.12,
    },
]


def test_match_jobs_filters_by_profession(monkeypatch):
    captured = {}

    def fake_retrieve(query, k=5, doc_type=None, profession=None):
        captured["profession"] = profession
        captured["doc_type"] = doc_type
        return FAKE_NURSE_HITS

    monkeypatch.setattr(matcher, "retrieve", fake_retrieve)

    cv = ParsedCV(raw_text="...", profession="Nurse", job_title="Registered Nurse - ICU",
                  experience_years=3, skills=["ventilator management"])
    results = matcher.match_jobs(cv, k=5)

    # The matcher must always constrain retrieval to the candidate's own profession.
    assert captured["profession"] == "Nurse"
    assert captured["doc_type"] == "job"
    assert len(results) == 1
    assert results[0]["profession"] == "Nurse"
    assert results[0]["job_id"] == "JOB-006"
    assert 0 <= results[0]["match_score"] <= 100


def test_match_jobs_returns_empty_when_profession_unknown():
    cv = ParsedCV(raw_text="unrelated text", profession=None, job_title=None)
    assert matcher.match_jobs(cv) == []
