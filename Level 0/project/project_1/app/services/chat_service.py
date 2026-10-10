from app.core.config import settings
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.document import DocumentResponse


def generate_answer(
    payload: ChatRequest,
    document: DocumentResponse,
) -> ChatResponse:
    question = payload.question.lower()
    excerpt = document.content[:120]

    if "summary" in question or "summarize" in question:
        answer = (
            f"Summary for '{document.title}': "
            f"{document.content[:100].rstrip()}..."
        )
    elif "tag" in question:
        answer = f"Document tags are: {', '.join(document.tags) or 'no tags'}."
    else:
        answer = (
            f"Based on '{document.title}', the document says: "
            f"{document.content[:100].rstrip()}..."
        )

    return ChatResponse(
        status="success",
        document_id=document.id,
        model=settings.default_model,
        answer=answer,
        source_excerpt=excerpt,
    )
