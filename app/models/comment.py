from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Text,
    JSON,
    DateTime,
)
from datetime import datetime, timezone
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

# from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.orm import declarative_base
# import uuid
from app.db.base import Base


class Comment(Base):
    __tablename__ = "comments"

    # id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id = Column(String, primary_key=True)
    # document_id = Column(String, nullable=False, index=True)
    document_id = Column(
        String,
        ForeignKey("project_documents.document_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    page_number = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    width = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    text = Column(Text, nullable=False)
    selected_text = Column(Text)
    highlight_rects = Column(JSON)
    status = Column(String, nullable=False, default="new")
    status_history = Column(JSON, nullable=False, default=list)

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
        back_populates="comments_created",
    )

    project_document = relationship(
        "ProjectDocument",
        back_populates="comments",
    )
