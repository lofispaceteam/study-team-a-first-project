from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Строка подключения к базе данных PostgreSQL
# Формат: postgresql://<пользователь>:<пароль>@<хост>/<имя_бд>
DATABASE_URL = "postgresql://fastapi_user:mypassword123@localhost/fastapi_db"

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