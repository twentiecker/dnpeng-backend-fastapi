from sqlalchemy.orm import Session
from app.models.token_blacklist import TokenBlacklist


def create_token(db: Session, data: TokenBlacklist):
    db.add(data)
    db.commit()


def get_blacklisted_token(db: Session, token_hash: str):
    return db.query(TokenBlacklist).filter(TokenBlacklist.token == token_hash).first()
