from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3)
    document_id: int = Field(..., ge=1)


class ChatResponse(BaseModel):
    status: str
    document_id: int
    model: str
    answer: str
    source_excerpt: str
