from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # Argon default setting
# pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Argon hardcore setting
pwd_context = CryptContext(
    schemes=["argon2"],
    argon2__memory_cost=102400,
    argon2__time_cost=3,
    argon2__parallelism=8,
    deprecated="auto",
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict):
    expire = datetime.utcnow() + timedelta(days=7)
    data.update({"exp": expire})
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
