from datetime import (
    datetime,
    timedelta,
    timezone,
)
from jose import jwt
from fastapi import HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.models.token_blacklist import TokenBlacklist
from app.core.config import settings
from app.core.security import hash_token
from app.features.auth import repository as token_repo
from app.repositories import user as user_repo


def create_access_token(data: dict):
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    data.update({"exp": expire})
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict):
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    data.update({"exp": expire})
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


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
    blacklisted = token_repo.get_blacklisted_token(db, hash_token(refresh_token))
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
    user = user_repo.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    blacklist_token(db, refresh_token, "refresh")
    new_access_token = create_access_token(
        {"sub": user.email, "role": user.role, "type": "access"}
    )
    new_refresh_token = create_refresh_token({"sub": user.email, "type": "refresh"})
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


def blacklist_token(db, token: str, token_type: str):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        exp = payload.get("exp")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    entry = TokenBlacklist(
        token=hash_token(token),
        token_type=token_type,
        expired_at=datetime.fromtimestamp(exp),
    )
    token_repo.create_token(db, entry)
