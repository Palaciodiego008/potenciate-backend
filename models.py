from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

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
    # Relación uno-a-muchos
    projects = relationship("Project", back_populates="user")

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

class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    objetive = Column(Text)
    area = Column(String)
    file = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="projects")


class ProjectCreate(BaseModel):
    title: str
    description: str
    objetive: str
    area: str
    user_id: int

    class Config:
        from_attributes = True
