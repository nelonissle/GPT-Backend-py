import os
import requests
from fastapi import HTTPException

def create_kong_consumer(username: str):
    """
    Creates a Kong consumer with the given username.
    """
    kong_admin_url = os.getenv("KONG_ADMIN_URL", "http://kong-gateway:8001/consumers")
    if not kong_admin_url:
        raise HTTPException(status_code=500, detail="KONG_ADMIN_URL environment variable is not set.")
    
    payload = {"username": username}
    response = requests.post(kong_admin_url, json=payload)
    if response.status_code not in (201, 409):  # 201 = Created, 409 = Already exists
        raise HTTPException(status_code=500, detail=f"Failed to create Kong consumer: {response.text}")
    return response.json()

def create_kong_jwt_credentials(username: str):
    """
    Creates JWT credentials for a Kong consumer.
    The key for the credential is set to the consumer's username.
    """
    kong_admin_url = os.getenv("KONG_ADMIN_URL", "http://kong-gateway:8001/consumers")
    if not kong_admin_url:
        raise HTTPException(status_code=500, detail="KONG_ADMIN_URL environment variable is not set.")
    
    # Use the username as the key so that it will match the token's "sub" claim.
    key = username
    jwt_secret = os.getenv("SECRET_KEY", "default-secret-key")
    payload = {"key": key, "secret": jwt_secret}
    url = f"{kong_admin_url}/{username}/jwt"
    
    print(f"Creating JWT credentials at URL: {url} with payload: {payload}")
    response = requests.post(url, json=payload)
    print(f"Response status code: {response.status_code}, response text: {response.text}")
    
    if response.status_code not in (201, 409):
        raise HTTPException(status_code=500, detail=f"Failed to create Kong JWT credentials: {response.text}")
    return response.json()
