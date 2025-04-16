from fastapi import FastAPI
from app.routes import auth_routes

app = FastAPI()

# Route-Prefix setzen (zum Beispiel /auth)
app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
