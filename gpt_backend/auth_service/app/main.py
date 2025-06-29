from dotenv import load_dotenv
# Load .env from project root, regardless of working directory
load_dotenv()

from fastapi import FastAPI
from app.routes import auth_routes
from app.database import engine, Base, SessionLocal
from app.models.user import User
from passlib.context import CryptContext

# Initialize FastAPI application
app = FastAPI()
app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.on_event("startup")
def startup():
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Optional: seed test users
    db = SessionLocal()
    try:
        if not db.query(User).first():
            test_users = [
                {"username": "admin", "password": "AdminPassword123!", "role": "Admin"},
                {"username": "user1", "password": "UserPassword123!", "role": "Kunde"},
                {"username": "user2", "password": "UserPassword123!", "role": "Kunde"},
            ]
            for user in test_users:
                hashed_password = pwd_context.hash(user["password"])
                db.add(User(username=user["username"], password_hash=hashed_password, role=user["role"]))
            db.commit()
            print("✅ Test users seeded.")
        else:
            print("ℹ️ Users already seeded.")
    finally:
        db.close()