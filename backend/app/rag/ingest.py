"""
Builds the Chroma vector store Dr. Eezy uses for retrieval-augmented generation (RAG).

Two kinds of content get embedded into the same collection, tagged with a `doc_type`
metadata field so retrieval can filter or weight them differently later:

  - "job"       -> one chunk per job posting in data/jobs.json
  - "knowledge" -> chunks of the markdown files in data/knowledge_base/

Embeddings are produced locally with sentence-transformers (all-MiniLM-L6-v2, ~80MB,
open-source, Apache 2.0 license) — no external API calls, no cost.

Run with:  cd backend && source .venv/bin/activate && python -m app.rag.ingest
"""
import glob
import json
import os

import chromadb
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..")
DATA_DIR = os.path.join(BASE_DIR, "data")
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")
COLLECTION_NAME = "dr_eezy_knowledge"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

_embedder = None


def get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedder


def get_chroma_client():
    return chromadb.PersistentClient(path=CHROMA_DIR)


def get_or_create_collection(client=None):
    client = client or get_chroma_client()
    return client.get_or_create_collection(name=COLLECTION_NAME)


def _chunk_markdown(text: str, chunk_size: int = 600, overlap: int = 100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return [c.strip() for c in chunks if c.strip()]


def load_job_documents():
    jobs_path = os.path.join(DATA_DIR, "jobs.json")
    with open(jobs_path, "r") as f:
        jobs = json.load(f)

    docs, metadatas, ids = [], [], []
    for job in jobs:
        text = (
            f"Job title: {job['title']} ({job['profession']} - {job['specialty']}).\n"
            f"Location: {job['location']}. Employment type: {job['employment_type']}. "
            f"Shift type: {job['shift_type']}.\n"
            f"Minimum experience: {job['min_experience_years']} years.\n"
            f"Required skills: {', '.join(job['required_skills'])}.\n"
            f"Salary range: {job['salary_range']}.\n"
            f"Description: {job['description']}"
        )
        docs.append(text)
        metadatas.append({
            "doc_type": "job",
            "job_id": job["id"],
            "title": job["title"],
            "profession": job["profession"],
            "specialty": job["specialty"],
        })
        ids.append(f"job-{job['id']}")
    return docs, metadatas, ids


def load_knowledge_documents():
    docs, metadatas, ids = [], [], []
    kb_files = sorted(glob.glob(os.path.join(DATA_DIR, "knowledge_base", "*.md")))
    for path in kb_files:
        fname = os.path.basename(path)
        with open(path, "r") as f:
            text = f.read()
        for i, chunk in enumerate(_chunk_markdown(text)):
            docs.append(chunk)
            metadatas.append({"doc_type": "knowledge", "source": fname})
            ids.append(f"kb-{fname}-{i}")
    return docs, metadatas, ids


def build_index(reset: bool = True):
    client = get_chroma_client()

    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass

    collection = get_or_create_collection(client)
    embedder = get_embedder()

    job_docs, job_meta, job_ids = load_job_documents()
    kb_docs, kb_meta, kb_ids = load_knowledge_documents()

    all_docs = job_docs + kb_docs
    all_meta = job_meta + kb_meta
    all_ids = job_ids + kb_ids

    embeddings = embedder.encode(all_docs, show_progress_bar=False).tolist()

    collection.add(
        documents=all_docs,
        metadatas=all_meta,
        ids=all_ids,
        embeddings=embeddings,
    )

    return {
        "jobs_indexed": len(job_docs),
        "knowledge_chunks_indexed": len(kb_docs),
        "total_indexed": len(all_docs),
        "collection_count": collection.count(),
    }


if __name__ == "__main__":
    stats = build_index(reset=True)
    print("Ingestion complete:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
