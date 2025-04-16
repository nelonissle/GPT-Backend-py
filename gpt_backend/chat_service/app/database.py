import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Lade .env Variablen
load_dotenv()

# Hole die MongoDB URI aus den Umgebungsvariablen
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("Die Umgebungsvariable MONGO_URI ist nicht gesetzt.")
client = MongoClient(MONGO_URI)

# Verwende eine Datenbank namens "chat_database"
db = client["chat_database"]

def get_db():
    """
    Liefert das Datenbankobjekt für den Chat-Service.
    """
    return db
