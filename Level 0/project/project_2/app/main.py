from fastapi import FastAPI

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.routers import documents, health

setup_logging()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="A small FastAPI file upload API for document processing practice.",
)

app.include_router(health.router)
app.include_router(documents.router)
