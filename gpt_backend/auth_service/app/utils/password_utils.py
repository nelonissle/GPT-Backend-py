import re
from fastapi import HTTPException
from passlib.context import CryptContext

# Erstelle ein CryptContext-Objekt als Modulvariable, sodass es nur einmal initialisiert wird
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Erzeugt einen Hash für das gegebene Passwort."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifiziert, ob das plain_password dem hashed_password entspricht."""
    return pwd_context.verify(plain_password, hashed_password)

def is_valid_password(password: str) -> bool:
    """
    Überprüft, ob das Passwort den Anforderungen entspricht.
    - Mindestens 15 Zeichen
    - Mindestens ein Buchstabe
    - Mindestens eine Zahl
    - Mindestens ein Sonderzeichen
    """
    if len(password) < 15:
        raise HTTPException(status_code=400, detail="Password must be at least 15 characters long.")
    if not re.search(r"[A-Za-z]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one letter.")
    if not re.search(r"\d", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one number.")
    if not re.search(r"[\W_]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one special character.")
    return True
