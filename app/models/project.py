from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.db.base import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True)

    category = Column(String, nullable=False)
    project = Column(String, nullable=False)

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

    creator = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="projects_created",
    )

    documents = relationship(
        "ProjectDocument",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    project_members = relationship(
        "ProjectMember",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
