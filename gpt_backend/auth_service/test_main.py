from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    print("test")
    assert response.status_code == 200
    assert response.json() == {"message": "AuthService is running"}
