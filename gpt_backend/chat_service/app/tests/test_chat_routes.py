import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app

client = TestClient(app)

# Mock JWT payload
def fake_verify_token(token):
    return {"sub": "testuser"}

# Dependency override for JWT
from app.routes import chat_routes
chat_routes.verify_token = fake_verify_token

@pytest.fixture
def mock_db():
    # Mock MongoDB collection and database
    mock_collection = MagicMock()
    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    return mock_db, mock_collection

@pytest.fixture
def auth_header():
    return {"Authorization": "Bearer faketoken"}

def test_new_chat(auth_header, mock_db):
    with patch("app.routes.chat_routes.get_db", return_value=mock_db[0]):
        with patch("app.routes.chat_routes.get_llm_response", return_value="LLM response"):
            response = client.post("/chat/new", json={"initial_query": "Hello world test"}, headers=auth_header)
            assert response.status_code == 200
            assert "chat_id" in response.json()

def test_add_message(auth_header, mock_db):
    fake_chat_id = "507f1f77bcf86cd799439011"
    mock_db[1].find_one.return_value = {"_id": fake_chat_id}
    mock_db[1].update_one.return_value.modified_count = 1
    with patch("app.routes.chat_routes.get_db", return_value=mock_db[0]):
        response = client.post("/chat/add", json={
            "chat_id": fake_chat_id,
            "role": "user",
            "text": "Hello again"
        }, headers=auth_header)
        assert response.status_code == 200
        assert response.json()["chat_id"] == fake_chat_id

def test_chat_history(auth_header, mock_db):
    mock_db[1].find.return_value.sort.return_value = [
        {
            "_id": "507f1f77bcf86cd799439011",
            "chat_name": "Test Chat",
            "messages": [{"text": "Hi", "timestamp": "now"}]
        }
    ]
    with patch("app.routes.chat_routes.get_db", return_value=mock_db[0]):
        response = client.get("/chat/history", headers=auth_header)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

def test_get_chat(auth_header, mock_db):
    fake_chat_id = "507f1f77bcf86cd799439011"
    mock_db[1].find_one.return_value = {
        "_id": fake_chat_id,
        "chat_name": "Test Chat",
        "messages": []
    }
    with patch("app.routes.chat_routes.get_db", return_value=mock_db[0]):
        response = client.get(f"/chat/{fake_chat_id}", headers=auth_header)
        assert response.status_code == 200
        assert response.json()["chat_name"] == "Test Chat"