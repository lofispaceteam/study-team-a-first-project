from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, index = true)
    first_name = Column(String, nullable = False)
    last_name = Column(String, nullable = False)
    email = Column(String, unique = True, index = True, nullable = False)
    phone_number = Column(String, unique = True, nullable = False)
    password_hash = Column(String, nullable = False)