"""
main.py - Entry point for the Chat Service FastAPI application.

This module initializes the FastAPI app, loads environment variables,
and includes the chat-related API routes.

Author: Nelo Nisslé
Date: 2024-06-09
"""

from dotenv import load_dotenv
# Load .env from project root
load_dotenv()

from fastapi import FastAPI
from app.routes import chat_routes


# Initialize FastAPI application
app = FastAPI()

# Alle Chat-Endpunkte werden unter /chat eingebunden
app.include_router(chat_routes.router, prefix="/chat", tags=["Chat Service"])
