from sqlalchemy.orm import Session
from app.models.user import User


def get_users_role(role: str, db: Session):
    return db.query(User).filter(User.role == role).all()
