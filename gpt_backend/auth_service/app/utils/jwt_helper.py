import os
import uuid
from datetime import datetime, timedelta
import jwt
from dotenv import load_dotenv

# Load environment variables if not already loaded
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def create_access_token(data: dict) -> str:
    """
    Generates a JWT token with a 3-day expiration and standard claims.
    The token's 'sub' claim (the username) is used as the 'iss' (issuer) value.
    This ensures consistency with the Kong JWT credential lookup.
    """
    payload = data.copy()
    now = datetime.utcnow()
    expire = now + timedelta(days=3)
    jti = str(uuid.uuid4())
    
    # Use the 'sub' claim as issuer if present, otherwise default to "nelo"
    issuer = data.get("sub", "nelo")
    
    payload.update({
        "iss": issuer,
        "iat": now,
        "exp": expire,
        "jti": jti
    })
    
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
