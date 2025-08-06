import os
import uuid
from datetime import datetime, timedelta
import jwt
from dotenv import load_dotenv
from app.utils.logger import get_logger

# Load environment variables if not already loaded
load_dotenv()

# Initialize logger
logger = get_logger("jwt_helper")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def create_access_token(data: dict) -> str:
    """
    Generates a JWT token with a 3-day expiration and standard claims.
    The token's 'sub' claim (the username) is used as the 'iss' (issuer) value.
    This ensures consistency with the Kong JWT credential lookup.
    """
    username = data.get("sub", "unknown")
    role = data.get("role", "unknown")
    logger.info("creating_access_token", username=username, role=role)
    
    if not SECRET_KEY:
        logger.error("token_creation_failed", reason="missing_secret_key", username=username)
        raise ValueError("SECRET_KEY environment variable is not set")
    
    try:
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
        
        logger.info("access_token_created_successfully", 
                   username=username, 
                   role=role, 
                   issuer=issuer, 
                   jti=jti, 
                   expires_at=expire.isoformat())
        
        return encoded_jwt
    except Exception as e:
        logger.error("token_creation_failed", username=username, role=role, error=str(e))
        raise
