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

@app.post('/register')
def register(user: UserCreate, db: Session = Depends(get_db)):
    if user.password != user.confirm_password:
        raise HTTPException(status_code = 400, detail = "Пароли не совпадают!") #Для Frontend! detail - вывести если не совпадают пароли.