import os
import jwt
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from app.database import get_mongo_db, Base
from app.utils.logger import get_logger
import httpx

# Initialize logger
logger = get_logger("admin_routes")

# --- JWT setup ---
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

auth_service = os.getenv("AUTH_SERVICE_URL", "/auth")
kong_host = os.getenv("KONG_GATEWAY_SERVICE_SERVICE_HOST", "localhost")
kong_port = os.getenv("KONG_GATEWAY_SERVICE_SERVICE_PORT", "8000")
auth_service_url = f"http://{kong_host}:{kong_port}{auth_service}"

router = APIRouter()
security = HTTPBearer()


def verify_developer_token(
    creds: HTTPAuthorizationCredentials = Depends(security)
):
    logger.info("verifying_developer_token")
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")
        
        if role != "developer":
            logger.warning("developer_access_denied", username=username, role=role)
            raise HTTPException(status_code=403, detail="Developer role required")
        
        logger.info("developer_token_verified", username=username, role=role)
        return payload
        
    except jwt.PyJWTError as e:
        logger.warning("developer_token_verification_failed", error=str(e))
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# --- reflect the users table from auth_service ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=False)


# LIST USERS
@router.get(
    "/users",
    dependencies=[Depends(verify_developer_token)]
)
async def list_users(request: Request):
    logger.info("admin_list_users_request")
    
    token = request.headers.get("authorization")
    
    try:
        logger.info("requesting_users_from_auth_service", auth_service_url=auth_service_url)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{auth_service_url}/users",
                headers={"Authorization": token}
            )
            
            logger.info("auth_service_response_received",
                        status_code=response.status_code,
                        auth_service_url=auth_service_url)
            
            if response.status_code != 200:
                logger.error("auth_service_users_request_failed",
                             status_code=response.status_code,
                             response_text=response.text)
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to fetch users: {response.text}"
                )
            
            users_data = response.json()
            user_count = len(users_data) if isinstance(users_data, list) else "unknown"
            
            logger.info("users_list_retrieved_successfully",
                        user_count=user_count,
                        auth_service_url=auth_service_url)
            
            return users_data
            
    except httpx.RequestError as e:
        logger.error("auth_service_communication_error",
                     auth_service_url=auth_service_url,
                     error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with auth_service: {str(e)}"
        )


# DELETE USER
@router.delete(
    "/users/{username}",
    dependencies=[Depends(verify_developer_token)],
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user(username: str, request: Request, mongo_db=Depends(get_mongo_db)):
    logger.info("admin_delete_user_request", target_username=username)
    
    token = request.headers.get("authorization")

    # 1) Remove user via auth_service
    try:
        logger.info("deleting_user_from_auth_service",
                    target_username=username,
                    auth_service_url=auth_service_url)
        
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{auth_service_url}/users/{username}",
                headers={"Authorization": token}
            )
            
            logger.info("auth_service_delete_response_received",
                        target_username=username,
                        status_code=response.status_code)
            
            if response.status_code == 404:
                logger.warning("user_not_found_in_auth_service", target_username=username)
                raise HTTPException(status_code=404, detail="User not found")
            elif response.status_code != 204:
                logger.error("auth_service_delete_failed",
                             target_username=username,
                             status_code=response.status_code,
                             response_text=response.text)
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to delete user: {response.text}"
                )
        
        logger.info("user_deleted_from_auth_service_successfully", target_username=username)
        
    except httpx.RequestError as e:
        logger.error("auth_service_delete_communication_error",
                     target_username=username,
                     auth_service_url=auth_service_url,
                     error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with auth_service: {str(e)}"
        )

    # 2) Drop their MongoDB collection (all chats)
    try:
        collections = mongo_db.list_collection_names()
        if username in collections:
            logger.info("dropping_user_chat_collection", target_username=username)
            mongo_db.drop_collection(username)
            logger.info("user_chat_collection_dropped_successfully", target_username=username)
        else:
            logger.info("user_chat_collection_not_found", target_username=username)
        
        logger.info("user_deleted_completely", target_username=username)
        
    except Exception as e:
        logger.error("mongodb_collection_drop_failed",
                     target_username=username,
                     error=str(e))
        # Don't raise exception here as user is already deleted from auth service
        # Just log the error

    return


