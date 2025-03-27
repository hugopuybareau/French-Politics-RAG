# backend/chat/utils.py

from ollama import chat


def get_mistral_response(message: str) -> str:

    return f"Echo: {message}"