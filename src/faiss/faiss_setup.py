# src/preprocess/faiss_setup.py

import faiss
import numpy as np
import json
import os

class FaissIndex:

    def __init__(self, vector_dim: int, index_type: str = "flat", M: int = 32, efConstruction: int = 200):
        self.vector_dim = vector_dim
        self.index_type = index_type.lower()
        self.embeddings = [] #For embeddings
        self.metadata = [] #Real data

        if self.index_type == "flat":
            self.index = faiss.IndexFlatL2(vector_dim)
        elif self.index_type == "hnsw":
            self.index = faiss.IndexHNSWFlat(vector_dim, M, faiss.METRIC_L2)
            self.index.hnsw.efConstruction = efConstruction
        else:
            raise ValueError("[ERROR] Invalid index type. Choose between 'flat' and 'hnsw'.")


    def add(self, vectors: list[list[float]], meta: list[dict]):
        arr = np.array(vectors, dtype=np.float32)
        self.index.add(arr)
        self.metadata.extend(meta)
    

    def search(self, query_vector: list[float], ranks: int, efSearch=50):

        if self.index_type == "hnsw": # Set efSearch for HNSW
            self.index.hnsw.efSearch = efSearch

        arr = np.array([query_vector], dtype=np.float32)
        distances, indices = self.index.search(arr, ranks)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            meta = self.metadata[idx]
            results.append((dist, meta))
        return results
    

    def save(self, index_path, metadata_path):

        suffix = f"_{self.index_type}" if self.index_type != "flat" else ""
        index_path = index_path.replace(".index", f"{suffix}.index")
        metadata_path = metadata_path.replace(".json", f"{suffix}.json")
        faiss.write_index(self.index, index_path)

        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump({
                "metadata": self.metadata,
                "index_type": self.index_type, # We have to do that now because there could be 2
                "vector_dim": self.vector_dim
            }, f, indent=2, ensure_ascii=False)


    @classmethod
    def load(cls, index_path, metadata_path, index_type: str):
    
        suffix = f"_{index_type}" if index_type != "flat" else ""
        index_path = index_path.replace(".index", f"{suffix}.index")
        metadata_path = metadata_path.replace(".json", f"{suffix}.json")

        #Check
        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            raise FileNotFoundError("[ERROR] Index or metadata file not found.")
        
        # Load FAISS index
        faiss_index = faiss.read_index(index_path)
        vector_dim = faiss_index.d

        # Metadata to see what type we used
        with open(metadata_path, 'r', encoding='utf-8') as f:
            save_info = json.load(f)
        saved_metadata = save_info["metadata"]
        saved_index_type = save_info["index_type"]
        saved_vector_dim = save_info["vector_dim"]

        if saved_vector_dim != vector_dim:
            raise ValueError("[ERROR] Vector dimension mismatch between index and metadata.")
        if saved_index_type != index_type:
            raise ValueError(f"Index type mismatch: metadata says {saved_index_type}, but you asked for {index_type}.")

        # Instance
        obj = cls(vector_dim, saved_index_type)
        obj.index = faiss_index
        obj.metadata = saved_metadata

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
