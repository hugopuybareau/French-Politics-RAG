# src/preprocess/preprocess.py

import re
import os
import json
import sys

from ..faiss.faiss_setup import FaissIndex
from ..embeddings.embedding import *

def clean_text(text: str) -> str:

    text = re.sub(r"<.*?>", "", text) # HTML marks just in case
    text = re.sub(r"\s+", " ", text, flags=re.MULTILINE) # Multiple spaces/lines
    text = text.strip()

    return text

def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    
    words = text.split()
    chunks = []
    start_idx = 0

    while start_idx < len(words):
        end_idx = start_idx + chunk_size
        chunk_words = words[start_idx:end_idx]
        chunks.append(" ".join(chunk_words))
        start_idx += chunk_size - overlap

    return chunks

def process_json_file(json_path: str): #Just returns (vectors, metadata)
    # Reads the json
    with open(json_path, "r", encoding="utf-8") as f:
        articles = json.load(f)

    all_vectors = []
    all_metadata = []

    # Cleans and chucks the text
    for article_id, article in enumerate(articles):
        content = article.get("content", '')

        content = clean_text(content)
        chunks = chunk_text(content, chunk_size=300, overlap=50)

        for chunk_id, chunk in enumerate(chunks):
            vector = get_embedding(chunk)
            all_vectors.append(vector)
            meta = {
                "article_id" : f"{json_path}#{article_id}",
                "article_key" : article.get("link", "") + "#" + str(chunk_id),
                "title" : article.get("title", ""),
                "link" : article.get("link", ""),
                "chunk_id" : chunk_id,
                "text" : chunk
            }
            all_metadata.append(meta)
    return (all_vectors, all_metadata)

# TEST
if __name__ == "__main__" : 
    path = "../../data/raw/french_politics_22-02-2025_10-48-43.json"
    faiss_index = process_json_file(path)

    # Test a query
    query = "Nouvelle calédonie"
    query_emb = get_embedding(query)
    results = faiss_index.search(query_emb, ranks=3)
    for dist, meta in results:
        print(f"Distance: {dist:.2f}")
        print(f"Title: {meta['title']}")
        print(f"Snippet: {meta['text'][:200]}...\n")
