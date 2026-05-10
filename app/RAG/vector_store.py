import faiss
import numpy as np
import pickle

dimension = 384
index = faiss.IndexFlatL2(
    dimension
)
documents = []

def add_vectors(vectors, texts):
    global documents
    np_vectors = np.array(vectors).astype(
        "float32"
    )

    index.add(np_vectors)
    documents.extend(texts)
    
def save_index():

    faiss.write_index(
        index,
        r"D:\ai-simulation\data\raw\faiss.index"
    )

    with open(
        r"D:\ai-simulation\data\raw\documents.pkl",
        "wb"
    ) as f:

        pickle.dump(documents, f)

def load_index():

    global index
    global documents


    index = faiss.read_index(
         r"D:\ai-simulation\data\raw\faiss.index"
    )
    with open(
        r"D:\ai-simulation\data\raw\documents.pkl",
        "rb"
    ) as f:

        documents = pickle.load(f)