import os
import jwt
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from app.database import get_sql_db, get_mongo_db, Base

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
async def list_users(db: Session = Depends(get_sql_db)):
    users = db.query(User.id, User.username, User.role).all()
    return [{"id": u.id, "username": u.username, "role": u.role} for u in users]

# DELETE USER
@router.delete(
    "/admin/users/{username}",
    dependencies=[Depends(verify_developer_token)],
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user(
    username: str,
    db: Session = Depends(get_sql_db),
    mongo_db = Depends(get_mongo_db)
):
    # 1) remove from SQLite
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()

    # 2) drop their Mongo collection (all chats)
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
