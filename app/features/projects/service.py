from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import exists

from fastapi import (
    HTTPException,
    status,
    UploadFile,
)

from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.project import Project
from app.models.project_document import ProjectDocument
from app.models.user import User
from app.models.project_member import ProjectMember

from app.features.projects.schema import (
    ProjectCreate,
    ProjectDocumentCreate,
    ProjectDocumentStatusUpdate,
    ProjectUpdate,
    ProjectDocumentStatus,
)

from app.features.projects.repository import (
    create_project,
    get_projects,
    get_project_by_id,
    create_project_documents,
    get_project_document,
    update_project_document,
    delete_project_document,
    update_project,
    delete_project,
    get_project_summary,
    get_project_document_by_id,
    get_project_members,
    get_project_member,
    create_project_member,
    delete_project_member,
)

from app.features.projects.utils import generate_document_id, delete_file


def build_project_response(
    project: Project,
    current_user: User,
):
    return {
        "id": project.id,
        "category": project.category,
        "project": project.project,
        "creator": project.creator,
        "created_at": project.created_at,
        "documents": project.documents,
        "members": build_project_members_response(project),
        "is_member": any(
            member.user_id == current_user.id for member in project.project_members
        ),
    }


def build_project_members_response(project: Project):
    return [
        {
            "id": member.id,
            "user_id": member.user_id,
            "name": member.user.name,
            "email": member.user.email,
        }
        for member in project.project_members
    ]


def add_project_member_service(
    db: Session,
    project_id: str,
    user_id: int,
    current_user: User,
):
    project = get_project_or_404(
        db=db,
        project_id=project_id,
    )

    # Hanya creator project yang boleh
    # menambahkan member
    if project.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner can add members",
        )

    # Pastikan user yang akan ditambahkan memang ada
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Jangan boleh duplicate
    existing_member = get_project_member(
        db=db,
        project_id=project.id,
        user_id=user.id,
    )

    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a project member",
        )

    member = ProjectMember(
        project_id=project.id,
        user_id=user.id,
    )

    project_member = create_project_member(
        db=db,
        member=member,
    )

    return {
        "id": project_member.id,
        "user_id": project_member.user_id,
        "name": project_member.user.name,
        "email": project_member.user.email,
    }


def get_project_members_service(
    db: Session,
    project_id: str,
):
    project = get_project_or_404(
        db=db,
        project_id=project_id,
    )

    members = get_project_members(
        db=db,
        project_id=project.id,
    )

    return [
        {
            "id": member.id,
            "user_id": member.user_id,
            "name": member.user.name,
            "email": member.user.email,
        }
        for member in members
    ]


def create_project_service(
    db: Session,
    payload: ProjectCreate,
    current_user: User,
):

    now = datetime.now(timezone.utc)

    project = Project(
        id=str(uuid4()),
        category=payload.category,
        project=payload.project,
        created_by=current_user.id,
        created_at=now,
    )

    project.project_members = [ProjectMember(user_id=current_user.id)]

    project.documents = [
        ProjectDocument(
            id=str(uuid4()),
            document_id=generate_document_id(doc.document_id),
            document=doc.document,
            file_path=doc.file_path,
            status="NEW",
            created_at=now,
            created_by=current_user.id,
        )
        for doc in payload.documents
    ]

    project = create_project(
        db=db,
        project=project,
    )

    return build_project_response(
        project=project,
        current_user=current_user,
    )


def get_projects_service(
    db: Session,
    category: str,
    current_user: User,
):
    projects = get_projects(
        db=db,
        category=category,
    )

    return [
        build_project_response(
            project=project,
            current_user=current_user,
        )
        for project in projects
    ]


def get_project_document_by_id_service(
    db: Session,
    document_id: str,
):
    project_document = get_project_document_by_id(
        db=db,
        document_id=document_id,
    )

    if not project_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project document not found",
        )

    return project_document


