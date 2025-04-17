from fastapi import FastAPI
from app.routes.admin_routes import router as admin_router

app = FastAPI(title="Chat Admin Service")
app.include_router(admin_router)
