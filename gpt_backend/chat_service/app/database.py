# app/database.py

import os
from pymongo import MongoClient
from app.utils.logger import get_logger

# Initialize logger
logger = get_logger("database")


def get_db():
    """
    Lazily construct and return a MongoDB database instance.
    Raises ValueError if any required MONGO_* env-vars are missing.
    """
    logger.info("connecting_to_mongodb")
    
    host = os.getenv("MONGO_GPT_SERVICE_HOST")
    port = os.getenv("MONGO_GPT_SERVICE_PORT")
    user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    pwd = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
    db_name = "chat_database"

    missing = [
        name for name, val in [
            ("MONGO_GPT_SERVICE_HOST", host),
            ("MONGO_GPT_SERVICE_PORT", port),
            ("MONGO_INITDB_ROOT_USERNAME", user),
            ("MONGO_INITDB_ROOT_PASSWORD", pwd),
        ] if not val
    ]
    
    if missing:
        logger.error("mongodb_connection_failed", 
                    reason="missing_environment_variables", 
                    missing_vars=missing)
        raise ValueError(
            "Die Umgebungsvariable(n) " + ", ".join(missing) + " ist/sind nicht gesetzt."
        )

    try:
        uri = f"mongodb://{user}:{pwd}@{host}:{port}/"
        logger.info("mongodb_connection_attempt", host=host, port=port, database=db_name)
        
        client = MongoClient(uri)
        db = client[db_name]
        
        # Test the connection
        client.admin.command('ismaster')
        logger.info("mongodb_connection_successful", host=host, port=port, database=db_name)
        
        return db
        
    except Exception as e:
        logger.error("mongodb_connection_error", 
                    host=host, 
                    port=port, 
                    database=db_name, 
                    error=str(e))
        raise
