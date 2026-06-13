import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from models.users import Users

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"


def create_access_token(user_id: int, username: str, expires_minutes: int = 60):
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=expires_minutes),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None


def register(db: Session, username: str, password: str):
    existing = db.query(Users).filter(Users.username == username).first()

    if existing:
        return None

    user = Users(username=username, password=password)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

def login(db: Session, username:str, password:str):
    users = db.query(Users).filter(Users.username == username, Users.password == password).first()

    return users