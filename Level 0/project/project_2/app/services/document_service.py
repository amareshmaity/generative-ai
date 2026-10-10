from __future__ import annotations

import csv
import io
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings
from app.schemas.document import (
    DocumentListItem,
    DocumentProcessResponse,
    DocumentResponse,
)

ALLOWED_EXTENSIONS = {".txt", ".csv", ".pdf"}
_DOCUMENTS: list[dict] = []
_next_id = 1


def _ensure_upload_dir() -> Path:
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    return settings.upload_dir


def _to_document_response(document: dict) -> DocumentResponse:
    return DocumentResponse(
        id=document["id"],
        filename=document["filename"],
        content_type=document["content_type"],
        size_bytes=document["size_bytes"],
        processing_status=document["processing_status"],
        saved_path=document["saved_path"],
        preview=document["preview"],
    )


def _to_list_item(document: dict) -> DocumentListItem:
    return DocumentListItem(
        id=document["id"],
        filename=document["filename"],
        content_type=document["content_type"],
        size_bytes=document["size_bytes"],
        processing_status=document["processing_status"],
    )


def _extract_preview(filename: str, content_type: str, raw_bytes: bytes) -> tuple[str, str]:
    suffix = Path(filename).suffix.lower()

    if suffix == ".txt":
        text = raw_bytes.decode("utf-8", errors="ignore")
        return text[:160], text

    if suffix == ".csv":
        text = raw_bytes.decode("utf-8", errors="ignore")
        reader = csv.reader(io.StringIO(text))
        rows = list(reader)
        preview_lines = [", ".join(row) for row in rows[:3]]
        preview = " | ".join(preview_lines)
        normalized_text = "\n".join([", ".join(row) for row in rows])
        return preview[:160], normalized_text

    if suffix == ".pdf":
        preview = (
            "PDF file received. Full text extraction is not implemented in this "
            "beginner project."
        )
        return preview, preview

    raise ValueError("Unsupported file type")


async def save_uploaded_document(file: UploadFile) -> DocumentResponse:
    global _next_id

    try:
        if not file.filename:
            raise ValueError("Filename is required")

        suffix = Path(file.filename).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise ValueError("Only .txt, .csv, and .pdf files are supported")

        raw_bytes = await file.read()
        if not raw_bytes:
            raise ValueError("Uploaded file is empty")

        if len(raw_bytes) > settings.max_file_size:
            raise ValueError("Uploaded file is too large")

        preview, normalized_text = _extract_preview(
            filename=file.filename,
            content_type=file.content_type or "application/octet-stream",
            raw_bytes=raw_bytes,
        )

        upload_dir = _ensure_upload_dir()
        stored_filename = f"{uuid4().hex}{suffix}"
        saved_path = upload_dir / stored_filename
        saved_path.write_bytes(raw_bytes)

        document = {
            "id": _next_id,
            "filename": file.filename,
            "content_type": file.content_type or "application/octet-stream",
            "size_bytes": len(raw_bytes),
            "processing_status": "uploaded",
            "saved_path": str(saved_path),
            "preview": preview,
            "normalized_text": normalized_text,
        }
        _DOCUMENTS.append(document)
        _next_id += 1

        return _to_document_response(document)
    finally:
        await file.close()


def list_documents() -> list[DocumentListItem]:
    return [_to_list_item(document) for document in _DOCUMENTS]


def get_document(document_id: int) -> DocumentResponse:
    for document in _DOCUMENTS:
        if document["id"] == document_id:
            return _to_document_response(document)
    raise ValueError("Document not found")


def process_document(document_id: int) -> DocumentProcessResponse:
    for document in _DOCUMENTS:
        if document["id"] == document_id:
            normalized_text = document["normalized_text"]
            document["processing_status"] = "processed"
            return DocumentProcessResponse(
                document_id=document["id"],
                filename=document["filename"],
                content_type=document["content_type"],
                processing_status=document["processing_status"],
                character_count=len(normalized_text),
                line_count=max(1, normalized_text.count("\n") + 1),
                estimated_word_count=len(normalized_text.split()),
                preview=document["preview"],
                notes=_build_processing_note(document["filename"]),
            )
    raise ValueError("Document not found")


def _build_processing_note(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return "PDF metadata was processed. Text extraction can be expanded later with a dedicated PDF parser."
    if suffix == ".csv":
        return "CSV rows were normalized into text-style content for lightweight document processing."
    return "Plain text content was processed successfully."


def reset_store() -> None:
    global _next_id

    for document in _DOCUMENTS:
        saved_path = Path(document["saved_path"])
        if saved_path.exists():
            try:
                saved_path.unlink()
            except PermissionError:
                # On Windows, uploaded test files can remain locked briefly.
                pass
    _DOCUMENTS.clear()
    _next_id = 1
