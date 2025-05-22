import pytest
from database import SessionLocal
from models import User
from passlib.context import CryptContext

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
        phone_number="+79999999999",  
        password_hash=pwd_context.hash("testpassword"),
    )
    db.add(user)
    db.commit()
    yield
    db.query(User).filter(User.email == "test@example.com").delete()
    db.commit()
    db.close()