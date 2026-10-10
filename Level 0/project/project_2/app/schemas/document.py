from pydantic import BaseModel


class DocumentListItem(BaseModel):
    id: int
    filename: str
    content_type: str
    size_bytes: int
    processing_status: str


class DocumentResponse(DocumentListItem):
    saved_path: str
    preview: str


class UploadResponse(BaseModel):
    status: str
    message: str
    document: DocumentResponse


class DocumentProcessResponse(BaseModel):
    document_id: int
    filename: str
    content_type: str
    processing_status: str
    character_count: int
    line_count: int
    estimated_word_count: int
    preview: str
    notes: str
