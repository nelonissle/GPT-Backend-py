import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient

load_dotenv()

# --- SQLite setup (shared file from auth_service) ---
SQLITE_PATH = os.getenv("SQLITE_PATH")
if not SQLITE_PATH:
    raise RuntimeError("SQLITE_PATH not set in .env")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{SQLITE_PATH}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_sql_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- MongoDB setup (same database as chat_service) ---
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI not set in .env")
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["chat_database"]

def get_mongo_db():
    return mongo_db
