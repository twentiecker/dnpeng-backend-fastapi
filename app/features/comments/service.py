from uuid import uuid4
from fastapi import HTTPException, status as http_status
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.comment import Comment
from app.models.user import User
from app.models.project_document import ProjectDocument
from app.features.projects.schema import ProjectDocumentStatus
from app.features.comments.schema import (
    ReviewStatus,
    CommentCreate,
    CommentStatusUpdate,
    CommentUpdate,
)
from app.features.comments.repository import (
    create_comment,
    get_comment_by_id,
    get_comments_by_document_id,
    update_comment,
    delete_comment,
)
from app.features.projects.repository import get_project_member_by_user


def create_comment_service(
    db: Session,
    payload: CommentCreate,
    current_user: User,
) -> Comment:

    project_document = (
        db.query(ProjectDocument)
        .filter(ProjectDocument.document_id == payload.document_id)
        .first()
    )

    if not project_document:
        raise HTTPException(status_code=404, detail="Document not found")

    if project_document.status == ProjectDocumentStatus.FINISHED.value:
        raise HTTPException(
            status_code=400, detail="Cannot add comment to finished document"
        )

    if project_document:
        if project_document.status == ProjectDocumentStatus.NEW.value:
            project_document.status = ProjectDocumentStatus.ON_PROGRESS.value

    comment = Comment(
        id=str(uuid4()),
        document_id=payload.document_id,
        page_number=payload.page_number,
        type=payload.type,
        x=payload.x,
        y=payload.y,
        width=payload.width,
        height=payload.height,
        text=payload.text,
        selected_text=payload.selected_text,
        highlight_rects=(
            [rect.model_dump() for rect in payload.highlight_rects]
            if payload.highlight_rects
            else None
        ),
        status=ReviewStatus.NEW.value,
        status_history=[],
        created_by=current_user.id,
        # created_by=current_user.name,
    )

    return create_comment(
        db=db,
        comment=comment,
    )


def get_comment_by_id_service(
    db: Session,
    comment_id: str,
) -> Comment:
    comment = get_comment_by_id(
        db=db,
        comment_id=comment_id,
    )

    if not comment:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    return comment


def get_comments_by_document_id_service(
    db: Session,
    document_id: str,
) -> list[Comment]:
    return get_comments_by_document_id(
        db=db,
        document_id=document_id,
    )


def update_comment_status_service(
    db: Session,
    comment_id: str,
    payload: CommentStatusUpdate,
    current_user: User,
) -> Comment:
    comment = get_comment_by_id(
        db=db,
        comment_id=comment_id,
    )

    if not comment:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    project_document = (
        db.query(ProjectDocument)
        .filter(ProjectDocument.document_id == comment.document_id)
        .first()
    )

    if not project_document:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    # if project_document.created_by != current_user.id:
    #     raise HTTPException(
    #         status_code=http_status.HTTP_403_FORBIDDEN,
    #         detail="Only document creator can change comment status",
    #     )

    project_member = get_project_member_by_user(
        db=db,
        project_id=project_document.project_id,
        user_id=current_user.id,
    )

    if project_document.created_by != current_user.id and not project_member:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Only document creator or project members can change comment status",
        )

    # Tidak ada perubahan status
    if comment.status == payload.status.value:
        return comment

    history = list(comment.status_history or [])

    history.append(
        {
            "status": payload.status.value,
            "changed_at": datetime.now(timezone.utc).isoformat(),
            "reviewer_id": current_user.id,
            "reviewer_name": current_user.name,
        }
    )

    comment.status = payload.status.value
    comment.status_history = history

    return update_comment(
        db=db,
        comment=comment,
    )


def update_comment_service(
    db: Session,
    comment_id: str,
    payload: CommentUpdate,
    current_user: User,
) -> Comment:

    comment = get_comment_by_id(
        db=db,
        comment_id=comment_id,
    )

    if not comment:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    if comment.created_by != current_user.id:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Only comment creator can update comment",
        )

    comment.text = payload.text

    return update_comment(
        db=db,
        comment=comment,
    )


def delete_comment_service(
    db: Session,
    comment_id: str,
    current_user: User,
) -> None:
    comment = get_comment_by_id(
        db=db,
        comment_id=comment_id,
    )

    if not comment:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    if comment.created_by != current_user.id:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Only comment creator can delete comment",
        )

    delete_comment(
        db=db,
        comment=comment,
    )
