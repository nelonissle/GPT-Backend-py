# app/database.py

import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Lade .env Variablen
load_dotenv()

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
# Erstelle eine MongoDB-URI
client = MongoClient(myMongoUri)

# Verwende eine Datenbank namens "chat_database"
db = client["chat_database"]

def get_db():
    """
    Liefert das Datenbankobjekt für den Chat-Service.
    """
    return db
