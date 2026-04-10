from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from jose import jwt
from app.core.config import settings
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories import user as repo
from app.features.auth.services import token_service
import logging

logger = logging.getLogger(__name__)


def register_user(db: Session, name: str, email: str, password: str):
    if repo.get_user_by_email(db, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    user = User(
        name=name,
        email=email,
        hashed_password=hash_password(password),
        role="user",
        is_active=True,
    )
    logger.info(f"New user registered: {email}")
    return repo.create_user(db, user)


def login_user(db: Session, email: str, password: str, ip: str):
    user = repo.get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User inactive",
        )
    logger.info(f"User login success: {email} from {ip}")
    access_token = token_service.create_access_token(
        {"sub": user.email, "role": user.role, "type": "access"}
    )
    refresh_token = token_service.create_refresh_token(
        {"sub": user.email, "type": "refresh"}
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def logout_user(db: Session, access_token: str, refresh_token: str):
    token_service.blacklist_token(db, access_token, "access")
    token_service.blacklist_token(db, refresh_token, "refresh")
    payload = jwt.decode(
        access_token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
    email = payload.get("sub")
    logger.info(f"User logout: {email}")
    return {"message": "Successfully logged out"}
