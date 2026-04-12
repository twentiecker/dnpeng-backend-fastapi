from sqlalchemy.orm import Session
from app.models.files import Files


def get_all_files(db: Session):
    return db.query(Files).all()


def save(db: Session, data: dict):
    file = Files(**data)
    db.add(file)
    db.commit()
    db.refresh(file)
    return file
