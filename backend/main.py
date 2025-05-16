from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
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

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

PHOTO_DIR = "static/photos"
os.makedirs(PHOTO_DIR, exist_ok=True)  # Создаст папку, если её нет

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

UPLOAD_DIR = "static/photos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

Base.metadata.create_all(bind=engine)
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

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

def hash_password(password: str) -> str:
    return pwd_context.hash(password)    

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

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

@app.post('/register', status_code = 201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if user.password != user.confirm_password:
        raise HTTPException(status_code = 422, detail = "Пароли не совпадают!") #Для Frontend! detail - вывести если не совпадают пароли.
    if len(user.password) < 8:
        raise HTTPException(status_code = 422, detail = "Пароль меньше 8 символов!") #Для Frontend! detail - вывести если короткий пароль.
    
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code = 409, detail = "Пользователь с такой почтой уже существует!") #Для Frontend! detail - вывести если пользователь с такой почтой существует.
    
    new_user = User(
        first_name = user.first_name,
        last_name = user.last_name,
        email = user.email,
        password = user.password,
        password_hash = pwd_context.hash(user.password)
    )

    db.add(new_user)
    db.commit()

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Неверная почта или пароль")
    
    token = jwt.encode({"sub": user.email}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/upload-photo", status_code = 201)
def upload_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Удаление старого фото, если оно есть
    if current_user.photo_path:
        old_path = current_user.photo_path
        file_to_delete = old_path.lstrip("/")
        if os.path.exists(file_to_delete):
            os.remove(file_to_delete)

    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join("static", "photos", filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Обновляем путь в БД
    current_user.photo_path = f"/{file_path}"  # путь начинается с "/"
    db.commit()

    return {"detail": "Фото успешно загружено"}

@app.get("/me")
def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "phone_number": current_user.phone_number,
        "photo_path": current_user.photo_path
    }

@app.put("/me", status_code=200)
def update_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Обновление основного профиля
    if user_update.first_name is not None:
        current_user.first_name = user_update.first_name
    if user_update.last_name is not None:
        current_user.last_name = user_update.last_name
    if user_update.phone_number is not None:
        current_user.phone_number = user_update.phone_number

    # Смена пароля
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