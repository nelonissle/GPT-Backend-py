import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create a single connection and bind the session to it
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
connection = engine.connect()
Base.metadata.create_all(bind=connection)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)

@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "testsecret")
    monkeypatch.setenv("ALGORITHM", "HS256")

@pytest.fixture
def client():
    # Dependency override
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

def test_register_user(client):
    response = client.post("/auth/register", json={
        "username": "testuser",
        "password": "VeryStrongPassword!1",
        "role": "Kunde"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"]
    assert "access_token" in data

def test_register_duplicate_user(client):
    client.post("/auth/register", json={
        "username": "dupuser",
        "password": "VeryStrongPassword!1",
        "role": "Kunde"
    })
    response = client.post("/auth/register", json={
        "username": "dupuser",
        "password": "VeryStrongPassword!1",
        "role": "Kunde"
    })
    assert response.status_code == 400
    assert "Username already exists" in response.json()["detail"]

def test_register_invalid_password(client):
    response = client.post("/auth/register", json={
        "username": "weakuser",
        "password": "short",
        "role": "Kunde"
    })
    assert response.status_code == 400

def test_login_success(client):
    client.post("/auth/register", json={
        "username": "loginuser",
        "password": "VeryStrongPassword!1",
        "role": "Kunde"
    })
    response = client.post("/auth/login", json={
        "username": "loginuser",
        "password": "VeryStrongPassword!1"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_fail(client):
    response = client.post("/auth/login", json={
        "username": "nouser",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_get_all_users(client):
    client.post("/auth/register", json={
        "username": "adminuser",
        "password": "VeryStrongPassword!1",
        "role": "developer"
    })
    from app.utils.jwt_helper import create_access_token
    token = create_access_token({"sub": "adminuser", "role": "developer"})
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/users", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_delete_user(client):
    client.post("/auth/register", json={
        "username": "todelete",
        "password": "VeryStrongPassword!1",
        "role": "developer"
    })
    from app.utils.jwt_helper import create_access_token
    token = create_access_token({"sub": "todelete", "role": "developer"})
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete("/auth/users/todelete", headers=headers)
    assert response.status_code == 204