import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.security import verify_api_key
from app.schemas.document import (
    DocumentListItem,
    DocumentProcessResponse,
    DocumentResponse,
    UploadResponse,
)
from app.services import document_service

router = APIRouter(prefix="/documents", tags=["documents"])
logger = logging.getLogger(__name__)
ApiKeyDependency = Annotated[str, Depends(verify_api_key)]


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    _: ApiKeyDependency,
    file: UploadFile = File(...),
) -> UploadResponse:
    logger.info("Upload request received for filename=%s", file.filename)
    try:
        document = await document_service.save_uploaded_document(file)
    except ValueError as exc:
        logger.warning("Upload rejected for filename=%s", file.filename)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return UploadResponse(
        status="success",
        message="File uploaded successfully",
        document=document,
    )


@router.get("", response_model=list[DocumentListItem])
def list_documents(_: ApiKeyDependency) -> list[DocumentListItem]:
    logger.info("Listing uploaded documents")
    return document_service.list_documents()


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, _: ApiKeyDependency) -> DocumentResponse:
    logger.info("Fetching uploaded document_id=%s", document_id)
    try:
        return document_service.get_document(document_id)
    except ValueError as exc:
        logger.warning("Document not found for document_id=%s", document_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post("/{document_id}/process", response_model=DocumentProcessResponse)
def process_document(
    document_id: int,
    _: ApiKeyDependency,
) -> DocumentProcessResponse:
    logger.info("Processing document_id=%s", document_id)
    try:
        return document_service.process_document(document_id)
    except ValueError as exc:
        logger.warning("Processing failed for document_id=%s", document_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
