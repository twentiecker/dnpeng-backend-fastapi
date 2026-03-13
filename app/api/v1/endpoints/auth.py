from fastapi.security import OAuth2PasswordRequestForm
from fastapi import (
    APIRouter,
    Depends,
    Request,
)
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.user import UserCreate
from app.schemas.request import RefreshRequest, LogoutRequest
from app.services import auth_service as service

router = APIRouter()


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    return service.register_user(db, user.name, user.email, user.password)


@router.post("/login")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    return service.login_user(
        db,
        form_data.username,
        form_data.password,
        request.client.host,
    )


@router.post("/refresh")
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    return service.refresh_access_token(db, data.refresh_token)


@router.post("/logout")
def logout(data: LogoutRequest, db: Session = Depends(get_db)):
    return service.logout_user(db, data.access_token, data.refresh_token)
