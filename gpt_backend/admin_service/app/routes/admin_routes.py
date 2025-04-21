import os
import jwt
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from app.database import get_mongo_db, Base
import httpx

# --- JWT setup ---
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

router = APIRouter()
security = HTTPBearer()

def verify_developer_token(
    creds: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if payload.get("role") != "developer":
        raise HTTPException(status_code=403, detail="Developer role required")
    return payload

# --- reflect the users table from auth_service ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=False)

# LIST USERS
@router.get(
    "/admin/users",
    dependencies=[Depends(verify_developer_token)]
)
async def list_users():
    """
    Fetch the list of users from auth_service via Kong.
    """
    auth_service_url = os.getenv("AUTH_SERVICE_URL")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{auth_service_url}/users")
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to fetch users: {response.text}"
                )
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with auth_service: {str(e)}"
        )

# DELETE USER
@router.delete(
    "/admin/users/{username}",
    dependencies=[Depends(verify_developer_token)],
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user(
    username: str,
    mongo_db=Depends(get_mongo_db)
):
    # 1) Remove user via auth_service
    auth_service_url = os.getenv("AUTH_SERVICE_URL")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{auth_service_url}/users/{username}")
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="User not found")
            elif response.status_code != 204:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to delete user: {response.text}"
                )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with auth_service: {str(e)}"
        )

    # 2) Drop their MongoDB collection (all chats)
    if username in mongo_db.list_collection_names():
        mongo_db.drop_collection(username)

    return

# LIST CHATS
@router.get(
    "/admin/users/{username}/chats",
    dependencies=[Depends(verify_developer_token)]
)
async def list_user_chats(username: str, mongo_db = Depends(get_mongo_db)):
    if username not in mongo_db.list_collection_names():
        raise HTTPException(status_code=404, detail="User not found")
    coll = mongo_db[username]
    result = []
    for doc in coll.find().sort("timestamp", -1):
        result.append({
            "chat_id": str(doc["_id"]),
            "chat_name": doc["chat_name"],
            "last_timestamp": doc["timestamp"]
        })
    return {"chats": result}

# DELETE A SINGLE CHAT
@router.delete(
    "/admin/users/{username}/chats/{chat_id}",
    dependencies=[Depends(verify_developer_token)],
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user_chat(
    username: str,
    chat_id: str,
    mongo_db = Depends(get_mongo_db)
):
    if username not in mongo_db.list_collection_names():
        raise HTTPException(status_code=404, detail="User not found")
    coll = mongo_db[username]
    result = coll.delete_one({"_id": ObjectId(chat_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Chat not found")
    return

# FETCH A SINGLE CHAT
@router.get(
    "/admin/users/{username}/chats/{chat_id}",
    dependencies=[Depends(verify_developer_token)]
)
async def get_user_chat(username: str, chat_id: str, mongo_db = Depends(get_mongo_db)):
    if username not in mongo_db.list_collection_names():
        raise HTTPException(status_code=404, detail="User not found")
    coll = mongo_db[username]
    doc = coll.find_one({"_id": ObjectId(chat_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Chat not found")
    doc["_id"] = str(doc["_id"])
    return doc
