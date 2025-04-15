from fastapi.testclient import TestClient
from app.auth import app

client = TestClient(app)

def test_register():
    response = client.post("/register", json={
        "username": "testuser",
        "password": "StrongPassword123!",
        "role": "Kunde"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "User registered successfully."

def test_login():
    response = client.post("/login", json={
        "username": "testuser",
        "password": "StrongPassword123!"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()