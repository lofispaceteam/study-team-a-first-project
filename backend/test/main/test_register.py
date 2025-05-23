import pytest
from fastapi.testclient import TestClient
from main import app, get_db
from database import SessionLocal
from models import User

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    db = SessionLocal()
    # Удаляем пользователя, если уже существует (на всякий случай)
    db.query(User).filter(User.email == "test@example.com").delete()
    db.commit()
    yield
    # После теста очищаем
    db.query(User).filter(User.email == "test@example.com").delete()
    db.commit()
    db.close()

def test_register_success():
    response = client.post("/register", json={
        "first_name": "Тест",
        "last_name": "Пользователь",
        "email": "test@example.com",
        "phone_number": "+79999999999",
        "password": "testpassword",
        "confirm_password": "testpassword"
    })
    assert response.status_code == 201