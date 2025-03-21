# src/faiss/build_update_index.py

import os
import glob

from src.faiss.faiss_setup import FaissIndex
from src.preprocess.preprocess import process_json_file

INDEX_DIR = "data/index"
INDEX_PATH = os.path.join(INDEX_DIR, "faiss.index")
META_PATH = os.path.join(INDEX_DIR, "faiss_meta.json")

def build_or_update_index(index_type="flat"):

    os.makedirs(INDEX_DIR, exist_ok=True)

    try:
        print(f"[INFO] Attempting to load existing {index_type} index and metadata ...")
        my_index = FaissIndex.load(INDEX_PATH, META_PATH, index_type)
        print(f"[INFO] Loaded existing {index_type} index with {my_index.size} vectors.")
    except FileNotFoundError:
        print(f"[INFO] No existing {index_type} index found. We'll create a new one.")
        my_index = None

    # Process JSON files in data/raw/
    raw_files = glob.glob("data/raw/*.json")
    print(f"[INFO] Found {len(raw_files)} raw JSON files: {raw_files}")

    total_new_chunks = 0

    for json_path in raw_files:
        print(f"[INFO] Processing {json_path} ...")
        vectors, metadata = process_json_file(json_path)

        final_vectors = []
        final_metadata = []

        for vec, meta in zip(vectors, metadata):
            article_key = meta["article_key"]
            print(f"   [INFO] Treating article_key={article_key}")

            # If we already have an index, skip duplicates
            if my_index and my_index.article_already_indexed(article_key):
                print(f"   [INFO] Skipping duplicate article: {article_key}")
                continue

            final_vectors.append(vec)
            final_metadata.append(meta)

        if not final_vectors:
            print(f"[INFO] No new articles in {json_path}. Skipping.")
            continue

        # Index doesn't exist yet
        if not my_index:
            dim = len(final_vectors[0])
            print(f"[INFO] Creating a new {index_type} FaissIndex with dim={dim}")
            my_index = FaissIndex(vector_dim=dim, index_type=index_type)

        # Add the new vectors/metadata
        my_index.add(final_vectors, final_metadata)
        total_new_chunks += len(final_vectors)

    # 5) Save the updated index (if it exists at all)
    if my_index:
        print(f"[INFO] Saving updated {index_type} index with {my_index.size} vectors...")
        my_index.save(INDEX_PATH, META_PATH)
    else:
        print("[INFO] Nothing to index. No index saved.")

    print(f"[INFO] Added {total_new_chunks} new chunks overall.")

if __name__ == "__main__":
    build_or_update_index(index_type="hnsw")