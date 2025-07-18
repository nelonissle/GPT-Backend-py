from datetime import datetime
import os
from bson import ObjectId
import jwt
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.services.ollama_llm import get_llm_response  # Import the function to interact with Ollama

# JWT-Konfiguration (soll mit dem Auth-Service übereinstimmen)
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

router = APIRouter()
security = HTTPBearer()

def verify_token(token: str):
    """
    Verifiziert das JWT und gibt die dekodierte Payload zurück.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Ungültiger oder abgelaufener Token")

# Pydantic-Modelle
class NewChatRequest(BaseModel):
    initial_query: str  # Die erste Benutzeranfrage

class ChatMessageInput(BaseModel):
    chat_id: Optional[str] = None  # Falls nicht angegeben, wird der aktivste Chat verwendet
    role: str                     # "user" oder "llm"
    text: str                     # Nachrichtentext

@router.post("/new")
async def new_chat(request: NewChatRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Benutzername nicht im Token gefunden")
    
    # Erstellen des Chat-Namens: Die ersten drei Wörter der initial_query
    words = request.initial_query.split()
    chat_name = " ".join(words[:3]) if len(words) >= 3 else request.initial_query

    # Zusammenstellen des Chat-Dokuments
    now = datetime.utcnow()
    llm_response = get_llm_response(request.initial_query)  # Get response from Ollama
    chat_doc = {
        "chat_name": chat_name,
        "timestamp": now,
        "messages": [
            {
                "role": "user",
                "text": request.initial_query,
                "timestamp": now
            },
            {
                "role": "llm",
                "text": llm_response,
                "timestamp": now
            }
        ]
    }
    
    # Benutzer-Collection in MongoDB (wird automatisch erstellt, falls nicht vorhanden)
    db = get_db()
    user_collection = db[username]
    result = user_collection.insert_one(chat_doc)
    
    return {"message": "Neuer Chat erstellt", "chat_id": str(result.inserted_id)}

@router.post("/add")
async def add_message(message: ChatMessageInput, credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Benutzername nicht im Token gefunden")
    
    db = get_db()
    user_collection = db[username]
    
    # Wenn keine chat_id angegeben wurde, nutze den zuletzt erstellten (aktiven) Chat
    if message.chat_id is None:
        active_chat = user_collection.find_one(sort=[("timestamp", -1)])
        if active_chat is None:
            raise HTTPException(status_code=404, detail="Kein aktiver Chat gefunden. Bitte erstelle einen neuen Chat.")
        chat_id = active_chat["_id"]
    else:
        chat_id = ObjectId(message.chat_id)

    now = datetime.utcnow()
    update_result = user_collection.update_one(
        {"_id": chat_id},
        {
            # Neue Nachricht anhängen
            "$push": {
                "messages": {
                    "role": message.role,
                    "text": message.text,
                    "timestamp": now
                }
            },
            # Chat-Timestamp bumpen, damit es als aktiv gilt
            "$set": {"timestamp": now}
        }
    )
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Chat nicht gefunden")
    
    return {"message": "Nachricht erfolgreich hinzugefügt", "chat_id": str(chat_id)}

@router.get("/history")
async def chat_history(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Benutzername nicht im Token gefunden")
    
    db = get_db()
    user_collection = db[username]
    raw = user_collection.find().sort("timestamp", -1)
    
    chats = []
    for doc in raw:
        last_msg = doc["messages"][-1]
        chats.append({
            "chat_id": str(doc["_id"]),
            "chat_name": doc["chat_name"],
            "last_message": last_msg["text"],
            "last_timestamp": last_msg["timestamp"]
        })
    return chats

@router.get("/{chat_id}")
async def get_chat(chat_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Benutzername nicht im Token gefunden")

    db = get_db()
    user_collection = db[username]
    chat = user_collection.find_one({"_id": ObjectId(chat_id)})
    if not chat:
        raise HTTPException(status_code=404, detail="Chat nicht gefunden")
    chat["_id"] = str(chat["_id"])
    return chat