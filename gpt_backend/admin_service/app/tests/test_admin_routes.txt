import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from app.main import app
from app.routes import admin_routes

client = TestClient(app)

# Dependency override for authentication
def override_verify_developer_token():
    return {"role": "developer"}

app.dependency_overrides[admin_routes.verify_developer_token] = override_verify_developer_token

MOCK_TOKEN = "mocked.jwt.token"
MOCK_HEADERS = {"Authorization": f"Bearer {MOCK_TOKEN}"}

@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "testsecret")
    monkeypatch.setenv("ALGORITHM", "HS256")
    monkeypatch.setenv("AUTH_SERVICE_URL", "http://fake-auth-service")

def test_list_users():
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json = AsyncMock(return_value=[{"username": "alice"}])
        response = client.get("/admin/users", headers=MOCK_HEADERS)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

def test_delete_user():
    with patch("httpx.AsyncClient.delete", new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value.status_code = 204
        response = client.delete("/admin/users/alice", headers=MOCK_HEADERS)
        assert response.status_code == 204

def test_list_user_chats():
    mock_db = MagicMock()
    mock_db.list_collection_names.return_value = ["alice"]
    mock_coll = MagicMock()
    mock_coll.find.return_value.sort.return_value = [
        {"_id": "1", "chat_name": "test", "timestamp": 123}
    ]
    mock_db.__getitem__.return_value = mock_coll

    with patch("app.routes.admin_routes.get_mongo_db", return_value=mock_db):
        response = client.get("/admin/users/alice/chats", headers=MOCK_HEADERS)
        assert response.status_code == 200
        assert "chats" in response.json()

def test_list_user_chats_user_not_found():
    mock_db = MagicMock()
    mock_db.list_collection_names.return_value = []
    with patch("app.routes.admin_routes.get_mongo_db", return_value=mock_db):
        response = client.get("/admin/users/bob/chats", headers=MOCK_HEADERS)
        assert response.status_code == 404

def test_delete_user_chat():
    mock_db = MagicMock()
    mock_db.list_collection_names.return_value = ["alice"]
    mock_coll = MagicMock()
    mock_coll.delete_one.return_value.deleted_count = 1
    mock_db.__getitem__.return_value = mock_coll

    with patch("app.routes.admin_routes.get_mongo_db", return_value=mock_db):
        response = client.delete("/admin/users/alice/chats/1", headers=MOCK_HEADERS)
        assert response.status_code == 204

def test_delete_user_chat_not_found():
    mock_db = MagicMock()
    mock_db.list_collection_names.return_value = ["alice"]
    mock_coll = MagicMock()
    mock_coll.delete_one.return_value.deleted_count = 0
    mock_db.__getitem__.return_value = mock_coll

    with patch("app.routes.admin_routes.get_mongo_db", return_value=mock_db):
        response = client.delete("/admin/users/alice/chats/999", headers=MOCK_HEADERS)
        assert response.status_code == 404

def test_get_user_chat():
    mock_db = MagicMock()
    mock_db.list_collection_names.return_value = ["alice"]
    mock_coll = MagicMock()
    mock_coll.find_one.return_value = {"_id": "1", "chat_name": "test", "timestamp": 123}
    mock_db.__getitem__.return_value = mock_coll

    with patch("app.routes.admin_routes.get_mongo_db", return_value=mock_db):
        response = client.get("/admin/users/alice/chats/1", headers=MOCK_HEADERS)
        assert response.status_code == 200
        assert response.json()["chat_name"] == "test"

def test_get_user_chat_not_found():
    mock_db = MagicMock()
    mock_db.list_collection_names.return_value = ["alice"]
    mock_coll = MagicMock()
    mock_coll.find_one.return_value = None
    mock_db.__getitem__.return_value = mock_coll

    with patch("app.routes.admin_routes.get_mongo_db", return_value=mock_db):
        response = client.get("/admin/users/alice/chats/999", headers=MOCK_HEADERS)
        assert response.status_code == 404