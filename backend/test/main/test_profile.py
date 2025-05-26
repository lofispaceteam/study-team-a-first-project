import pytest
from fastapi.testclient import TestClient
from main import app
from jose import jwt
import os

client = TestClient(app)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def get_token():
    response = client.post("/login", json={
        "email": "test@example.com",
        "password": "testpassword"
    })
    return response.json()["access_token"]

def test_get_profile_success():
    token = get_token()
    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"

def test_update_profile_name():
    token = get_token()
    response = client.put("/me", json={
        "first_name": "ОбновлённоеИмя",
        "last_name": "ОбновлённаяФамилия",
        "phone_number": "+79999999999",
        "current_password": "testpassword",
        "new_password": "newsecurepassword",
        "confirm_new_password": "newsecurepassword"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["detail"] == "Профиль успешно обновлён"