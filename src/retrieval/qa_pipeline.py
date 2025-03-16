# src/retrieval/qa_pipeline.py

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
from typing import List, Tuple, Dict

from src.retrieval.retriever import retrieve

model_name = "EleutherAI/gpt-neo-1.3B"
print(f"[INFO] Loading {model_name} and the tokenizer...")

# GPU 
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load the model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name) 
model = AutoModelForCausalLM.from_pretrained(
    model_name,
).to(device)
print(f"[INFO] Loading OK")


# Generation config
generation_config = GenerationConfig(
    temperature=0.2,
    max_new_tokens=512,
    max_lenght=2048,
    do_sample=True,
    top_p=0.9,
)

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
            f"Link: {link}\n"
            # f"{chunk_text}\n\n"
        )

    user_question = f"Question: {question}\n\n"
    prompt = instructions + context_str + user_question + "Answer:"
    return prompt

def answer_question(question: str, ranks: int):
    retrieved_chunks = retrieve(question, ranks)
    if not retrieved_chunks:
        return ValueError("[ERROR] Problem with the index. No chunks retrieved.")
    
    prompt_text = build_prompt(question, retrieved_chunks)
    inputs = tokenizer(prompt_text, return_tensors="pt").to(device)

    # Generation
    with torch.no_grad(): # No need to compute gradients so we can save memory
        outputs = model.generate(
            **inputs,
            generation_config=generation_config
        )
    print(f"[INFO] Generated {len(outputs)} outputs")

    # Decoding
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # We only want the answer
    answer_split = answer.split("Answer:")
    if len(answer_split) > 1:
        answer = answer_split[1].strip()

    return answer


# Testing
if __name__ == "__main__":
    test_q = "Parle moi des news parues sur la compagnie du Mississippi"
    print(f"[INFO] Q: {test_q}")
    ans = answer_question(test_q, ranks=3)
    print("Answer:", ans)