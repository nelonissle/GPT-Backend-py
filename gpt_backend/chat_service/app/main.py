# main.py

from fastapi import FastAPI
from app.routes import chat_routes

app = FastAPI()

# Alle Chat-Endpunkte werden unter /chat eingebunden
app.include_router(chat_routes.router, prefix="/chat", tags=["Chat Service"])
