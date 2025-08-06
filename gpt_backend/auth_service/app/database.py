from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from app.utils.logger import get_logger

# Initialize logger
logger = get_logger("database")

# Hole die MongoDB URI aus den Umgebungsvariablen
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.error("database_configuration_failed", reason="missing_database_url")
    raise ValueError("Die Umgebungsvariable DATABASE_URL ist nicht gesetzt.")

logger.info("database_configuration", database_url=DATABASE_URL)

try:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    logger.info("database_engine_created_successfully")
except Exception as e:
    logger.error("database_engine_creation_failed", error=str(e))
    raise

# Dependency to get the database session
def get_db():
    logger.info("creating_database_session")
    db = SessionLocal()
    try:
        yield db
        logger.info("database_session_completed")
    except Exception as e:
        logger.error("database_session_error", error=str(e))
        raise
    finally:
        db.close()
        logger.info("database_session_closed")