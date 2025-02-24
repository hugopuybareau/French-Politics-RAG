import re
import os
import json
from sentence_transformers import SentenceTransformer
from faiss_setup import *

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

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def get_embedding(text: str):
    return model.encode([text])[0].tolist() #Wrap it in a list so the single string test vector doesn't
                                            #generate a float instead of a 1D-np.ndarray. 
    
def build_index_from_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        articles = json.load(f)

    test_vector = get_embedding("test is cool")
    print(test_vector)
    vector_dim = len(test_vector)
    # vector_dim = 1536

    index = FaissIndex(vector_dim=vector_dim)

    article_id = 0
    for article in articles:
        text = article.get("content", '')
        text = clean_text(text)
        chunks = chunk_text(text, chunk_size=300, overlap=50)

        vectors = []
        metadata_list = []

        chunk_id = 0
        for chunk in chunks:
            chunk_emb = get_embedding(chunk)
            vectors.append(chunk_emb)
            meta = {
                "article_id" : article_id,
                "chunk_id" : chunk_id,
                "title" : article.get('title', ''),
                "link" : article.get('link',''),
                "text" : chunk
            }
            metadata_list.append(meta)
            chunk_id += 1
        
        index.add(vectors, metadata_list)
        article_id += 1

        print(f"Index build OK, with {index.count()} chunks.")
    return index

# TEST
if __name__ == "__main__" : 
    path = "../../data/raw/french_politics_22-02-2025_10-48-43.json"
    faiss_index = build_index_from_json(path)

    # Test a query
    query = "Nouvelle calédonie"
    query_emb = get_embedding(query)
    results = faiss_index.search(query_emb, ranks=3)
    for dist, meta in results:
        print(f"Distance: {dist:.2f}")
        print(f"Title: {meta['title']}")
        print(f"Snippet: {meta['text'][:200]}...\n")
