from io import BytesIO

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import document_service

client = TestClient(app)
AUTH_HEADERS = {"x-api-key": "level1-upload-key"}


@pytest.fixture(autouse=True)
def reset_document_store() -> None:
    document_service.reset_store()
    yield
    document_service.reset_store()


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_upload_requires_api_key() -> None:
    response = client.post(
        "/documents/upload",
        files={"file": ("notes.txt", BytesIO(b"hello world"), "text/plain")},
    )
    assert response.status_code == 401


def test_upload_text_file() -> None:
    response = client.post(
        "/documents/upload",
        headers=AUTH_HEADERS,
        files={
            "file": (
                "notes.txt",
                BytesIO(b"FastAPI helps build APIs quickly for AI backends."),
                "text/plain",
            )
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "success"
    assert body["document"]["filename"] == "notes.txt"
    assert body["document"]["processing_status"] == "uploaded"


def test_list_documents_after_upload() -> None:
    client.post(
        "/documents/upload",
        headers=AUTH_HEADERS,
        files={
            "file": (
                "dataset.csv",
                BytesIO(b"name,score\nAlice,95\nBob,88"),
                "text/csv",
            )
        },
    )

    response = client.get("/documents", headers=AUTH_HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["filename"] == "dataset.csv"


def test_get_document_by_id() -> None:
    upload_response = client.post(
        "/documents/upload",
        headers=AUTH_HEADERS,
        files={
            "file": (
                "notes.txt",
                BytesIO(b"Document content for retrieval testing."),
                "text/plain",
            )
        },
    )
    document_id = upload_response.json()["document"]["id"]

    response = client.get(f"/documents/{document_id}", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert response.json()["id"] == document_id


def test_process_document() -> None:
    upload_response = client.post(
        "/documents/upload",
        headers=AUTH_HEADERS,
        files={
            "file": (
                "notes.txt",
                BytesIO(b"Line one.\nLine two.\nLine three."),
                "text/plain",
            )
        },
    )
    document_id = upload_response.json()["document"]["id"]

    response = client.post(f"/documents/{document_id}/process", headers=AUTH_HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert body["processing_status"] == "processed"
    assert body["line_count"] == 3


def test_reject_unsupported_file_type() -> None:
    response = client.post(
        "/documents/upload",
        headers=AUTH_HEADERS,
        files={
            "file": (
                "image.png",
                BytesIO(b"not-a-real-image"),
                "image/png",
            )
        },
    )
    assert response.status_code == 400
    assert "supported" in response.json()["detail"]
