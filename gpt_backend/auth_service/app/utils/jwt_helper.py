import os
import uuid
from datetime import datetime, timedelta
import jwt
from dotenv import load_dotenv

# Environment laden (falls noch nicht global geladen)
load_dotenv()

# Konfiguration aus der .env
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ISSUER = "nelo"  # Issuer-Claim: in diesem Fall dein Name

def create_access_token(data: dict) -> str:
    """
    Erzeugt einen JWT mit einer Ablaufzeit von 3 Tagen und fügt Standard-Claims hinzu:
    - iss: Issuer (hier: "nelo")
    - iat: Zeitpunkt der Ausstellung
    - exp: Ablaufzeit (3 Tage ab Ausstellung)
    - jti: Eindeutige Token-ID
    - aud: Audience (optional; wird nur gesetzt, wenn in den Eingabedaten vorhanden)
    """
    payload = data.copy()
    now = datetime.utcnow()
    expire = now + timedelta(days=3)
    
    # Optional: Extrahiere einen Audience-Wert, falls in den Eingabedaten vorhanden
    audience = payload.get("aud", None)
    
    # Generiere eine eindeutige JWT ID (jti)
    jti = str(uuid.uuid4())
    
    # Füge die Standard-Claims hinzu
    payload.update({
        "iss": ISSUER,   # Aussteller des Tokens
        "iat": now,      # Zeitpunkt der Ausstellung
        "exp": expire,   # Ablaufzeit
        "jti": jti       # Eindeutige ID des Tokens
    })
    
    # Falls ein Audience-Wert existiert, wird dieser hinzugefügt
    if audience:
        payload["aud"] = audience
        
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt