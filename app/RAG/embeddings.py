from sentence_transformers import (
    SentenceTransformer
)


embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)



def embed_text(text):

    return embedding_model.encode(text)