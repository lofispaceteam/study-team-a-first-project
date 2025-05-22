from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Request, APIRouter
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer 
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from models import User
from database import Base, engine, get_db
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
from jose import jwt, JWTError
from datetime import datetime, timedelta
import shutil
import uuid
from typing import Optional
from fastapi.staticfiles import StaticFiles
import re
from routers import promotions

# Загружаем переменные окружения из .env файла
load_dotenv()

# Настройки JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Папка для хранения фото
PHOTO_DIR = "static/photos"
os.makedirs(PHOTO_DIR, exist_ok=True)

# Настройки хеширования пароля
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Создаем таблицы в БД
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Подключаем статику (для отображения фото и карты)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Подключаем роутер акций
app.include_router(promotions.router)

# Модели Pydantic для валидации входящих данных
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    password: str
    confirm_password: str

class UserUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    
    current_password: Optional[str]
    new_password: Optional[str]
    confirm_new_password: Optional[str]

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Хеширует пароль
def hash_password(password: str) -> str:
    return pwd_context.hash(password)    

# Проверяет соответствие пароля и хеша
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Создает JWT-токен с заданными данными и временем жизни
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Получает текущего пользователя из токена
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Невалидный токен",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# Проверяет валидность номера телефона
def validate_phone(phone: str) -> bool:
    # Пример: телефон должен содержать только цифры, плюс и дефис, от 7 до 15 символов
    pattern = re.compile(r"^\+?[\d\-]{7,15}$")
    return bool(pattern.match(phone))

# Регистрация нового пользователя
@app.post('/register', status_code = 201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if user.password != user.confirm_password:
        raise HTTPException(status_code = 422, detail = "Пароли не совпадают!")
    if len(user.password) < 8:
        raise HTTPException(status_code = 422, detail = "Пароль меньше 8 символов!")
    
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code = 409, detail = "Пользователь с такой почтой уже существует!")
    
    new_user = User(
        first_name = user.first_name,
        last_name = user.last_name,
        email = user.email,
        phone_number=user.phone_number,
        password_hash = pwd_context.hash(user.password)
    )

    db.add(new_user)
    db.commit()

# Авторизация пользователя
@app.post("/login", status_code = 201)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Неверная почта или пароль")
    
    token = jwt.encode({"sub": user.email}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

# Загрузка аватарки пользователя
@app.post("/upload-photo", status_code = 201)
def upload_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Проверяем расширение файла
    allowed_extensions = {".jpg", ".jpeg", ".png"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=415, detail="Недопустимый формат файла. Разрешены: jpg, jpeg, png")

    # Проверяем размер файла (например, максимум 2 МБ)
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    max_size = 2 * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(status_code=413, detail="Файл слишком большой. Максимум 2 МБ.")

    # Удаление старого фото, если есть
    if current_user.photo_path:
        old_path = current_user.photo_path.lstrip("/")
        if os.path.exists(old_path):
            os.remove(old_path)

    filename = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join("static", "photos", filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    current_user.photo_path = f"/{file_path}"  # относительный URL с "/"
    db.commit()

    return {"detail": "Фото успешно загружено"}

# Получение данных профиля текущего пользователя
@app.get("/me")
def get_profile(request: Request, current_user: User = Depends(get_current_user)):
    # Формируем полный URL для фотографии, если она есть
    photo_url = None
    if current_user.photo_path:
        photo_url = str(request.base_url)[:-1] + current_user.photo_path  # убираем последний слеш у base_url и добавляем путь

    return {
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "phone_number": current_user.phone_number,
        "photo_url": photo_url
    }

# Обновление профиля пользователя
@app.put("/me", status_code=200)
def update_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Обновление ФИО и телефона
    if user_update.first_name is not None:
        current_user.first_name = user_update.first_name
    if user_update.last_name is not None:
        current_user.last_name = user_update.last_name

    if user_update.phone_number is not None:
        if not validate_phone(user_update.phone_number):
            raise HTTPException(status_code=422, detail="Некорректный номер телефона")
        current_user.phone_number = user_update.phone_number

    # Обновление пароля
    if user_update.new_password or user_update.confirm_new_password:
        if not user_update.current_password:
            raise HTTPException(status_code=400, detail="Требуется текущий пароль")
        if not verify_password(user_update.current_password, current_user.password_hash):
            raise HTTPException(status_code=401, detail="Неверный текущий пароль")
        if user_update.new_password != user_update.confirm_new_password:
            raise HTTPException(status_code=400, detail="Новые пароли не совпадают")
        if len(user_update.new_password) < 8:
            raise HTTPException(status_code=400, detail="Новый пароль должен быть не менее 8 символов")

        current_user.password_hash = hash_password(user_update.new_password)

    db.commit()

    return {"detail": "Профиль успешно обновлён"}

@router.post("/logout", status_code = 200)
def logout(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Не прошел проверку подлинности")
    return JSONResponse(content={"message": "Успешно вышли из системы"})

app.include_router(router)

# Возвращает URL карты города
@app.get("/map")
def get_map_url():
    
    return {"map_url": "/static/map/city_map.jpg"}