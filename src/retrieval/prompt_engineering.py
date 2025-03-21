# src/retreival/prompt_engineering.py

from typing import List, Tuple

def build_prompt(question: str, retrieved_chunks: List[Tuple[float, dict]]) -> str:
    instructions = (
        "You are an AI assistant. You have been provided with the following context. "
        "Use this context to answer the user's question in French politics domain. "
        "If the answer is not in the context, say you do not know. "
        "Cite the relevant source if possible.\n\n"
    )

    context_str = "Context:\n"
    for i, (dist, meta) in enumerate(retrieved_chunks, start=1):
        chunk_text = meta.get("text", "")
        title = meta.get("title", "No title")
        link = meta.get("link", "No link")
        context_str += (
            f"[Source {i} - (distance : {dist:.2f})]\n"
            f"Title: {title}\n"
            # f"Link: {link}\n"
            # f"{chunk_text}\n\n"
        )

    user_question = f"Question: {question}\n\n"
    prompt = instructions + context_str + user_question + "Réponds à cette question maintenant:"
    return prompt