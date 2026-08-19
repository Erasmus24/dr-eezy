"""
Retrieval layer over the Chroma vector store built by ingest.py.
"""
from typing import List, Optional

from app.rag.ingest import get_chroma_client, get_embedder, COLLECTION_NAME


def retrieve(query: str, k: int = 4, doc_type: Optional[str] = None,
             profession: Optional[str] = None) -> List[dict]:
    """
    Semantic search over the knowledge base + job postings.

    Args:
        query: natural language question / search text.
        k: number of results to return.
        doc_type: optional filter, "job" or "knowledge".
        profession: optional filter, "Doctor" or "Nurse" (only applies to job docs).
    """
    client = get_chroma_client()
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    embedder = get_embedder()

    where = {}
    if doc_type and profession:
        where = {"$and": [{"doc_type": doc_type}, {"profession": profession}]}
    elif doc_type:
        where = {"doc_type": doc_type}
    elif profession:
        where = {"profession": profession}

    query_embedding = embedder.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=k,
        where=where or None,
    )

    hits = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]
    for doc, meta, dist in zip(docs, metas, dists):
        hits.append({"text": doc, "metadata": meta, "distance": dist})
    return hits
