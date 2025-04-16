from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.utils.jwt_helper import create_access_token
from app.utils.password_utils import hash_password, verify_password, is_valid_password
from app.utils.kong_consumer import create_kong_consumer, create_kong_jwt_credentials

router = APIRouter()

class UserRegister(BaseModel):
    username: str
    password: str
    role: str = "Kunde"

class UserLogin(BaseModel):
    username: str
    password: str

@router.post("/register")
async def register(user: UserRegister, db: Session = Depends(get_db)):
    if not user.username or not user.password:
        raise HTTPException(status_code=400, detail="Username and password are required.")
    
    if not is_valid_password(user.password):
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 15 characters long and contain a letter, a number, and a special character."
        )
    
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists.")
    
    password_hash = hash_password(user.password)
    new_user = User(username=user.username, password_hash=password_hash, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Automatically create a Kong consumer and add JWT credentials for this user.
    try:
        create_kong_consumer(new_user.username)
    except Exception as e:
        print(f"Warning: Failed to create Kong consumer: {e}")
    
    try:
        create_kong_jwt_credentials(new_user.username)
    except Exception as e:
        print(f"Warning: Failed to create Kong JWT credentials: {e}")
    
    # Generate JWT token with 'sub' set to the new user's username.
    access_token = create_access_token(data={
        "sub": new_user.username,
        "role": new_user.role
    })

    return {
        "message": "User registered successfully.",
        "user_id": new_user.id,
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    
    access_token = create_access_token(data={"sub": db_user.username, "role": db_user.role})
    return {"message": "Login successful.", "access_token": access_token, "token_type": "bearer"}

@router.get("/users")
async def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{"id": user.id, "username": user.username, "role": user.role} for user in users]
