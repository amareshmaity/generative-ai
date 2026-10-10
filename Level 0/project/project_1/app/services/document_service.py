from app.schemas.document import DocumentCreate, DocumentResponse

_DOCUMENTS: list[dict] = [
    {
        "id": 1,
        "title": "FastAPI Basics",
        "content": (
            "FastAPI is a modern Python framework used to build APIs quickly "
            "with validation, automatic docs, and clean request handling."
        ),
        "tags": ["fastapi", "backend"],
    },
    {
        "id": 2,
        "title": "RAG Notes",
        "content": (
            "RAG stands for retrieval augmented generation. It combines search "
            "or retrieval with language model generation to ground answers."
        ),
        "tags": ["genai", "rag"],
    },
]
_next_id = 3


def _to_response(document: dict) -> DocumentResponse:
    return DocumentResponse(
        id=document["id"],
        title=document["title"],
        content=document["content"],
        tags=document["tags"],
        word_count=len(document["content"].split()),
    )


def list_documents() -> list[DocumentResponse]:
    return [_to_response(document) for document in _DOCUMENTS]


def get_document(document_id: int) -> DocumentResponse:
    for document in _DOCUMENTS:
        if document["id"] == document_id:
            return _to_response(document)
    raise ValueError("Document not found")


def create_document(payload: DocumentCreate) -> DocumentResponse:
    global _next_id

    document = {
        "id": _next_id,
        "title": payload.title,
        "content": payload.content,
        "tags": payload.tags,
    }
    _DOCUMENTS.append(document)
    _next_id += 1
    return _to_response(document)
