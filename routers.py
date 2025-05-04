from fastapi import APIRouter, Depends, HTTPException, UploadFile, Form
from sqlalchemy.orm import Session
from auth import create_access_token, get_password_hash, authenticate_user
from repository import SessionLocal, create_user, get_user_by_email, create_project
from models import UserCreate, UserLogin, User, ProjectCreate, Project
import os
from shadai.core.session import Session as ShadaiSession  
from helpers import ingest_documents_with_alias, chat_with_history, ingest_documents_without_alias

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
async def create_new_project(
    title: str = Form(...),
    description: str = Form(...),
    objetive: str = Form(...),
    area: str = Form(...),
    user_id: str = Form(...),
    file: UploadFile = UploadFile(...),
    db: Session = Depends(get_db)
):
    print("title:", title)
    if not title or not description or not objetive or not area or not user_id:
        raise HTTPException(status_code=400, detail="All fields are required")
    if not file:
        raise HTTPException(status_code=400, detail="File is required")

    # Crear instancia de datos del proyecto
    project_data = ProjectCreate(
        title=title,
        description=description,
        objetive=objetive,
        area=area,
        user_id=user_id
    )

    print(f"Project data: {project_data}")

    # Guardar el proyecto en DB y subir el archivo en create_project
    db_project = create_project(db, project_data=project_data, file=file)
    print(f"DB Project: {db_project}")

    filename = db_project.file.split("/")[-1]
    file_url = f"/uploads/{user_id}/{filename}"

    return {
        "id": db_project.id,
        "title": db_project.title,
        "description": db_project.description,
        "file_url": file_url
    }


@router.get("/projects")
async def get_all_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    if not projects:
        raise HTTPException(status_code=404, detail="No projects found")
    return projects

@router.get("/projects/user/{user_id}")
async def get_user_projects(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    projects = db.query(Project).filter(Project.user_id == user_id).all()
    if not projects:
        raise HTTPException(status_code=404, detail="No projects found for this user")

    return projects

@router.get("/projects/check/{user_id}")
async def check_document_content(user_id: int):
    user_upload_dir = os.path.join("uploads", str(user_id))
    query_prompt_path = "query_prompt.txt"

    if not os.path.exists(user_upload_dir) or not os.listdir(user_upload_dir):
        raise HTTPException(status_code=404, detail="No documents found for this user.")

    if not os.path.exists(query_prompt_path):
        raise HTTPException(status_code=400, detail="query_prompt.txt not found in user directory.")

    try:
        # Leer el contenido del archivo .txt como prompt
        with open(query_prompt_path, "r", encoding="utf-8") as f:
            prompt_message = f.read()
            print(f"Prompt message: {prompt_message}")


        async with ShadaiSession(type="standard", delete=True) as session:
            await ingest_documents_without_alias(input_dir=user_upload_dir, session=session)

            # Usar el prompt leído del archivo para el análisis
            query_result = await chat_with_history(
                session=session,
                system_prompt=prompt_message,
                message="Eres un analista experto en proyectos tecnológicos y educativos. Evalúa con detalle técnico y pedagógico."
            )

        return {
            "user_id": user_id,
            "analysis_result": query_result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing document(s): {str(e)}")