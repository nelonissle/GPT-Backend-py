# app/database.py

import os
from pymongo import MongoClient

def get_db():
    """
    Lazily construct and return a MongoDB database instance.
    Raises ValueError if any required MONGO_* env-vars are missing.
    """
    host = os.getenv("MONGO_GPT_SERVICE_HOST")
    port = os.getenv("MONGO_GPT_SERVICE_PORT")
    user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    pwd  = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
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
        raise ValueError(
            "Die Umgebungsvariable(n) " + ", ".join(missing) + " ist/sind nicht gesetzt."
        )

    uri = f"mongodb://{user}:{pwd}@{host}:{port}/"
    client = MongoClient(uri)
    return client[db_name]
