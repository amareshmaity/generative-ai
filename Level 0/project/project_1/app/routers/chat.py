import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import verify_api_key
from app.schemas.chat import ChatRequest, ChatResponse
from app.services import chat_service, document_service

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)
logger = logging.getLogger(__name__)
ApiKeyDependency = Annotated[str, Depends(verify_api_key)]


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest, _: ApiKeyDependency) -> ChatResponse:
    logger.info("Chat request received for document_id=%s", payload.document_id)
    try:
        document = document_service.get_document(payload.document_id)
    except ValueError as exc:
        logger.warning("Chat failed because document was missing: %s", payload.document_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return chat_service.generate_answer(payload, document)
