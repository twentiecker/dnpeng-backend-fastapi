from sqlalchemy.orm import Session
from app.models.user import User
from sqlalchemy import or_


def get_users_role(role: str, db: Session):
    return db.query(User).filter(User.role == role).all()


def update_password(
    user: User,
    hashed_password: str,
    db: Session,
):
    user.hashed_password = hashed_password

    db.commit()
    db.refresh(user)

    return user


def search_users(
    db: Session,
    keyword: str,
    limit: int = 20,
):
    return (
        db.query(User)
        .filter(
            User.is_active.is_(True),
            or_(
                User.name.ilike(f"%{keyword}%"),
                User.email.ilike(f"%{keyword}%"),
            ),
        )
        .order_by(User.name.asc())
        .limit(limit)
        .all()
    )
