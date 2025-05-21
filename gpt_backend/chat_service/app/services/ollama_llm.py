import requests
import os

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")  # Default model

def get_llm_response(prompt: str) -> str:
    response = requests.post(
        f"{OLLAMA_API_URL}/api/chat",
        json={
            "model": OLLAMA_MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False  # <--- ADD THIS LINE
        }
    )
    response.raise_for_status()
    return response.json()["message"]["content"]