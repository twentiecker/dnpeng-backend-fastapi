from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.features.projects.schema import ProjectDocumentStatus

from app.db.base import Base


class ProjectDocument(Base):
    __tablename__ = "project_documents"

    id = Column(String, primary_key=True)

    project_id = Column(
        String,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )

    document_id = Column(
        String,
        nullable=False,
        unique=True,
    )

    document = Column(String, nullable=False)

    file_path = Column(
        String,
        nullable=False,
    )

    status = Column(
        String,
        default=ProjectDocumentStatus.NEW.value,
        nullable=False,
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    project = relationship(
        "Project",
        back_populates="documents",
    )

    creator = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="documents_created",
    )

    comments = relationship(
        "Comment",
        back_populates="project_document",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
