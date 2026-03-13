from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from jose import jwt, JWTError
from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    hash_token,
    create_access_token,
    create_refresh_token,
)
from app.models.user import User
from app.models.token_blacklist import TokenBlacklist
from app.repositories import user_repository as repo
from app.services import token_service as service
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

    access_token = create_access_token(
        {"sub": user.email, "role": user.role, "type": "access"}
    )
    refresh_token = create_refresh_token({"sub": user.email, "type": "refresh"})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def refresh_access_token(db: Session, refresh_token: str):
    try:
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    blacklisted = (
        db.query(TokenBlacklist)
        .filter(TokenBlacklist.token == hash_token(refresh_token))
        .first()
    )

    if blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )

    user = repo.get_user_by_email(db, email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    service.blacklist_token(db, refresh_token, "refresh")

    new_access_token = create_access_token(
        {"sub": user.email, "role": user.role, "type": "access"}
    )
    new_refresh_token = create_refresh_token({"sub": user.email, "type": "refresh"})

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


def logout_user(db: Session, access_token: str, refresh_token: str):
    service.blacklist_token(db, access_token, "access")
    service.blacklist_token(db, refresh_token, "refresh")

    payload = jwt.decode(
        access_token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
    email = payload.get("sub")

    logger.info(f"User logout: {email}")

    return {"message": "Successfully logged out"}
