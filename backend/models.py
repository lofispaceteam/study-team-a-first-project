from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# Модель пользователя для таблицы users в базе данных
class User(Base):
    __tablename__ = "users" # Название таблицы в базе данных

    # Уникальный идентификатор пользователя (первичный ключ)
    id = Column(Integer, primary_key = True, index = True)
    
    first_name = Column(String, nullable = False)
    last_name = Column(String, nullable = False)
    email = Column(String, unique = True, index = True, nullable = False)
    phone_number = Column(String, unique = True, nullable = False)
    password_hash = Column(String, nullable = False)
    photo_path = Column(String, nullable = True)
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="refresh_tokens")