# src/retrieval/retriever.py

import os
import faiss
import json
import numpy as np

from ..embeddings.embedding import *
from ..faiss.faiss_setup import FaissIndex

INDEX_DIR = os.path.join("data/index")
INDEX_PATH = os.path.join(INDEX_DIR, "faiss.index")
META_PATH = os.path.join(INDEX_DIR, "faiss_meta.json")

# Load the Faiss index
try:
    print("[INFO] Loading the Faiss index & metadata ...")
    faiss_index = FaissIndex.load(INDEX_PATH, META_PATH)
    print(f"[INFO] Loaded the index with {faiss_index.size} vectors.")
except FileNotFoundError:
    faiss_index = None
    print("[INFO] Index not found.")


def retrieve(query: str, ranks: int):
    if not faiss_index:
        print("[INFO] No index loaded.")
        return []

    query_vector = get_embedding(query)
    results = faiss_index.search(query_vector, ranks)

    return results

