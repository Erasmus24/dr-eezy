"""
Checkpoint test: verifies Dr. Eezy's RAG answer pipeline, including the offline
"extractive fallback" it should use when the local Ollama server isn't running
(exactly what happens in this sandbox / CI, and a realistic scenario during a
live demo if Ollama isn't started yet).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.rag import chatbot
from app.rag.llm_client import OllamaClient, OllamaUnavailableError

FAKE_HITS = [
    {
        "text": "Registered Nurse - ICU role requires ventilator management and critical care monitoring.",
        "metadata": {"title": "Registered Nurse - ICU", "doc_type": "job"},
        "distance": 0.1,
    },
    {
        "text": "No employee should be scheduled for more than 3 consecutive night shifts.",
        "metadata": {"source": "roster_policy.md", "doc_type": "knowledge"},
        "distance": 0.2,
    },
]


class DeadOllamaClient(OllamaClient):
    def generate(self, prompt, system=""):
        raise OllamaUnavailableError("Ollama not running (expected in this test)")


class FakeWorkingLLM(OllamaClient):
    def generate(self, prompt, system=""):
        assert "CONTEXT" in prompt  # the retrieved context must be stuffed into the prompt
        assert "Dr. Eezy" in system  # the system prompt should set the assistant's persona
        return "Here is a friendly, grounded answer about ICU nursing shifts."


def fake_retrieve_by_doc_type(query, k=4, doc_type=None, profession=None):
    """Mimics the real retriever's doc_type filtering so tests reflect production
    behaviour (chatbot.answer() calls retrieve() once per doc_type)."""
    return [h for h in FAKE_HITS if h["metadata"]["doc_type"] == doc_type]


def test_answer_falls_back_gracefully_when_ollama_unavailable(monkeypatch):
    monkeypatch.setattr(chatbot, "retrieve", fake_retrieve_by_doc_type)

    result = chatbot.answer("What does the ICU nurse role require?",
                             profession="Nurse", llm_client=DeadOllamaClient())

    assert result["used_local_llm"] is False
    assert "ICU" in result["answer"] or "ventilator" in result["answer"].lower()
    assert len(result["sources"]) == 2


def test_answer_uses_llm_when_available(monkeypatch):
    monkeypatch.setattr(chatbot, "retrieve", fake_retrieve_by_doc_type)

    result = chatbot.answer("What does the ICU nurse role require?",
                             profession="Nurse", llm_client=FakeWorkingLLM())

    assert result["used_local_llm"] is True
    assert result["answer"] == "Here is a friendly, grounded answer about ICU nursing shifts."
