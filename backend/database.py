from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv(dotenv_path = ".env")

# Строка подключения к базе данных PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

# Создаём движок SQLAlchemy для подключения к базе данных
engine = create_engine(DATABASE_URL)

# Создаём сессию для взаимодействия с базой данных
# autocommit=False — транзакции нужно фиксировать вручную
# autoflush=False — изменения не отправляются в БД автоматически до коммита
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для объявления моделей
Base = declarative_base()

# Зависимость FastAPI для получения сессии БД внутри эндпоинтов
def get_db():
    db = SessionLocal()
    try:
        yield db # Возвращаем сессию вызывающему коду
    finally:
        db.close() # Закрываем сессию после завершения работы