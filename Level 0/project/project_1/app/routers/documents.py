import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import verify_api_key
from app.schemas.document import DocumentCreate, DocumentResponse
from app.services import document_service

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)
logger = logging.getLogger(__name__)
ApiKeyDependency = Annotated[str, Depends(verify_api_key)]


@router.get("", response_model=list[DocumentResponse])
def list_documents(_: ApiKeyDependency) -> list[DocumentResponse]:
    logger.info("Listing documents")
    return document_service.list_documents()


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, _: ApiKeyDependency) -> DocumentResponse:
    logger.info("Fetching document_id=%s", document_id)
    try:
        return document_service.get_document(document_id)
    except ValueError as exc:
        logger.warning("Document lookup failed for document_id=%s", document_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_document(
    payload: DocumentCreate,
    _: ApiKeyDependency,
) -> DocumentResponse:
    logger.info("Creating document with title=%s", payload.title)
    return document_service.create_document(payload)
