from sqlalchemy import (
    String,
    Column,
    Integer,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class ProjectMember(Base):
    __tablename__ = "project_members"

    id = Column(Integer, primary_key=True, autoincrement=True)

    project_id = Column(
        String,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "user_id",
            name="uq_project_member",
        ),
    )

    project = relationship(
        "Project",
        back_populates="project_members",
    )

    user = relationship(
        "User",
        back_populates="project_members",
    )
