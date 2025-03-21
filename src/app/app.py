# src/app.py

import requests

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.retrieval.retriever import retrieve
from src.retrieval.prompt_engineering import build_prompt

app = FastAPI()

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    chunks: list

OLLAMA_SERVER_URL = ""

@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    # user question from the request
    user_question = request.question.strip()
    if not user_question:
        raise HTTPException(status_code=400, detail="No question provided")
    
    chunks_retrieved = retrieve(user_question, ranks=3)
    if not chunks_retrieved: # maybe put a condition on the distance idk
        return AskResponse(
            answer="No article has been found where this subject is discussed.",
            chunks=[]
        )
    
    chunks =[{
        "title": chunk[1].get("title","No title"),
        "link": chunk[1].get("link", "No link"),
        "distance": float(chunk[0])
    } for chunk in chunks_retrieved]

    return AskResponse(answer="Pour l'instant je teste juste avec les chunks:", chunks=chunks)

    # # prompt engineering
    # prompt_text = build_prompt(user_question, chunks_retrieved)

    # # call the go server with the prompt
    # payload = {"prompt": prompt_text}

    # try:
    #     response = requests.post(OLLAMA_SERVER_URL, json=payload, timeout=120)
    #     response.raise_for_status()
    # except requests.exceptions.RequestException as e:
    #     raise HTTPException(status_code=500, detail=f"Error calling Go/Ollama server: {str(e)}")

    # # 4) Parse the Go server’s response.
    # # We'll assume the Go server returns JSON: {"generated_text": "..."}
    # result_json = response.json()
    # generated_text = result_json.get("generated_text", "")

    # if not generated_text:
    #     return AskResponse(answer="The LLM returned an empty answer or the server did not respond.")

    # # 5) Return that text as the final answer
    # return AskResponse(answer=generated_text)