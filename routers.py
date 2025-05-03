from fastapi import APIRouter, Depends, HTTPException, UploadFile, Form
from sqlalchemy.orm import Session
from auth import create_access_token, get_password_hash, authenticate_user
from repository import SessionLocal, create_user, get_user_by_email, create_project
from models import UserCreate, UserLogin, User, ProjectCreate


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


## auth .py
@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email) 
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password) 
    user.password = hashed_password
    
    new_user = create_user(db=db, user_data=user)
    return {"id": new_user.id, "name": new_user.name, "email": new_user.email}

@router.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    authenticated_user = authenticate_user(db_user, user.password)
    
    if not authenticated_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(user=authenticated_user, data={"sub": authenticated_user.email})
    return {"access_token": access_token}


@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    for user in users:
        del user.password
    return users


@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    del user.password
    return user


@router.post("/projects")
def create_new_project(
    title: str = Form(...),
    description: str = Form(...),
    objetive: str = Form(...),
    area: str = Form(...),
    user_id: int = Form(...),
    file: UploadFile = UploadFile(...),
    db: Session = Depends(get_db)
):
    if not title or not description or not objetive or not area or not user_id:
        raise HTTPException(status_code=400, detail="All fields are required")
    if not file:
        raise HTTPException(status_code=400, detail="File is required")
    if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOCX are allowed")

    project_data = ProjectCreate(
        title=title,
        description=description,
        objetive=objetive,
        area=area,
        user_id=user_id
    )

    print("project data =======>", project_data)

    db_project = create_project(db, project_data=project_data, file=file)

    filename = db_project.file.split("/")[-1]
    file_url = f"/uploads/{filename}"

    return {
        "id": db_project.id,
        "title": db_project.title,
        "description": db_project.description,
        "file_url": file_url
    }
