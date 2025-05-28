import os
from dotenv import load_dotenv
from sqlalchemy.ext.declarative import declarative_base
from pymongo import MongoClient

# ✅ Füge das hinzu
Base = declarative_base()

# .env laden
# Load .env from project root
load_dotenv(dotenv_path="../.env")

# MongoDB-Setup
MONGO_SERVICE_HOST = os.getenv("MONGO_SERVICE_HOST")
MONGO_SERVICE_PORT = os.getenv("MONGO_SERVICE_PORT")
MONGO_INITDB_ROOT_USERNAME = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_INITDB_ROOT_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

if not all([MONGO_SERVICE_HOST, MONGO_SERVICE_PORT, MONGO_INITDB_ROOT_USERNAME, MONGO_INITDB_ROOT_PASSWORD]):
    raise ValueError("One or more required MongoDB env variables are missing.")

mongo_uri = f"mongodb://{MONGO_INITDB_ROOT_USERNAME}:{MONGO_INITDB_ROOT_PASSWORD}@{MONGO_SERVICE_HOST}:{MONGO_SERVICE_PORT}/"
mongo_client = MongoClient(mongo_uri)
mongo_db = mongo_client["chat_database"]

def get_mongo_db():
    return mongo_db
