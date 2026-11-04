from sqlalchemy.orm import Session
from app.models.comment import Comment


def create_comment(
    db: Session,
    comment: Comment,
) -> Comment:
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


def get_comment_by_id(
    db: Session,
    comment_id: str,
) -> Comment | None:
    return db.query(Comment).filter(Comment.id == comment_id).first()


def get_comments_by_document_id(
    db: Session,
    document_id: str,
) -> list[Comment]:
    return (
        db.query(Comment)
        .filter(Comment.document_id == document_id)
        .order_by(Comment.created_at.desc())
        .all()
    )


def update_comment(
    db: Session,
    comment: Comment,
) -> Comment:
    db.commit()
    db.refresh(comment)

    return comment


def delete_comment(
    db: Session,
    comment: Comment,
) -> None:
    db.delete(comment)
    db.commit()
