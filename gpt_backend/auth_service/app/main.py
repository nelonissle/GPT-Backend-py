import os
import time
from contextlib import asynccontextmanager
from dotenv import load_dotenv
# Load .env from project root, regardless of working directory
load_dotenv()

from fastapi import FastAPI, Request
from app.routes import auth_routes
from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.utils.logger import setup_logging
from passlib.context import CryptContext

# Setup logging
logger = setup_logging("auth_service", os.getenv("LOG_LEVEL", "INFO"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("auth_service_starting", port=8002)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    logger.info("database_tables_created")

    # Optional: seed test users
    db = SessionLocal()
    try:
        if not db.query(User).first():
            logger.info("seeding_test_users")
            test_users = [
                {"username": "admin", "password": "AdminPassword123!", "role": "Admin"},
                {"username": "developer", "password": "DeveloperPassword123!", "role": "developer"},
                {"username": "user1", "password": "UserPassword123!", "role": "Kunde"},
                {"username": "user2", "password": "UserPassword123!", "role": "Kunde"},
            ]
            for user in test_users:
                hashed_password = pwd_context.hash(user["password"])
                db.add(User(username=user["username"], password_hash=hashed_password, role=user["role"]))
            db.commit()
            logger.info("test_users_seeded", count=len(test_users))
        else:
            logger.info("test_users_already_exist")
    except Exception as e:
        logger.error("test_user_seeding_failed", error=str(e))
        db.rollback()
    finally:
        db.close()
    
    logger.info("auth_service_started", port=8002)
    
    yield
    
    # Shutdown
    logger.info("auth_service_shutting_down")

# Initialize FastAPI application with lifespan
app = FastAPI(title="Auth Service", lifespan=lifespan)

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

app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])