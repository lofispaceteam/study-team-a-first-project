from fastapi import FastAPI, Depends, HTTPException 
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from models import User
from database import Base, engine, get_db
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
from jose import jwt

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

Base.metadata.create_all(bind=engine)
app = FastAPI()

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    password: str
    confirm_password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

@app.post('/register')
def register(user: UserCreate, db: Session = Depends(get_db)):
    if user.password != user.confirm_password:
        raise HTTPException(status_code = 400, detail = "Пароли не совпадают!") #Для Frontend! detail - вывести если не совпадают пароли.
    if len(user.password) < 8:
        raise HTTPException(status_code = 400, detail = "Пароль меньше 8 символов!") #Для Frontend! detail - вывести если короткий пароль.
    
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code = 400, detail = "Пользователь с такой почтой уже существует!") #Для Frontend! detail - вывести если пользователь с такой почтой существует.
    
    new_user = User(
        first_name = user.first_name,
        last_name = user.last_name,
        email = user.email,
        password = user.password,
        password_hash = pwd_context.hash(user.password)
    )

    db.add(new_user)
    db.commit()

    return 

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Неверная почта или пароль")
    
    token = jwt.encode({"sub": user.email}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}