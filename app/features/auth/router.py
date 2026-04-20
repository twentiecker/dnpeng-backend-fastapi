from fastapi.security import OAuth2PasswordRequestForm
from fastapi import (
    APIRouter,
    Depends,
    Request,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session
from app.models.user import User
from app.api.deps import get_db, get_current_user
from app.schemas.user import UserCreate
from app.features.auth.schema import RefreshRequest, LogoutRequest
from app.features.auth.services import auth_service, token_service

router = APIRouter()


@router.post("/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    return auth_service.register_user(
        db, user.name, user.email, user.password, user.role
    )


@router.post("/login")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    return auth_service.login_user(
        db,
        form_data.username,
        form_data.password,
        request.client.host,
    )


@router.post("/refresh")
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    return token_service.refresh_access_token(db, data.refresh_token)


@router.post("/logout")
def logout(data: LogoutRequest, db: Session = Depends(get_db)):
    return auth_service.logout_user(db, data.access_token, data.refresh_token)
