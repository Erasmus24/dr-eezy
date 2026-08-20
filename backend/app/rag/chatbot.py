"""
Dr. Eezy — the RAG chatbot for Medics Online.

Pipeline: retrieve relevant job postings / knowledge-base chunks from Chroma,
stuff them into a grounded prompt, and ask a local open-source LLM (via Ollama)
to answer using ONLY that retrieved context. If Ollama isn't reachable (e.g. not
installed yet, or momentarily down during a live demo), Dr. Eezy falls back to an
"extractive" answer built directly from the retrieved snippets, so the chat never
just dies mid-demo.
"""
from typing import List, Optional

from app.rag.llm_client import OllamaClient, OllamaUnavailableError
from app.rag.retriever import retrieve

SYSTEM_PROMPT = """You are Dr. Eezy, the friendly AI assistant for Medics Online, a \
recruitment platform for doctors and nurses. Answer ONLY using the CONTEXT provided \
below. If the context does not contain the answer, say you don't have that \
information and suggest the user contact Medics Online support. Always be clear \
about whether you are talking about a Doctor role or a Nurse role when relevant. \
Keep answers concise and friendly."""


def _format_context(hits: List[dict]) -> str:
    lines = []
    for i, hit in enumerate(hits, 1):
        meta = hit["metadata"]
        label = meta.get("title") or meta.get("source") or meta.get("doc_type")
        lines.append(f"[{i}] ({label}) {hit['text']}")
    return "\n\n".join(lines)


def _extractive_fallback(question: str, hits: List[dict]) -> str:
    if not hits:
        return ("I couldn't find anything relevant in the Medics Online knowledge base "
                "for that question. Could you rephrase, or ask about a specific job title?")
    top = hits[0]
    meta = top["metadata"]
    label = meta.get("title") or meta.get("source") or "this topic"
    return (f"(Offline mode — local LLM unavailable, showing the most relevant match)\n\n"
            f"Regarding **{label}**: {top['text'][:400]}")


def answer(question: str, profession: Optional[str] = None,
           llm_client: Optional[OllamaClient] = None, k: int = 4) -> dict:
    """
    Args:
        question: the user's chat message.
        profession: optional "Doctor"/"Nurse" filter, applied only to job postings
                    (knowledge-base docs are always searched unfiltered).
        llm_client: inject a client for testing; defaults to a real OllamaClient.
        k: number of context chunks to retrieve.
    """
    llm_client = llm_client or OllamaClient()

    job_hits = retrieve(question, k=k, doc_type="job", profession=profession)
    kb_hits = retrieve(question, k=k, doc_type="knowledge")
    hits = (job_hits + kb_hits)[:k + 2]

    context = _format_context(hits)
    prompt = f"CONTEXT:\n{context}\n\nQUESTION: {question}\n\nAnswer as Dr. Eezy:"

    used_fallback = False
    try:
        reply_text = llm_client.generate(prompt, system=SYSTEM_PROMPT)
        if not reply_text:
            raise OllamaUnavailableError("Empty response from LLM")
    except OllamaUnavailableError:
        reply_text = _extractive_fallback(question, hits)
        used_fallback = True

    return {
        "answer": reply_text,
        "used_local_llm": not used_fallback,
        "sources": [
            {
                "label": h["metadata"].get("title") or h["metadata"].get("source"),
                "doc_type": h["metadata"].get("doc_type"),
            }
            for h in hits
        ],
    }
