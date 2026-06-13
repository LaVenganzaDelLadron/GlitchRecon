from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from api.dependencies import get_db
from schemas.auth import CreateUser, LoginUser
from services.auth_service import create_access_token, login as login_service
from services.auth_service import register as register_service

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)



@router.post("/register")
def register_user(user: CreateUser, db: Session = Depends(get_db)):
    result = register_service(db, user.username, user.password)

    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account already exists")

    token = create_access_token(result.id, result.username)

    return {
        "message": "Account created successfully",
        "username": user.username,
        "token": token,
    }

@router.post("/login")
async def login(user: LoginUser, db: Session = Depends(get_db)):
    result = login_service(db, user.username, user.password)

    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")

    token = create_access_token(result.id, result.username)

    return {
        "message": "Logged in successfully",
        "username": user.username,
        "token": token,
    }