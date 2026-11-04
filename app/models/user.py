from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(
        String,
        default="user",
        nullable=False,
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    documents_created = relationship(
        "ProjectDocument",
        back_populates="creator",
        lazy="selectin",
    )

    projects_created = relationship(
        "Project",
        back_populates="creator",
        lazy="selectin",
    )

    comments_created = relationship(
        "Comment",
        back_populates="creator",
        lazy="selectin",
    )

    project_members = relationship(
        "ProjectMember",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
