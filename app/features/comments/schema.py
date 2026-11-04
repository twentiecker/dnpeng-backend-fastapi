from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum
from app.features.users.schema import UserMiniResponse


class ReviewStatus(str, Enum):
    NEW = "new"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class StatusHistorySchema(BaseModel):
    status: str
    changed_at: str
    reviewer_name: str


class HighlightRectSchema(BaseModel):
    x: float
    y: float
    width: float
    height: float


class CommentCreate(BaseModel):
    document_id: str
    page_number: int
    type: str
    x: float
    y: float
    width: float
    height: float
    text: str
    selected_text: Optional[str] = None
    highlight_rects: Optional[list[HighlightRectSchema]] = None


class CommentStatusUpdate(BaseModel):
    status: ReviewStatus


class CommentUpdate(BaseModel):
    text: str


class CommentResponse(BaseModel):
    id: str
    document_id: str
    page_number: int
    type: str
    x: float
    y: float
    width: float
    height: float
    text: str
    selected_text: str | None = None
    highlight_rects: list[HighlightRectSchema] | None = None
    status: str
    status_history: list[StatusHistorySchema]
    creator: UserMiniResponse
    created_at: datetime

    class Config:
        from_attributes = True
