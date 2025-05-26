import pytest
from fastapi.testclient import TestClient
from main import app
from models import User
from database import SessionLocal
from passlib.context import CryptContext

client = TestClient(app)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@pytest.fixture(scope="module", autouse=True)
def create_test_user():
    db = SessionLocal()
    db.query(User).filter(User.email == "test@example.com").delete()
    db.commit()

    user = User(
        first_name="Тест",
        last_name="Пользователь",
        email="test@example.com",
        phone_number = "+79999999999",
        password_hash=pwd_context.hash("testpassword"),
    )
    db.add(user)
    db.commit()
    yield
    db.query(User).filter(User.email == "test@example.com").delete()
    db.commit()
    db.close()

def test_login_success():
    response = client.post("/login", json={
        "email": "test@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 201
    assert "access_token" in response.json()

def test_login_wrong_password():
    response = client.post("/login", json={
        "email": "test@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401