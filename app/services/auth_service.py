from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from jose import jwt, JWTError

from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.models.user import User
from app.models.token_blacklist import TokenBlacklist
from app.repositories.user_repository import get_user_by_email, create_user


def register_user(db: Session, email: str, password: str):
    if get_user_by_email(db, email):
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=email,
        hashed_password=hash_password(password),
        role="user",
        is_active=True,
    )
    return create_user(db, user)


def login_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User inactive",
        )

    accses_token = create_access_token({"sub": user.email, "role": user.role})
    refresh_token = create_refresh_token({"sub": user.email})
    return {
        "access_token": accses_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# =========================
# REFRESH TOKEN
# =========================
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

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # cek blacklist
    blacklisted = (
        db.query(TokenBlacklist).filter(TokenBlacklist.token == refresh_token).first()
    )

    if blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )

    user = get_user_by_email(db, email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    new_access_token = create_access_token({"sub": user.email, "role": user.role})

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }


# =========================
# LOGOUT
# =========================
def logout_user(db: Session, refresh_token: str):
    try:
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        exp = payload.get("exp")

        expired_at = datetime.utcfromtimestamp(exp)

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    token_entry = TokenBlacklist(
        token=refresh_token,
        expired_at=expired_at,
    )

    db.add(token_entry)
    db.commit()

    return {"message": "Successfully logged out"}
