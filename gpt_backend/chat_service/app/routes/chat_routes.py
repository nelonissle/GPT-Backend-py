from datetime import datetime
import os
from bson import ObjectId
import jwt
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.services.ollama_llm import get_llm_response
from app.utils.logger import get_logger

# Initialize logger
logger = get_logger("chat_routes")

# JWT-Konfiguration (soll mit dem Auth-Service übereinstimmen)
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

router = APIRouter()
security = HTTPBearer()


def verify_token(token: str):
    """
    Verifiziert das JWT und gibt die dekodierte Payload zurück.
    """
    logger.info("verifying_jwt_token")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")
        logger.info("jwt_token_verified", username=username, role=role)
        return payload
    except jwt.PyJWTError as e:
        logger.warning("jwt_token_verification_failed", error=str(e))
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
    logger.info("new_chat_request", query_length=len(request.initial_query))
    
    token = credentials.credentials
    payload = verify_token(token)
    username = payload.get("sub")
    if not username:
        logger.warning("new_chat_failed", reason="username_not_in_token")
        raise HTTPException(status_code=401, detail="Benutzername nicht im Token gefunden")
    
    logger.info("creating_new_chat", username=username, query_preview=request.initial_query[:50])
    
    try:
        # Erstellen des Chat-Namens: Die ersten drei Wörter der initial_query
        words = request.initial_query.split()
        chat_name = " ".join(words[:3]) if len(words) >= 3 else request.initial_query
        
        logger.info("generating_chat_name", chat_name=chat_name, username=username)

        # Zusammenstellen des Chat-Dokuments
        now = datetime.utcnow()
        
        # Get response from Ollama
        logger.info("requesting_llm_response", username=username, query_length=len(request.initial_query))
        llm_response = get_llm_response(request.initial_query)
        logger.info("llm_response_received", username=username, response_length=len(llm_response))
        
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
        logger.info("saving_chat_to_database", username=username, chat_name=chat_name)
        db = get_db()
        user_collection = db[username]
        result = user_collection.insert_one(chat_doc)
        
        chat_id = str(result.inserted_id)
        logger.info("new_chat_created_successfully",
                    username=username,
                    chat_id=chat_id,
                    chat_name=chat_name,
                    message_count=len(chat_doc["messages"]))
        
        return {"message": "Neuer Chat erstellt", "chat_id": chat_id}
        
    except Exception as e:
        logger.error("new_chat_creation_failed", username=username, error=str(e))
        raise HTTPException(status_code=500, detail="Fehler beim Erstellen des neuen Chats")


@router.post("/add")
async def add_message(message: ChatMessageInput, credentials: HTTPAuthorizationCredentials = Depends(security)):
    logger.info("add_message_request",
                chat_id=message.chat_id,
                role=message.role,
                message_length=len(message.text))
    
    token = credentials.credentials
    payload = verify_token(token)
    username = payload.get("sub")
    if not username:
        logger.warning("add_message_failed", reason="username_not_in_token")
        raise HTTPException(status_code=401, detail="Benutzername nicht im Token gefunden")
    
    try:
        db = get_db()
        user_collection = db[username]
        
        # Wenn keine chat_id angegeben wurde, nutze den zuletzt erstellten (aktiven) Chat
        if message.chat_id is None:
            logger.info("finding_active_chat", username=username)
            active_chat = user_collection.find_one(sort=[("timestamp", -1)])
            if active_chat is None:
                logger.warning("add_message_failed", username=username, reason="no_active_chat_found")
                raise HTTPException(status_code=404, detail="Kein aktiver Chat gefunden. Bitte erstelle einen neuen Chat.")
            chat_id = active_chat["_id"]
            logger.info("using_active_chat", username=username, chat_id=str(chat_id))
        else:
            chat_id = ObjectId(message.chat_id)
            logger.info("using_specified_chat", username=username, chat_id=str(chat_id))

        now = datetime.utcnow()
        logger.info("updating_chat_with_message",
                    username=username,
                    chat_id=str(chat_id),
                    role=message.role)
        
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
            logger.warning("add_message_failed",
                           username=username,
                           chat_id=str(chat_id),
                           reason="chat_not_found")
            raise HTTPException(status_code=404, detail="Chat nicht gefunden")
        
        logger.info("message_added_successfully",
                    username=username,
                    chat_id=str(chat_id),
                    role=message.role,
                    message_length=len(message.text))
        
        return {"message": "Nachricht erfolgreich hinzugefügt", "chat_id": str(chat_id)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("add_message_error", username=username, error=str(e))
        raise HTTPException(status_code=500, detail="Fehler beim Hinzufügen der Nachricht")


@router.get("/history")
async def chat_history(credentials: HTTPAuthorizationCredentials = Depends(security)):
    logger.info("chat_history_request")
    
    token = credentials.credentials
    payload = verify_token(token)
    username = payload.get("sub")
    if not username:
        logger.warning("chat_history_failed", reason="username_not_in_token")
        raise HTTPException(status_code=401, detail="Benutzername nicht im Token gefunden")
    
    try:
        logger.info("fetching_chat_history", username=username)
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
        
        logger.info("chat_history_retrieved", username=username, chat_count=len(chats))
        return chats
        
    except Exception as e:
        logger.error("chat_history_error", username=username, error=str(e))
        raise HTTPException(status_code=500, detail="Fehler beim Abrufen der Chat-Historie")


@router.get("/{chat_id}")
async def get_chat(chat_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    logger.info("get_chat_request", chat_id=chat_id)
    
    token = credentials.credentials
    payload = verify_token(token)
    username = payload.get("sub")
    if not username:
        logger.warning("get_chat_failed", chat_id=chat_id, reason="username_not_in_token")
        raise HTTPException(status_code=401, detail="Benutzername nicht im Token gefunden")

    try:
        logger.info("fetching_specific_chat", username=username, chat_id=chat_id)
        db = get_db()
        user_collection = db[username]
        chat = user_collection.find_one({"_id": ObjectId(chat_id)})
        
        if not chat:
            logger.warning("get_chat_failed", username=username, chat_id=chat_id, reason="chat_not_found")
            raise HTTPException(status_code=404, detail="Chat nicht gefunden")
        
        chat["_id"] = str(chat["_id"])
        message_count = len(chat.get("messages", []))
        
        logger.info("chat_retrieved_successfully",
                    username=username,
                    chat_id=chat_id,
                    chat_name=chat.get("chat_name"),
                    message_count=message_count)
        
        return chat
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_chat_error", username=username, chat_id=chat_id, error=str(e))
        raise HTTPException(status_code=500, detail="Fehler beim Abrufen des Chats")