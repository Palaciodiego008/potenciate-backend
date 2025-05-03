from pydantic import BaseModel
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Modelo de base de datos
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    terms = Column(Boolean)
    phone = Column(String)
    address = Column(String)

# Pydantic model para registro
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    terms: bool
    phone: str
    address: str

    class Config:
        orm_mode = True

# Pydantic model para login
class UserLogin(BaseModel):
    email: str
    password: str
