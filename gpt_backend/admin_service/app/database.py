import os
from sqlalchemy.ext.declarative import declarative_base
from pymongo import MongoClient
from app.utils.logger import get_logger

# Initialize logger
logger = get_logger("database")

# ✅ Füge das hinzu
Base = declarative_base()

# MongoDB-Setup
MONGO_GPT_SERVICE_HOST = os.getenv("MONGO_GPT_SERVICE_HOST")
MONGO_GPT_SERVICE_PORT = os.getenv("MONGO_GPT_SERVICE_PORT")
MONGO_INITDB_ROOT_USERNAME = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_INITDB_ROOT_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

if not all([MONGO_GPT_SERVICE_HOST, MONGO_GPT_SERVICE_PORT,
            MONGO_INITDB_ROOT_USERNAME, MONGO_INITDB_ROOT_PASSWORD]):
    logger.error("mongodb_configuration_missing",
                 missing_vars=[
                     var for var, val in [
                         ("MONGO_GPT_SERVICE_HOST", MONGO_GPT_SERVICE_HOST),
                         ("MONGO_GPT_SERVICE_PORT", MONGO_GPT_SERVICE_PORT),
                         ("MONGO_INITDB_ROOT_USERNAME", MONGO_INITDB_ROOT_USERNAME),
                         ("MONGO_INITDB_ROOT_PASSWORD", MONGO_INITDB_ROOT_PASSWORD)
                     ] if not val
                 ])
    raise ValueError("One or more required MongoDB env variables are missing.")

try:
    mongo_uri = f"mongodb://{MONGO_INITDB_ROOT_USERNAME}:{MONGO_INITDB_ROOT_PASSWORD}@{MONGO_GPT_SERVICE_HOST}:{MONGO_GPT_SERVICE_PORT}/"
    logger.info("connecting_to_mongodb",
                host=MONGO_GPT_SERVICE_HOST,
                port=MONGO_GPT_SERVICE_PORT,
                database="chat_database")
    
    mongo_client = MongoClient(mongo_uri)
    mongo_db = mongo_client["chat_database"]
    
    # Test the connection
    mongo_client.admin.command('ismaster')
    logger.info("mongodb_connection_successful",
                host=MONGO_GPT_SERVICE_HOST,
                port=MONGO_GPT_SERVICE_PORT,
                database="chat_database")
    
except Exception as e:
    logger.error("mongodb_connection_failed",
                 host=MONGO_GPT_SERVICE_HOST,
                 port=MONGO_GPT_SERVICE_PORT,
                 database="chat_database",
                 error=str(e))
    raise


def get_mongo_db():
    logger.debug("mongodb_database_requested")
    return mongo_db
