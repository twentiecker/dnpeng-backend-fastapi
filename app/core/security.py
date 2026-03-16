from passlib.context import CryptContext
import hashlib

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


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
