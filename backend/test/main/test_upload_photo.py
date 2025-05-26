import os
import io
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def get_token():
    response = client.post("/login", json={
        "email": "test@example.com",
        "password": "testpassword"
    })
    return response.json()["access_token"]

def test_upload_photo_success():
    token = get_token()

    # Создаём фейковое изображение (в памяти)
    image_content = io.BytesIO()
    image_content.write(b"\x89PNG\r\n\x1a\n")  # минимальный заголовок PNG
    image_content.seek(0)

    files = {
        "file": ("test.png", image_content, "image/png")
    }

    response = client.post("/upload-photo", headers={
        "Authorization": f"Bearer {token}"
    }, files=files)

    assert response.status_code == 201
    assert response.json()["detail"] == "Фото успешно загружено"