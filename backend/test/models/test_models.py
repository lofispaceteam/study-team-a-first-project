import pytest
from sqlalchemy.orm import Session
from models import User
from database import get_db

@pytest.fixture
def db():
    # Получаем реальную сессию БД
    gen = get_db()
    session: Session = next(gen)
    yield session
    try:
        next(gen)
    except StopIteration:
        pass

def test_create_user(db):
    test_email = "unit_test_user@example.com"
    test_phone = "+70000000000"

    # Удалим, если уже есть (чтобы тест можно было запускать повторно)
    existing = db.query(User).filter(User.email == test_email).first()
    if existing:
        db.delete(existing)
        db.commit()

    user = User(
        first_name="Unit",
        last_name="Test",
        email=test_email,
        phone_number=test_phone,
        password_hash="hashed_password"
    )

    db.add(user)
    db.commit()

    saved_user = db.query(User).filter(User.email == test_email).first()
    assert saved_user is not None
    assert saved_user.first_name == "Unit"
    assert saved_user.last_name == "Test"
    assert saved_user.phone_number == test_phone
    assert saved_user.password_hash == "hashed_password"