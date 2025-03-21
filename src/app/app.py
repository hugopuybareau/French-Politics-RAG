# src/app.py

import requests
import logging
import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.retrieval.retriever import retrieve
from src.retrieval.prompt_engineering import build_prompt

logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    # chunks: list

OLLAMA_SERVER_URL = "http://localhost:11434/api/generate"

@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    # user question from the request
    user_question = request.question.strip()
    if not user_question:
        raise HTTPException(status_code=400, detail="No question provided")
    
    # chunks_retrieved = retrieve(user_question, ranks=3)
    # if not chunks_retrieved: # maybe put a condition on the distance idk
    #     return AskResponse(
    #         answer="No article has been found where this subject is discussed.",
    #         chunks=[]
    #     )
    
    # chunks =[{
    #     "title": chunk[1].get("title","No title"),
    #     "link": chunk[1].get("link", "No link"),
    #     "distance": float(chunk[0])
    # } for chunk in chunks_retrieved]

    # prompt engineering
    # prompt_text = build_prompt(user_question, chunks_retrieved)
    prompt_text = f"You are a helpful chatbot. Answer the following message like a french human: {user_question}. Do not repeat the questions."

    # call the ollama server with the prompt
    payload = {
        "model": "mistral",
        "prompt": prompt_text,
        "raw": True,
        "stream": False
    }

    logging.info(f"[LOGGING] Sending payload: {payload}")

    try:
        response = requests.post(OLLAMA_SERVER_URL, json=payload, timeout=120)
        response.raise_for_status()
        logging.info(f"[LOGGING] Raw response content: {response.text}")
        
        # parse main response
        result_json = response.json()
        
        # 'response' field as a string
        generated_text = result_json.get("response", "")

    except requests.exceptions.JSONDecodeError as e:
        logging.error(f"[ERROR] JSON decode error: {str(e)}")
        raise HTTPException(status_code=500, detail="Invalid JSON response from Ollama server")
    except requests.exceptions.RequestException as e:
        logging.error(f"[ERROR] Error calling Ollama server: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calling Ollama server: {str(e)}")

    if not generated_text:
        return AskResponse(answer="The LLM returned an empty answer or the server did not respond.")

    return AskResponse(answer=generated_text)