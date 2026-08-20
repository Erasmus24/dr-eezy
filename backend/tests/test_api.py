"""
Checkpoint tests for the full FastAPI wiring: /health, /jobs, /cv/upload, /chat,
/roster/generate, /roster/pdf.

The RAG-dependent calls (retrieve()) are monkeypatched so this suite runs fully
offline/instantly, without needing the embedding model download or Ollama running
— exactly like a CI environment. Once you have real internet + Ollama running
locally (see GUIDE.md), hit the same endpoints with curl or /docs to see live
semantic answers instead of the mocked ones.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient

from app import main as main_module
from app.cv import matcher as matcher_module
from app.rag import chatbot as chatbot_module

client = TestClient(main_module.app)

SAMPLE_CV = os.path.join(os.path.dirname(__file__), "..", "data", "sample_cvs", "cv_palesa_mokoena.pdf")

FAKE_NURSE_HITS = [
    {
        "text": "Job title: Registered Nurse - ICU ...",
        "metadata": {"job_id": "JOB-006", "title": "Registered Nurse - ICU",
                      "profession": "Nurse", "specialty": "Intensive Care"},
        "distance": 0.1,
    },
]


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_list_jobs():
    r = client.get("/jobs")
    assert r.status_code == 200
    jobs = r.json()
    assert len(jobs) == 10
    assert {j["profession"] for j in jobs} == {"Doctor", "Nurse"}


def test_cv_upload_and_match(monkeypatch):
    monkeypatch.setattr(matcher_module, "retrieve", lambda *a, **k: FAKE_NURSE_HITS)

    with open(SAMPLE_CV, "rb") as f:
        r = client.post("/cv/upload", files={"file": ("cv_palesa_mokoena.pdf", f, "application/pdf")})

    assert r.status_code == 200
    body = r.json()
    assert body["profession"] == "Nurse"
    assert body["job_title"] == "Registered Nurse - ICU"
    assert len(body["matches"]) == 1
    assert body["matches"][0]["profession"] == "Nurse"


def test_chat_endpoint(monkeypatch):
    monkeypatch.setattr(chatbot_module, "retrieve", lambda *a, **k: FAKE_NURSE_HITS)

    r = client.post("/chat", json={"message": "What does an ICU nurse do?", "profession": "Nurse"})
    assert r.status_code == 200
    body = r.json()
    assert "answer" in body
    assert isinstance(body["used_local_llm"], bool)


def test_chat_rejects_empty_message():
    r = client.post("/chat", json={"message": "   "})
    assert r.status_code == 400


def test_roster_generate_and_pdf():
    payload = {"start_date": "2026-08-24", "num_days": 7}

    r = client.post("/roster/generate", json=payload)
    assert r.status_code == 200
    roster = r.json()
    assert "Registered Nurse - ICU" in roster
    assert len(roster["Registered Nurse - ICU"]["dates"]) == 7

    r2 = client.post("/roster/pdf", json=payload)
    assert r2.status_code == 200
    assert r2.headers["content-type"] == "application/pdf"
    assert r2.content[:4] == b"%PDF"
