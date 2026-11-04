from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.models.user import User
from app.api.deps import get_db, get_current_user

from app.features.projects.schema import (
    ProjectCreate,
    ProjectResponse,
    ProjectDocumentResponse,
    ProjectDocumentCreate,
    ProjectDocumentStatusUpdate,
    MessageResponse,
    ProjectUpdate,
    ProjectSummaryResponse,
    ProjectMemberResponse,
    ProjectMemberCreate,
)

from app.features.projects.service import (
    create_project_service,
    get_projects_service,
    get_project_detail_service,
    add_document_to_project_service,
    update_project_document_status_service,
    delete_project_document_service,
    update_project_service,
    delete_project_service,
    get_project_summary_service,
    get_project_document_by_id_service,
    finish_project_document_service,
    get_project_members_service,
    add_project_member_service,
    remove_project_member_service,
)

from app.models.project_document import ProjectDocument
from urllib.parse import unquote
from app.core.config import settings
import os
from fastapi.responses import FileResponse

router = APIRouter()


@router.post(
    "",
    response_model=ProjectResponse,
)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return create_project_service(
        db=db,
        payload=payload,
        current_user=current_user,
    )


@router.get(
    "",
    response_model=list[ProjectResponse],
)
def get_projects(
    category: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_projects_service(db, category, current_user)


@router.get(
    "/data/summary",
    response_model=ProjectSummaryResponse,
)
def get_project_summary_endpoint(
    db: Session = Depends(get_db),
):
    return get_project_summary_service(
        db=db,
    )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
def get_project_detail(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_project_detail_service(
        db=db,
        project_id=project_id,
        current_user=current_user,
    )


@router.post(
    "/{project_id}/documents",
    response_model=list[ProjectDocumentResponse],
)
def add_document_to_project(
    project_id: str,
    payload: list[ProjectDocumentCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return add_document_to_project_service(
        db=db,
        project_id=project_id,
        payload=payload,
        current_user=current_user,
    )


@router.patch(
    "/{project_id}/documents/{document_id}/status",
    response_model=ProjectDocumentResponse,
)
def update_project_document_status(
    project_id: str,
    document_id: str,
    payload: ProjectDocumentStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return update_project_document_status_service(
        db=db,
        project_id=project_id,
        document_id=document_id,
        payload=payload,
        current_user=current_user,
    )


@router.delete(
    "/{project_id}/documents/{document_id}",
    response_model=MessageResponse,
)
def delete_project_document(
    project_id: str,
    document_id: str,
    force: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return delete_project_document_service(
        db=db,
        project_id=project_id,
        document_id=document_id,
        force=force,
        current_user=current_user,
    )


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
)
def update_project(
    project_id: str,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_project_service(
        db=db, project_id=project_id, payload=payload, current_user=current_user
    )


@router.delete("/{project_id}")
def delete_project(
    project_id: str,
    force: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return delete_project_service(
        db=db,
        project_id=project_id,
        force=force,
        current_user=current_user,
    )


@router.get(
    "/document/{document_id}",
    response_model=ProjectDocumentResponse,
)
def get_project_document_by_id_endpoint(
    document_id: str,
    db: Session = Depends(get_db),
):
    return get_project_document_by_id_service(
        db=db,
        document_id=document_id,
    )


@router.get("/view/{filename}")
def view_file(filename: str, db: Session = Depends(get_db)):
    decoded_filename = unquote(filename)
    file = (
        db.query(ProjectDocument)
        .filter(ProjectDocument.document == decoded_filename)
        .first()
    )
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    if settings.ENV == "cpanel":
        base_path = settings.BASE_PATH_CPANEL
        relative_path = file.file_path.replace("public/files/", "")
    else:
        base_path = os.getcwd()
        relative_path = file.file_path

    file_path = os.path.join(base_path, relative_path)
    # 🔒 validasi file ada
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"File not found: {file_path}"
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",  # ganti sesuai tipe dokumen, misal 'application/msword' untuk .doc
    )


@router.patch(
    "/document/{document_id}/finish",
    response_model=ProjectDocumentResponse,
)
def finish_project_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return finish_project_document_service(
        db=db,
        document_id=document_id,
        current_user=current_user,
    )


@router.get(
    "/{project_id}/members",
    response_model=list[ProjectMemberResponse],
)
def get_project_members(
    project_id: str,
    db: Session = Depends(get_db),
):
    return get_project_members_service(
        db=db,
        project_id=project_id,
    )


@router.post(
    "/{project_id}/members",
    response_model=ProjectMemberResponse,
)
def add_project_member(
    project_id: str,
    payload: ProjectMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return add_project_member_service(
        db=db,
        project_id=project_id,
        user_id=payload.user_id,
        current_user=current_user,
    )


@router.delete(
    "/{project_id}/members/{user_id}",
    response_model=MessageResponse,
)
def remove_project_member(
    project_id: str,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return remove_project_member_service(
        db=db,
        project_id=project_id,
        user_id=user_id,
        current_user=current_user,
    )
