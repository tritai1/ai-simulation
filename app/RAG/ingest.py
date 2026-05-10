from pathlib import Path
import sys

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from apps.RAG.documents import load_all_documents
from apps.RAG.chunking import split_documents
from apps.RAG.embeddings import embed_text
from apps.RAG.vector_store import add_vectors, save_index


def ingest_documents():

    docs = load_all_documents()
    chunks = split_documents(docs)

    texts = []
    vectors = []


    for chunk in chunks:
        text = chunk.page_content
        vector = embed_text(text)
        texts.append(text)
        vectors.append(vector)

    add_vectors(vectors, texts)

    save_index()
    print("TOTAL DOCS:", len(docs))
    print("RAG ingestion complete")

if __name__ == "__main__":

    ingest_documents()
