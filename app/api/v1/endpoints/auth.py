from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.user import UserCreate, UserLogin
from app.schemas.request import RefreshRequest, LogoutRequest
from app.services.auth_service import (
    register_user,
    login_user,
    refresh_access_token,
    logout_user,
)

router = APIRouter()


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, user.name, user.email, user.password)


@router.post("/login")
def login(request: Request, user: UserLogin, db: Session = Depends(get_db)):
    return login_user(db, user.email, user.password, request.client.host)


@router.post("/refresh")
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    return refresh_access_token(db, data.refresh_token)


@router.post("/logout")
def logout(data: LogoutRequest, db: Session = Depends(get_db)):
    return logout_user(db, data.access_token, data.refresh_token)