# LIST CHATS
@router.get(
    "/users/{username}/chats",
    dependencies=[Depends(verify_developer_token)]
)
async def list_user_chats(username: str, mongo_db=Depends(get_mongo_db)):
    logger.info("admin_list_user_chats_request", target_username=username)
    
    try:
        collections = mongo_db.list_collection_names()
        if username not in collections:
            logger.warning("user_chat_collection_not_found", target_username=username)
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info("fetching_user_chats", target_username=username)
        coll = mongo_db[username]
        result = []
        
        for doc in coll.find().sort("timestamp", -1):
            result.append({
                "chat_id": str(doc["_id"]),
                "chat_name": doc["chat_name"],
                "last_timestamp": doc["timestamp"]
            })
        
        logger.info("user_chats_retrieved_successfully",
                    target_username=username,
                    chat_count=len(result))
        
        return {"chats": result}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("list_user_chats_failed",
                     target_username=username,
                     error=str(e))
        raise HTTPException(status_code=500, detail="Error fetching user chats")


# DELETE A SINGLE CHAT
@router.delete(
    "/users/{username}/chats/{chat_id}",
    dependencies=[Depends(verify_developer_token)],
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user_chat(username: str, chat_id: str, mongo_db=Depends(get_mongo_db)):
    logger.info("admin_delete_user_chat_request",
                target_username=username,
                chat_id=chat_id)
    
    try:
        collections = mongo_db.list_collection_names()
        if username not in collections:
            logger.warning("user_not_found_for_chat_deletion",
                           target_username=username,
                           chat_id=chat_id)
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info("deleting_user_chat",
                    target_username=username,
                    chat_id=chat_id)
        
        coll = mongo_db[username]
        result = coll.delete_one({"_id": ObjectId(chat_id)})
        
        if result.deleted_count == 0:
            logger.warning("chat_not_found_for_deletion",
                           target_username=username,
                           chat_id=chat_id)
            raise HTTPException(status_code=404, detail="Chat not found")
        
        logger.info("user_chat_deleted_successfully",
                    target_username=username,
                    chat_id=chat_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_user_chat_failed",
                     target_username=username,
                     chat_id=chat_id,
                     error=str(e))
        raise HTTPException(status_code=500, detail="Error deleting chat")

    return


# FETCH A SINGLE CHAT
@router.get(
    "/users/{username}/chats/{chat_id}",
    dependencies=[Depends(verify_developer_token)]
)
async def get_user_chat(username: str, chat_id: str, mongo_db=Depends(get_mongo_db)):
    logger.info("admin_get_user_chat_request",
                target_username=username,
                chat_id=chat_id)
    
    try:
        collections = mongo_db.list_collection_names()
        if username not in collections:
            logger.warning("user_not_found_for_chat_retrieval",
                           target_username=username,
                           chat_id=chat_id)
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info("fetching_user_chat",
                    target_username=username,
                    chat_id=chat_id)
        
        coll = mongo_db[username]
        doc = coll.find_one({"_id": ObjectId(chat_id)})
        
        if not doc:
            logger.warning("chat_not_found",
                           target_username=username,
                           chat_id=chat_id)
            raise HTTPException(status_code=404, detail="Chat not found")
        
        doc["_id"] = str(doc["_id"])
        message_count = len(doc.get("messages", []))
        
        logger.info("user_chat_retrieved_successfully",
                    target_username=username,
                    chat_id=chat_id,
                    chat_name=doc.get("chat_name"),
                    message_count=message_count)
        
        return doc
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_user_chat_failed",
                     target_username=username,
                     chat_id=chat_id,
                     error=str(e))
        raise HTTPException(status_code=500, detail="Error fetching chat")


# Health check endpoint
@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    logger.info("admin_health_check_requested")
    return {"status": "healthy", "service": "admin_service"}
