# src/preprocess/faiss_setup.py

import faiss
import numpy as np
import json
import os

class FaissIndex:

    def __init__(self, vector_dim: int):
        self.index = faiss.IndexFlatL2(vector_dim)
        self.embeddings = [] #For embeddings
        self.metadata = [] #Real data


    def add(self, vectors: list[list[float]], meta: list[dict]):
        arr = np.array(vectors, dtype=np.float32)
        self.index.add(arr)
        self.metadata.extend(meta)
    

    def search(self, query_vector: list[float], ranks: int):
        arr = np.array([query_vector], dtype=np.float32)
        distances, indices = self.index.search(arr, ranks)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            meta = self.metadata[idx]
            results.append((dist, meta))
        return results
    

    def save(self, index_path, metadata_path):
        faiss.write_index(self.index, index_path)
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)


    @classmethod
    def load(cls, index_path, metadata_path):
        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            raise FileNotFoundError("[ERROR] Index or metadata file not found.")
    
        # Load FAISS index
        faiss_index = faiss.read_index(index_path)

        # Index dimension
        vector_dim = faiss_index.d
        obj = cls(vector_dim)
        obj.index = faiss_index

        # Load MetaData
        with open(metadata_path, 'r', encoding='utf-8') as f:
            obj.metadata = json.load(f)
            
        return obj


    @property
    def size(self):
        return self.index.ntotal
    

    def article_already_indexed(self, article_key: str) -> bool:
        for meta in self.metadata:
            article_id = meta.get("article_key", "")
            if article_id == article_key:
                return True
            return False

    