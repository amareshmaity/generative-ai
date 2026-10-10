from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    content: str = Field(..., min_length=10)
    tags: list[str] = Field(default_factory=list)


class DocumentResponse(BaseModel):
    id: int
    title: str
    content: str
    tags: list[str]
    word_count: int
