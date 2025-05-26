# 🧋 FastAPI Bubble Tea Backend

Бэкенд-приложение для Bubble Tea кафе, реализованное на **FastAPI** с использованием **PostgreSQL**, **SQLAlchemy** и **JWT-аутентификации**. Поддерживает регистрацию, авторизацию, аватарки пользователей, отображение карты ресторанов и текущие промо-акции.

---

## 🚀 Возможности

- ✅ Регистрация и авторизация пользователей
- 🔐 JWT-аутентификация
- 🖼️ Загрузка и отображение аватарки
- 👤 Получение и обновление профиля
- 🚪 Выход из аккаунта (удаление refresh токена)
- 🗺️ Получение карты города с расположением ресторанов
- 🎁 Отображение актуальных промо-акций (обновляются каждую минуту)
- 🌐 Поддержка CORS (для взаимодействия с фронтендом)

---

## 🗂️ Структура проекта

```
.
├── main.py                 # Основной файл FastAPI-приложения
├── database.py             # Подключение к базе PostgreSQL
├── models.py               # SQLAlchemy-модель пользователя
├── routes/
│   ├── promotions.py       # Роут с эндпоинтом /promotions
│   └── upload_photo.py
├── static/
│   ├── photos/             # Загруженные аватарки пользователей
│   └── map/                # Картинка карты города
├── tests/
│   ├── database/
│   │   └── test_database.py
│   ├── models/
│   │   └── test_models.py
│   ├── promotions/
│   │   └── test_promotions.py
│   └── main/
│       ├── test_login.py
│       ├── test_logout.py
│       ├── test_map.py
│       ├── test_profile.py
│       ├── test_register.py
│       └── test_upload_photo.py
├── .env                    # Переменные окружения
├── pytest.ini              # Конфигурация тестов
└── requirements.txt        # Зависимости проекта
```
---

## 📌 Эндпоинты приложения
```
Метод   Путь            Описание
POST	/register	    Регистрация нового пользователя
POST	/login	        Авторизация и получение access + refresh токенов
POST	/refresh	    Обновление access токена по refresh токену
POST	/logout	        Выход (удаление refresh токена)
GET	    /me	            Получение данных текущего пользователя
PUT	    /me	            Обновление профиля пользователя
POST	/upload-photo	Загрузка аватарки
GET	    /map	        Получение URL карты города
GET	    /promotions	    Получение текущих промо-акций
```
---

## 🧪 Тестирование
    📦 Все тесты лежат в директории tests/.
    🧬 Используется реальная база данных PostgreSQL, указанная в .env.

    Запуск всех тестов(находясь в папке backend):
        pytest

---

### ⚙️ Переменные окружения
    .env должен содержать следующие переменные:
    ```
    DATABASE_URL=postgresql://fastapi_user:mypassword123@localhost/fastapi_db
    SECRET_KEY=your_secret_key
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=15
    ```

---

## 🌐 CORS
Поддержка CORS настроена в main.py с использованием fastapi.middleware.cors.CORSMiddleware.

В текущей конфигурации разрешены запросы с любых источников:
- allow_origins = ["*"]
⚠️ Важно: в продакшене рекомендуется указать конкретные домены фронтенда вместо "*", например:
- allow_origins = [
    "https://your-frontend-domain.com"
]
---

## 🐳 Возможности расширения
- Добавление категорий и фильтрации акций
- Интерактивная карта с выбором ресторана
- Админ-панель для управления пользователями и акциями
- Уведомления о новых акцияхи
- Подтверждение почты

---

## 📦 Зависимости
См. **requirements.txt**. Основные библиотеки:
- fastapi
- sqlalchemy
- psycopg2-binary
- python-jose
- passlib[bcrypt]
- python-dotenv
- pytest