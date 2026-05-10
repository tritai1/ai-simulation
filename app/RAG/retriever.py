from __future__ import annotations

import pickle
from functools import lru_cache
from typing import List, Tuple

import numpy as np

from app.RAG.embeddings import embed_text


@lru_cache(maxsize=1)
def _load_assets() -> Tuple[object, List[str]]:
    import faiss

    index = faiss.read_index("data/processed/faiss.index")
    with open("data/processed/documents.pkl", "rb") as f:
        documents = pickle.load(f)
    return index, documents


def retrieve_context(
    query: str,
    k: int = 3
):
    index, documents = _load_assets()
    query_embedding = embed_text(query)

    query_vector = np.array(
        [query_embedding],
        dtype="float32"
    )

    distances, indices = index.search(
        query_vector,
        k
    )

    results = []

    for idx in indices[0]:

        if idx == -1:
            continue

        if idx >= len(documents):
            continue

        results.append(
            documents[idx]
        )

    return "\n".join(results)