import requests
import os
from app.utils.logger import get_logger

# Initialize logger
logger = get_logger("ollama_llm")

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")  # Default model


def get_llm_response(prompt: str) -> str:
    """
    Get response from Ollama LLM service
    """
    logger.info("ollama_request_initiated",
                model=OLLAMA_MODEL,
                api_url=OLLAMA_API_URL,
                prompt_length=len(prompt))
    
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        
        logger.info("sending_request_to_ollama",
                    model=OLLAMA_MODEL,
                    url=f"{OLLAMA_API_URL}/api/chat")
        
        response = requests.post(
            f"{OLLAMA_API_URL}/api/chat",
            json=payload,
            timeout=30  # Add timeout
        )
        
        logger.info("ollama_response_received",
                    status_code=response.status_code,
                    model=OLLAMA_MODEL)
        
        response.raise_for_status()
        
        response_data = response.json()
        llm_content = response_data["message"]["content"]
        
        logger.info("ollama_response_processed",
                    model=OLLAMA_MODEL,
                    response_length=len(llm_content),
                    prompt_length=len(prompt))
        
        return llm_content
        
    except requests.exceptions.Timeout as e:
        logger.error("ollama_request_timeout",
                     model=OLLAMA_MODEL,
                     api_url=OLLAMA_API_URL,
                     error=str(e))
        raise Exception(f"Ollama service timeout: {str(e)}")
        
    except requests.exceptions.ConnectionError as e:
        logger.error("ollama_connection_error",
                     model=OLLAMA_MODEL,
                     api_url=OLLAMA_API_URL,
                     error=str(e))
        raise Exception(f"Cannot connect to Ollama service: {str(e)}")
        
    except requests.exceptions.HTTPError as e:
        logger.error("ollama_http_error",
                     model=OLLAMA_MODEL,
                     api_url=OLLAMA_API_URL,
                     status_code=response.status_code,
                     error=str(e))
        raise Exception(f"Ollama service HTTP error: {str(e)}")
        
    except KeyError as e:
        logger.error("ollama_response_parsing_error",
                     model=OLLAMA_MODEL,
                     error=str(e),
                     response_data=response_data if 'response_data' in locals() else "unavailable")
        raise Exception(f"Unexpected Ollama response format: {str(e)}")
        
    except Exception as e:
        logger.error("ollama_unexpected_error",
                     model=OLLAMA_MODEL,
                     api_url=OLLAMA_API_URL,
                     error=str(e))
        raise Exception(f"Unexpected error communicating with Ollama: {str(e)}")