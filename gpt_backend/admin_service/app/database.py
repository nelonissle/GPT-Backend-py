import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient

load_dotenv(dotenv_path="../.env")

# --- MongoDB setup (same database as chat_service) ---
# Hole die MongoDB URI aus den Umgebungsvariablen
MONGO_SERVICE_HOST = os.getenv("MONGO_SERVICE_HOST")
if not MONGO_SERVICE_HOST:
    raise ValueError("Die Umgebungsvariable MONGO_SERVICE_HOST ist nicht gesetzt.")
# create a mongo uri string with environment varialbes
MONGO_SERVICE_PORT = os.getenv("MONGO_SERVICE_PORT")
if not MONGO_SERVICE_PORT:
    raise ValueError("Die Umgebungsvariable MONGO_SERVICE_PORT ist nicht gesetzt.")
MONGO_INITDB_ROOT_USERNAME = os.getenv("MONGO_INITDB_ROOT_USERNAME")
if not MONGO_INITDB_ROOT_USERNAME:
    raise ValueError("Die Umgebungsvariable MONGO_INITDB_ROOT_USERNAME ist nicht gesetzt.")
MONGO_INITDB_ROOT_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
if not MONGO_INITDB_ROOT_PASSWORD:
    raise ValueError("Die Umgebungsvariable MONGO_INITDB_ROOT_PASSWORD ist nicht gesetzt.")
myMongoUri = f"mongodb://{MONGO_INITDB_ROOT_USERNAME}:{MONGO_INITDB_ROOT_PASSWORD}@{MONGO_SERVICE_HOST}:{MONGO_SERVICE_PORT}/"
mongo_client = MongoClient(myMongoUri)
mongo_db = mongo_client["chat_database"]

def get_mongo_db():
    return mongo_db
