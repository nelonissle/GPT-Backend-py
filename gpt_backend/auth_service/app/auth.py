from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import jwt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# SQLite setup
DATABASE_URL = "sqlite:///./auth_service.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT setup
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
ALGORITHM = "HS256"

# FastAPI app
app = FastAPI()

# Database Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="Kunde")

# Create the database tables
Base.metadata.create_all(bind=engine)

# Pydantic Models
class UserRegister(BaseModel):
    username: str
    password: str
    role: str = "Kunde"

class UserLogin(BaseModel):
    username: str
    password: str

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def is_valid_password(password: str) -> bool:
    import re
    if len(password) < 15:
        raise HTTPException(status_code=400, detail="Password must be at least 15 characters long.")
    if not re.search(r"[A-Za-z]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one letter.")
    if not re.search(r"\d", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one number.")
    if not re.search(r"[\W_]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one special character.")
    return True

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Routes
@app.post("/register")
async def register(user: UserRegister, db: SessionLocal = Depends(get_db)):
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
    
    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, password_hash=hashed_password, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate JWT token for the newly registered user
    access_token = create_access_token(data={"sub": new_user.username, "role": new_user.role})
    
    return {
        "message": "User registered successfully.",
        "user_id": new_user.id,
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.post("/login")
async def login(user: UserLogin, db: SessionLocal = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    
    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    
    # Generate JWT token
    access_token = create_access_token(data={"sub": db_user.username, "role": db_user.role})
    return {"message": "Login successful.", "access_token": access_token, "token_type": "bearer"}

@app.get("/users")
async def get_all_users(db: SessionLocal = Depends(get_db)):
    users = db.query(User).all()
    return [{"id": user.id, "username": user.username, "role": user.role} for user in users]