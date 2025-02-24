import faiss
import numpy as np

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

    def count(self):
        return self.index.ntotal