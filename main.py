from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, model_validator, ValidationError

app = FastAPI()

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
