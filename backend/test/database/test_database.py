from sqlalchemy.exc import OperationalError
from database import engine, get_db

def test_database_connection():
    try:
        # Пробуем установить соединение
        with engine.connect() as connection:
            assert connection.closed == False
    except OperationalError:
        assert False, "Не удалось подключиться к базе данных"

def test_get_db_yields_session():
    gen = get_db()
    session = next(gen)  # получаем сессию
    assert session is not None
    assert session.bind == engine  # проверяем, что привязана к правильному движку
    try:
        session.execute("SELECT 1")  # простой запрос
    finally:
        try:
            next(gen)
        except StopIteration:
            pass  # генератор должен завершиться без ошибок