def get_project_or_404(
    db: Session,
    project_id: str,
):
    project = get_project_by_id(
        db=db,
        project_id=project_id,
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project


def get_project_document_or_404(
    db: Session,
    project_id: str,
    document_id: str,
):
    document = get_project_document(
        db=db,
        project_id=project_id,
        document_id=document_id,
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document


def get_project_detail_service(
    db: Session,
    project_id: str,
    current_user: User,
):
    project = get_project_or_404(
        db=db,
        project_id=project_id,
    )

    # return project

    # return {
    #     "id": project.id,
    #     "category": project.category,
    #     "project": project.project,
    #     "creator": project.creator,
    #     "created_at": project.created_at,
    #     "documents": project.documents,
    #     "members": build_project_members_response(project),
    #     "is_member": any(
    #         member.user_id == current_user.id for member in project.project_members
    #     ),
    # }

    return build_project_response(
        project=project,
        current_user=current_user,
    )


def add_document_to_project_service(
    db: Session,
    project_id: str,
    payload: list[ProjectDocumentCreate],
    current_user: User,
):
    project = get_project_or_404(
        db=db,
        project_id=project_id,
    )

    now = datetime.now(timezone.utc)

    documents = [
        ProjectDocument(
            id=str(uuid4()),
            project_id=project.id,
            document_id=generate_document_id(doc.document_id),
            document=doc.document,
            file_path=doc.file_path,
            status="NEW",
            created_at=now,
            created_by=current_user.id,
        )
        for doc in payload
    ]

    return create_project_documents(
        db=db,
        documents=documents,
    )


def update_project_document_status_service(
    db: Session,
    project_id: str,
    document_id: str,
    payload: ProjectDocumentStatusUpdate,
    current_user: User,
):
    document = get_project_document_or_404(
        db=db,
        project_id=project_id,
        document_id=document_id,
    )

    if document.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only document owner can change document status",
        )

    current_status = document.status
    new_status = payload.status.value

    allowed_transition = {
        ProjectDocumentStatus.ON_PROGRESS.value: [
            ProjectDocumentStatus.FINISHED.value,
        ],
        ProjectDocumentStatus.FINISHED.value: [],
    }

    if current_status not in allowed_transition:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status {current_status} cannot be changed",
        )

    if new_status not in allowed_transition[current_status]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot change status from {current_status} to {new_status}",
        )

    document.status = new_status

    return update_project_document(
        db=db,
        document=document,
    )


def delete_project_document_service(
    db: Session,
    project_id: str,
    document_id: str,
    current_user: User,
    force: bool = False,
):
    document = get_project_document_or_404(
        db=db,
        project_id=project_id,
        document_id=document_id,
    )

    if document.creator.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only document owner can delete document",
        )

    has_comments = db.query(
        exists().where(Comment.document_id == document.document_id)
    ).scalar()

    if has_comments and not force:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Dokumen masih memiliki komentar",
                "has_comments": True,
                "can_force_delete": True,
            },
        )

    delete_file(document.file_path)

    delete_project_document(
        db=db,
        document=document,
    )

    return {"message": "Project document berhasil dihapus"}


def update_project_service(
    db: Session,
    project_id: str,
    payload: ProjectUpdate,
    current_user: User,
):
    project = get_project_or_404(
        db=db,
        project_id=project_id,
    )

    if payload.category is not None:
        project.category = payload.category

    if payload.project is not None:
        project.project = payload.project

    project = update_project(
        db=db,
        project=project,
    )

    return build_project_response(
        project=project,
        current_user=current_user,
    )


def delete_project_service(
    db: Session,
    project_id: str,
    current_user: User,
    force: bool = False,
):
    project = get_project_or_404(
        db=db,
        project_id=project_id,
    )

    print("project.creator.id:", project.creator.id)
    print("current_user.id:", current_user.id)

    if project.creator.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner can delete project",
        )

    document_count = len(project.documents)

    if document_count > 0 and not force:
        raise HTTPException(
            status_code=409,
            detail={
                "message": f"Project masih memiliki {document_count} dokumen",
                "document_count": document_count,
                "can_force_delete": True,
            },
        )

    # ===========================
    # Hapus seluruh file
    # ===========================
    for document in project.documents:
        delete_file(document.file_path)

    delete_project(
        db=db,
        project=project,
    )

    return {
        "message": "Project berhasil dihapus",
    }


def get_project_summary_service(
    db: Session,
):
    return get_project_summary(
        db=db,
    )


def finish_project_document_service(
    db: Session,
    document_id: str,
    current_user: User,
):

    document = (
        db.query(ProjectDocument)
        .filter(ProjectDocument.document_id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    if document.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only document owner can finish document",
        )

    document.status = ProjectDocumentStatus.FINISHED.value

    db.commit()
    db.refresh(document)

    return document


def remove_project_member_service(
    db: Session,
    project_id: str,
    user_id: int,
    current_user: User,
):
    project = get_project_or_404(
        db=db,
        project_id=project_id,
    )

    # Hanya creator project yang boleh menghapus member
    if project.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner can remove members",
        )

    # Creator tidak boleh dihapus dari project member
    if user_id == project.created_by:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project owner cannot be removed from project members",
        )

    member = get_project_member(
        db=db,
        project_id=project.id,
        user_id=user_id,
    )

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project member not found",
        )

    delete_project_member(
        db=db,
        member=member,
    )

    return {
        "message": "Project member berhasil dihapus",
    }
