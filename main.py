from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from models import User
from database import Base, engine, get_db
from passlib.context import CryptContext

Base.metadata.create_all(bind=engine)
app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    password: str
    confirm_password: str

    #Не доделано!
    @model_validator(mode='before')
    def check_password_length(cls, v):
        password = v.get('password')
        if len(password) < 8:
            raise ValueError('Длина пароля меньше 8 символов!')
        return v
    #Не доделано!
