print("models")
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String)
    address = Column(String)
    registration_date = Column(DateTime, default=datetime.utcnow)
    password = Column(String, nullable=False)  # Hashed password