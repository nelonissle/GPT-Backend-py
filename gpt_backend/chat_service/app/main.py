"""
main.py - Entry point for the Chat Service FastAPI application.

This module initializes the FastAPI app, loads environment variables,
and includes the chat-related API routes.

Author: Nelo Nisslé
Date: 2024-06-09
"""

import os
import time
from contextlib import asynccontextmanager
from dotenv import load_dotenv
# Load .env from project root, regardless of working directory
load_dotenv()

from fastapi import FastAPI, Request
from app.routes import chat_routes
from app.utils.logger import setup_logging

# Setup logging
logger = setup_logging("chat_service", os.getenv("LOG_LEVEL", "INFO"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("chat_service_starting", port=8001)
    
    # Any startup operations for chat service can go here
    logger.info("chat_service_started", port=8001)
    
    yield
    
    # Shutdown
    logger.info("chat_service_shutting_down")


# Initialize FastAPI application with lifespan
app = FastAPI(title="Chat Service", lifespan=lifespan)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log incoming request
    logger.info(
        "incoming_request",
        method=request.method,
        url=str(request.url),
        path=request.url.path,
        client_ip=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "unknown")
    )
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    # Log response
    logger.info(
        "request_completed",
        method=request.method,
        url=str(request.url),
        path=request.url.path,
        status_code=response.status_code,
        process_time=round(process_time, 4)
    )
    
    return response


# Alle Chat-Endpunkte werden unter /chat eingebunden
app.include_router(chat_routes.router, prefix="/chat", tags=["Chat Service"])
