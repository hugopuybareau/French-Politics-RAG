# src/preprocess/build_update_index.py

import os
import glob

from src.faiss.faiss_setup import FaissIndex
from src.preprocess.preprocess import process_json_file

INDEX_DIR = "data/index"
INDEX_PATH = os.path.join(INDEX_DIR, "faiss.index")
META_PATH = os.path.join(INDEX_DIR, "faiss_meta.json")

def build_or_update_index():
    os.makedirs(INDEX_DIR, exist_ok=True) # To be sure

    # Check if an index already exists
    if os.path.exists(INDEX_PATH) and os.path.exists(META_PATH):
        print("[INFO] Loading index and metadata ...")
        my_index = FaissIndex.load(INDEX_PATH, META_PATH)
    else: 
        print("[INFO] Bulding new index new metadata ...")
        my_index = None

    raw_files = glob.glob("data/raw/*.json")
    print(f"[INFO] {raw_files}")
    total_new_chunks = 0

    for json_path in raw_files:
        print(f"[INFO] Processing {json_path} ...")
        vectors, metadata = process_json_file(json_path)

        final_vectors = []
        final_metadata = []

        for vec, meta in zip(vectors, metadata):
            article_key = meta["article_key"]
            print(f"[INFO] Treating {article_key}")
            if my_index and my_index.article_already_indexed(article_key): #Skipping articles already indexed
                print(f"[INFO] Skipping {article_key}")
                continue

            final_vectors.append(vec)
            final_metadata.append(meta)

        if not final_vectors: #Skipping whole document
            print(f"[INFO] No new articles in {json_path}. Whole document skipped.")
            continue
    
        if not my_index: #Index not created
            from sentence_transformers import SentenceTransformer
            dim = len(final_vectors[0])
            my_index = FaissIndex(vector_dim=dim)

        # Add to the index
        my_index.add(final_vectors, final_metadata)
        total_new_chunks += len(final_vectors)
        
    if my_index:
        print(f"[INFO] Saving updated index with {my_index.size} vectors...")
        my_index.save(INDEX_PATH, META_PATH)
    else:
        print("[INFO] Nothing to index, nothing saved.")
    print(f"[INFO] Added {total_new_chunks} new chunks")

if __name__ == '__main__': 
    build_or_update_index()
    

    


