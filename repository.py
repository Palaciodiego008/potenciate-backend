from sqlalchemy.orm import Session
from models import User, Project
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path
from datetime import datetime
from fastapi import UploadFile
import shutil



DATABASE_URL = "sqlite:///./potenciate.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # Crear la carpeta si no existe

def init_db():
    from models import Base
    Base.metadata.create_all(bind=engine)

def create_user(db: Session, user_data):
    db_user = User(
        name=user_data.name,
        email=user_data.email,
        password=user_data.password,
        terms=user_data.terms,
        phone=user_data.phone,
        address=user_data.address
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_all_users(db: Session):
    return db.query(User).all()

def create_project(db: Session, project_data, file: UploadFile):
    user_dir = Path("uploads") / str(project_data.user_id)
    user_dir.mkdir(parents=True, exist_ok=True)

    file_name = file.filename
    file_path = user_dir / file_name

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db_project = Project(
        title=project_data.title,
        description=project_data.description,
        objetive=project_data.objetive,
        area=project_data.area,
        user_id=project_data.user_id,
        file=str(file_path)
    )

    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return db_project