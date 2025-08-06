import os
import requests
from fastapi import HTTPException
from app.utils.logger import get_logger

# Initialize logger
logger = get_logger("kong_consumer")

admin_url = os.getenv("KONG_ADMIN_URL", "/consumers")
auth_service = os.getenv("AUTH_SERVICE_URL", "/auth")
kong_host = os.getenv("KONG_GATEWAY_SERVICE_SERVICE_HOST", "localhost")
kong_port = os.getenv("KONG_ADMIN_PORT", "8001")
# kong_admin_url = os.getenv("KONG_ADMIN_URL", "http://kong-gateway:8001/consumers")
kong_admin_url = f"http://{kong_host}:{kong_port}{auth_service}"


def create_kong_consumer(username: str):
    """
    Creates a Kong consumer with the given username.
    """
    logger.info("creating_kong_consumer", username=username, url=kong_admin_url)

    if not kong_admin_url:
        logger.error("kong_consumer_creation_failed",
                     reason="missing_admin_url",
                     username=username)
        raise HTTPException(status_code=500, detail="KONG_ADMIN_URL environment variable is not set.")

    payload = {"username": username}

    try:
        response = requests.post(kong_admin_url, json=payload)
        logger.info("kong_consumer_api_response",
                    username=username,
                    status_code=response.status_code,
                    response_text=response.text[:200])  # Limit response text length

        if response.status_code not in (201, 409):  # 201 = Created, 409 = Already exists
            logger.error("kong_consumer_creation_failed",
                         username=username,
                         status_code=response.status_code,
                         response_text=response.text)
            raise HTTPException(status_code=500, detail=f"Failed to create Kong consumer: {response.text}")

        if response.status_code == 201:
            logger.info("kong_consumer_created_successfully", username=username)
        else:
            logger.info("kong_consumer_already_exists", username=username)

        return response.json()
    except requests.RequestException as e:
        logger.error("kong_consumer_request_failed", username=username, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to communicate with Kong: {str(e)}")


def create_kong_jwt_credentials(username: str):
    """
    Creates JWT credentials for a Kong consumer.
    The key for the credential is set to the consumer's username.
    """
    logger.info("creating_kong_jwt_credentials", username=username)

    kong_admin_url = os.getenv("KONG_ADMIN_URL", "http://kong-gateway:8001/consumers")
    if not kong_admin_url:
        logger.error("kong_jwt_creation_failed",
                     reason="missing_admin_url",
                     username=username)
        raise HTTPException(status_code=500, detail="KONG_ADMIN_URL environment variable is not set.")

    # Use the username as the key so that it will match the token's "sub" claim.
    key = username
    jwt_secret = os.getenv("SECRET_KEY", "default-secret-key")
    payload = {"key": key, "secret": jwt_secret}
    url = f"{kong_admin_url}/{username}/jwt"

    logger.info("kong_jwt_request_details", username=username, url=url, key=key)
    print(f"Creating JWT credentials at URL: {url} with payload: {payload}")

    try:
        response = requests.post(url, json=payload)
        logger.info("kong_jwt_api_response",
                    username=username,
                    status_code=response.status_code,
                    response_text=response.text[:200])  # Limit response text length
        print(f"Response status code: {response.status_code}, response text: {response.text}")

        if response.status_code not in (201, 409):
            logger.error("kong_jwt_creation_failed",
                         username=username,
                         status_code=response.status_code,
                         response_text=response.text)
            raise HTTPException(status_code=500, detail=f"Failed to create Kong JWT credentials: {response.text}")

        if response.status_code == 201:
            logger.info("kong_jwt_credentials_created_successfully", username=username)
        else:
            logger.info("kong_jwt_credentials_already_exist", username=username)

        return response.json()
    except requests.RequestException as e:
        logger.error("kong_jwt_request_failed", username=username, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to communicate with Kong: {str(e)}")
