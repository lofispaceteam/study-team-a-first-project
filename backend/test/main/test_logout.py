import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def get_token():
    response = client.post("/login", json={
        "email": "test@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 201, response.text
    return response.json()["access_token"]

@pytest.mark.usefixtures("create_test_user")
def test_logout_success():
    token = get_token()
    response = client.post("/logout", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Успешно вышли из системы"