from pydantic import BaseModel
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    terms = Column(Boolean)
    phone = Column(String)
    address = Column(String)

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    terms: bool
    phone: str
    address: str

    class Config:
        from_attributes = True 
class UserLogin(BaseModel):
    email: str
    password: str