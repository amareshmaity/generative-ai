from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
AUTH_HEADERS = {"x-api-key": "level1-secret-key"}


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_documents_requires_api_key() -> None:
    response = client.get("/documents")
    assert response.status_code == 401


def test_list_documents() -> None:
    response = client.get("/documents", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert len(response.json()) >= 2


def test_create_document() -> None:
    response = client.post(
        "/documents",
        headers=AUTH_HEADERS,
        json={
            "title": "Prompt Engineering Notes",
            "content": "Prompt engineering helps guide model behavior with clearer instructions.",
            "tags": ["prompting", "llm"],
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Prompt Engineering Notes"
    assert body["word_count"] > 0


def test_get_missing_document() -> None:
    response = client.get("/documents/999", headers=AUTH_HEADERS)
    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"


def test_chat_endpoint() -> None:
    response = client.post(
        "/chat",
        headers=AUTH_HEADERS,
        json={"question": "Summarize this document", "document_id": 1},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["document_id"] == 1
    assert "answer" in body
