from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session
import jwt
from app.database import get_db
from app.models.user import User
from app.utils.jwt_helper import create_access_token
from app.utils.password_utils import hash_password, verify_password, is_valid_password
from app.utils.kong_consumer import create_kong_consumer, create_kong_jwt_credentials
from app.utils.logger import get_logger
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="../../.env")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

router = APIRouter()
security = HTTPBearer()

# Initialize logger
logger = get_logger("auth_routes")


def verify_developer_token(
    creds: HTTPAuthorizationCredentials = Depends(security)
):
    logger.info("verifying_developer_token")
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info("developer_token_verified", username=payload.get("sub"), role=payload.get("role"))
    except jwt.PyJWTError as e:
        logger.warning("developer_token_verification_failed", error=str(e))
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if payload.get("role") != "developer":
        logger.warning("developer_role_required", actual_role=payload.get("role"), username=payload.get("sub"))
        raise HTTPException(status_code=403, detail="Developer role required")
    return payload


class UserRegister(BaseModel):
    username: str
    password: str
    role: str = "Kunde"


class UserLogin(BaseModel):
    username: str
    password: str


@router.post("/register")
async def register(user: UserRegister, db: Session = Depends(get_db)):
    logger.info("user_registration_attempt", username=user.username, role=user.role)

    if not user.username or not user.password:
        logger.warning("registration_failed", reason="missing_credentials", username=user.username)
        raise HTTPException(status_code=400, detail="Username and password are required.")

    try:
        if not is_valid_password(user.password):
            logger.warning("registration_failed", reason="invalid_password", username=user.username)
            raise HTTPException(
                status_code=400,
                detail="Password must be at least 15 characters long and contain a letter, a number, and a special character."
            )
    except HTTPException as e:
        logger.warning("password_validation_failed", username=user.username, detail=e.detail)
        raise e

    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        logger.warning("registration_failed", reason="username_exists", username=user.username)
        raise HTTPException(status_code=400, detail="Username already exists.")

    try:
        password_hash = hash_password(user.password)
        new_user = User(username=user.username, password_hash=password_hash, role=user.role)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info("user_created_in_database", user_id=new_user.id, username=new_user.username, role=new_user.role)

        # Automatically create a Kong consumer and add JWT credentials for this user.
        try:
            create_kong_consumer(new_user.username)
            logger.info("kong_consumer_created", username=new_user.username)
        except Exception as e:
            logger.error("kong_consumer_creation_failed", username=new_user.username, error=str(e))
            print(f"Warning: Failed to create Kong consumer: {e}")

        try:
            create_kong_jwt_credentials(new_user.username)
            logger.info("kong_jwt_credentials_created", username=new_user.username)
        except Exception as e:
            logger.error("kong_jwt_credentials_creation_failed", username=new_user.username, error=str(e))
            print(f"Warning: Failed to create Kong JWT credentials: {e}")

        # Generate JWT token with 'sub' set to the new user's username.
        access_token = create_access_token(data={
            "sub": new_user.username,
            "role": new_user.role
        })

        logger.info("user_registration_successful", user_id=new_user.id, username=new_user.username, role=new_user.role)

        return {
            "message": "User registered successfully.",
            "user_id": new_user.id,
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        logger.error("user_registration_error", username=user.username, error=str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error during registration")


@router.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    logger.info("login_attempt", username=user.username)

    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        logger.warning("login_failed", username=user.username, reason="invalid_credentials")
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    try:
        access_token = create_access_token(data={"sub": db_user.username, "role": db_user.role})
        logger.info("login_successful", username=db_user.username, role=db_user.role, user_id=db_user.id)
        return {"message": "Login successful.", "access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error("token_creation_failed", username=db_user.username, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create access token")


@router.get("/users", dependencies=[Depends(verify_developer_token)])
async def get_all_users(db: Session = Depends(get_db)):
    """
    Fetch all users from the database.
    """
    logger.info("fetching_all_users")
    try:
        users = db.query(User).all()
        user_count = len(users)
        logger.info("users_fetched_successfully", count=user_count)
        return [{"id": user.id, "username": user.username, "role": user.role} for user in users]
    except Exception as e:
        logger.error("users_fetch_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch users")


@router.delete("/users/{username}", status_code=204, dependencies=[Depends(verify_developer_token)])
async def delete_user(username: str, db: Session = Depends(get_db)):
    """
    Deletes a user by their username.
    """
    logger.info("delete_user_attempt", username=username)

    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        logger.warning("delete_user_failed", username=username, reason="user_not_found")
        raise HTTPException(status_code=404, detail="User not found")

    try:
        user_id = db_user.id
        user_role = db_user.role
        db.delete(db_user)
        db.commit()
        logger.info("user_deleted_successfully", username=username, user_id=user_id, role=user_role)
        return
    except Exception as e:
        logger.error("user_deletion_failed", username=username, error=str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete user")
