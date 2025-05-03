from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth import create_access_token, get_password_hash, authenticate_user
from repository import SessionLocal, get_user_by_email, create_user
from models import UserCreate, UserLogin, User

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

