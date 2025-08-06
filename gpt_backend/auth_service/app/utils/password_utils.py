import re
from fastapi import HTTPException
from passlib.context import CryptContext
from app.utils.logger import get_logger

# Initialize logger
logger = get_logger("password_utils")

# Erstelle ein CryptContext-Objekt als Modulvariable, sodass es nur einmal initialisiert wird
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Erzeugt einen Hash für das gegebene Passwort."""
    logger.info("hashing_password")
    try:
        hashed = pwd_context.hash(password)
        logger.info("password_hashed_successfully")
        return hashed
    except Exception as e:
        logger.error("password_hashing_failed", error=str(e))
        raise

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifiziert, ob das plain_password dem hashed_password entspricht."""
    logger.info("verifying_password")
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        logger.info("password_verification_completed", verified=result)
        return result
    except Exception as e:
        logger.error("password_verification_failed", error=str(e))
        return False

def is_valid_password(password: str) -> bool:
    """
    Überprüft, ob das Passwort den Anforderungen entspricht.
    - Mindestens 15 Zeichen
    - Mindestens ein Buchstabe
    - Mindestens eine Zahl
    - Mindestens ein Sonderzeichen
    """
    logger.info("validating_password", length=len(password))
    
    if len(password) < 15:
        logger.warning("password_validation_failed", reason="too_short", length=len(password))
        raise HTTPException(status_code=400, detail="Password must be at least 15 characters long.")
    if not re.search(r"[A-Za-z]", password):
        logger.warning("password_validation_failed", reason="no_letter")
        raise HTTPException(status_code=400, detail="Password must contain at least one letter.")
    if not re.search(r"\d", password):
        logger.warning("password_validation_failed", reason="no_number")
        raise HTTPException(status_code=400, detail="Password must contain at least one number.")
    if not re.search(r"[\W_]", password):
        logger.warning("password_validation_failed", reason="no_special_character")
        raise HTTPException(status_code=400, detail="Password must contain at least one special character.")
    
    logger.info("password_validation_successful")
    return True
