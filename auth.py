from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from models import User
from repository import get_user_by_email
import hashlib
from sqlalchemy.orm import Session

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__default_rounds=12)

def generate_secret_key(user: User):
    user_data = f"{user.id}{user.email}"
    return hashlib.sha256(user_data.encode()).hexdigest()

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user: User, data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta  # Fecha de expiración con zona horaria UTC
    to_encode.update({"exp": expire})
    secret_key = generate_secret_key(user)  # Clave secreta específica del usuario
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db_user, password: str):
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid password")
    return db_user

def get_user_by_email_from_db(db, email: str):
    db_user = get_user_by_email(db, email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User with this email does not exist")
    return db_user

def verify_token(token: str, db: Session):
    try:
        # Decodificar el token JWT usando la clave secreta del usuario
        payload = jwt.decode(token, options={"verify_exp": False}, algorithms=[ALGORITHM])
        user_id = payload.get("sub")  # 'sub' almacena el email o identificador único

        if user_id is None:
            raise HTTPException(status_code=403, detail="Token is invalid")

        user = db.query(User).filter(User.email == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Token is invalid")
    