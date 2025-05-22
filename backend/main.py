from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer 
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from models import User, RefreshToken
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
from routers.upload_photo import router as upload_photo_router

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
app.include_router(upload_photo_router)
# Подключаем статику (для отображения фото и карты)
app.mount("/static", StaticFiles(directory="static"), name="static")

#
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # или ["http://localhost:3000"], а так это все.
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)
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

class TokenRequest(BaseModel):
    refresh_token: str    

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
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Невалидный токен")
    except JWTError:
        raise HTTPException(status_code=401, detail="Невалидный токен")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

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

    # Access Token (короткоживущий)
    access_token = create_access_token({"sub": db_user.email}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    # Refresh Token (уникальный и хранится в БД)
    refresh_token = str(uuid.uuid4())
    db_token = RefreshToken(token=refresh_token, user_id=db_user.id)
    db.add(db_token)
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }

# Загрузка аватарки пользователя
@app.post("/upload-photo", status_code = 201)
async def upload_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Файл должен быть изображением")

    upload_folder = "static/photos"
    os.makedirs(upload_folder, exist_ok=True)

    safe_email = user.email.replace("@", "_").replace(".", "_")
    filename = f"{safe_email}_{file.filename}"
    file_path = os.path.join(upload_folder, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Обновляем путь к фото у пользователя
    user.photo_path = f"/static/photos/{filename}"
    db.add(user)
    db.commit()

    return {
        "filename": filename,
        "message": "Фото успешно загружено",
        "photo_url": user.photo_path
    }

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
def logout(payload: TokenRequest, db: Session = Depends(get_db)):
    refresh_token = payload.refresh_token
    token_entry = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if not token_entry:
        raise HTTPException(status_code=401, detail="Недействительный refresh токен")

    db.delete(token_entry)
    db.commit()
    return {"message": "Вы успешно вышли из системы"}

app.include_router(router)

# Возвращает URL карты города
@app.get("/map")
def get_map_url(request: Request):
    full_url = str(request.base_url)[:-1] + "/static/map/restaurant_map.jpg"
    return {"map_url": full_url}

@app.post("/refresh")
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    db_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if not db_token:
        raise HTTPException(status_code=401, detail="Недействительный refresh токен")

    user = db.query(User).filter(User.id == db_token.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    new_access_token = create_access_token({"sub": user.email}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": new_access_token, "token_type": "bearer"}