from fastapi import FastAPI
from dotenv import load_dotenv
from app.auth import app as auth_app  # Import the auth app

load_dotenv()

app = FastAPI()

# Include the auth routes under /auth
app.mount("/auth", auth_app)

@app.get("/")
def read_root():
    return {"message": "AuthService is running"}
