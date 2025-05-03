print("user router")

from pydantic import BaseModel, EmailStr

# Usuario para registrar
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# Usuario para login
class UserLogin(BaseModel):
    username: str
    password: str

# Usuario en base de datos
class User(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str
