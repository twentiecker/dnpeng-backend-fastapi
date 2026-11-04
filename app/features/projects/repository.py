from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models.project import Project
from app.models.project_document import ProjectDocument
from app.models.project_member import ProjectMember


def create_project(
    db: Session,
    project: Project,
):
    db.add(project)
    db.commit()
    db.refresh(project)

    return project


def get_project_members(
    db: Session,
    project_id: str,
):
    return (
        db.query(ProjectMember)
        .options(joinedload(ProjectMember.user))
        .filter(ProjectMember.project_id == project_id)
        .all()
    )


def get_project_member(
    db: Session,
    project_id: str,
    user_id: int,
):
    return (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        .first()
    )


def create_project_member(
    db: Session,
    member: ProjectMember,
):
    db.add(member)
    db.commit()
    db.refresh(member)

    return member


# Optimasi get_projects jika projek sudah banyak
def get_projects(
    db: Session,
    category: str,
):
    # return (
    #     db.query(Project)
    #     .options(joinedload(Project.documents))
    #     .filter(Project.category == category)
    #     .order_by(Project.created_at.desc())
    #     .all()
    # )

    return (
        db.query(Project)
        .options(
            joinedload(Project.documents),
            joinedload(Project.project_members).joinedload(ProjectMember.user),
        )
        .filter(Project.category == category)
        .order_by(Project.created_at.desc())
        .all()
    )


def get_project_document_by_id(
    db: Session,
    document_id: str,
):
    return db.query(ProjectDocument).filter(ProjectDocument.id == document_id).first()


def get_project_by_id(
    db: Session,
    project_id: str,
):
    # return (
    #     db.query(Project)
    #     .options(joinedload(Project.documents))
    #     .filter(Project.id == project_id)
    #     .first()
    # )

    return (
        db.query(Project)
        .options(
            joinedload(Project.documents),
            joinedload(Project.project_members).joinedload(ProjectMember.user),
        )
        .filter(Project.id == project_id)
        .first()
    )


def create_project_documents(
    db: Session,
    documents: list[ProjectDocument],
):
    db.add_all(documents)
    db.commit()

    return documents


def get_project_document(
    db: Session,
    project_id: str,
    document_id: str,
):
    return (
        db.query(ProjectDocument)
        .filter(
            ProjectDocument.project_id == project_id,
            ProjectDocument.id == document_id,
        )
        .first()
    )


def update_project_document(
    db: Session,
    document: ProjectDocument,
) -> ProjectDocument:
    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def delete_project_document(
    db: Session,
    document: ProjectDocument,
):
    db.delete(document)
    db.commit()


def update_project(
    db: Session,
    project: Project,
) -> Project:
    db.add(project)
    db.commit()
    db.refresh(project)

    return project


def delete_project(
    db: Session,
    project: Project,
) -> None:
    db.delete(project)
    db.commit()


def get_project_summary(
    db: Session,
):
    total_projects = db.query(func.count(Project.id)).scalar()

    total_documents = db.query(func.count(ProjectDocument.id)).scalar()

    new_documents = (
        db.query(func.count(ProjectDocument.id))
        .filter(ProjectDocument.status == "NEW")
        .scalar()
    )

    on_progress_documents = (
        db.query(func.count(ProjectDocument.id))
        .filter(ProjectDocument.status == "ON PROGRESS")
        .scalar()
    )

    finished_documents = (
        db.query(func.count(ProjectDocument.id))
        .filter(ProjectDocument.status == "FINISHED")
        .scalar()
    )

    return {
        "total_projects": total_projects,
        "total_documents": total_documents,
        "new_documents": new_documents,
        "on_progress_documents": on_progress_documents,
        "finished_documents": finished_documents,
    }


def delete_project_member(
    db: Session,
    member: ProjectMember,
):
    db.delete(member)
    db.commit()


def get_project_member_by_user(
    db: Session,
    project_id: str,
    user_id: int,
):
    return (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        .first()
    )
