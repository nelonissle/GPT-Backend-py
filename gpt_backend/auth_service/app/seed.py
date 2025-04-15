from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models.user import User
from passlib.context import CryptContext

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create the database tables
Base.metadata.create_all(bind=engine)

# Seed data
def seed_data():
    db: Session = SessionLocal()
    try:
        # Check if users already exist
        if db.query(User).first():
            print("Users already seeded.")
            return

        # Create test users
        test_users = [
            {"username": "admin", "password": "AdminPassword123!", "role": "Admin"},
            {"username": "user1", "password": "UserPassword123!", "role": "Kunde"},
            {"username": "user2", "password": "UserPassword123!", "role": "Kunde"},
        ]

        for user in test_users:
            hashed_password = pwd_context.hash(user["password"])
            new_user = User(username=user["username"], password_hash=hashed_password, role=user["role"])
            db.add(new_user)

        db.commit()
        print("Test users seeded successfully.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()