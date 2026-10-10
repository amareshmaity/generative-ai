from fastapi import FastAPI

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.routers import chat, documents, health

setup_logging()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="A small FastAPI service for Level 1 backend practice.",
)

app.include_router(health.router)
app.include_router(documents.router)
app.include_router(chat.router)
