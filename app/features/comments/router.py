from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)
from sqlalchemy.orm import Session
from app.models.user import User
from app.api.deps import get_db, get_current_user
from app.features.comments.schema import (
    CommentCreate,
    CommentResponse,
    CommentStatusUpdate,
    CommentUpdate,
)
from app.features.comments.service import (
    create_comment_service,
    get_comment_by_id_service,
    get_comments_by_document_id_service,
    update_comment_status_service,
    update_comment_service,
    delete_comment_service,
)

router = APIRouter()


@router.post(
    "",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_comment_service(db=db, payload=payload, current_user=current_user)


@router.get(
    "/document/{document_id}",
    response_model=list[CommentResponse],
)
def get_comments_by_document(
    document_id: str,
    db: Session = Depends(get_db),
):
    return get_comments_by_document_id_service(
        db=db,
        document_id=document_id,
    )


@router.get(
    "/{comment_id}",
    response_model=CommentResponse,
)
def get_comment(
    comment_id: str,
    db: Session = Depends(get_db),
):
    return get_comment_by_id_service(
        db=db,
        comment_id=comment_id,
    )


@router.patch(
    "/{comment_id}/status",
    response_model=CommentResponse,
)
def update_comment_status(
    comment_id: str,
    payload: CommentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_comment_status_service(
        db=db,
        comment_id=comment_id,
        payload=payload,
        current_user=current_user,
        # reviewer_name="Admin",
    )


@router.patch(
    "/{comment_id}",
    response_model=CommentResponse,
)
def update_comment(
    comment_id: str,
    payload: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_comment_service(
        db=db,
        comment_id=comment_id,
        payload=payload,
        current_user=current_user,
    )


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_comment_service(
        db=db,
        comment_id=comment_id,
        current_user=current_user,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
