from datetime import datetime
from pydantic import BaseModel
from enum import Enum
from app.features.users.schema import UserMiniResponse


class ProjectDocumentStatus(str, Enum):
    NEW = "NEW"
    ON_PROGRESS = "ON_PROGRESS"
    FINISHED = "FINISHED"


class ProjectDocumentCreate(BaseModel):
    document_id: str
    document: str
    file_path: str


class ProjectCreate(BaseModel):
    category: str
    project: str
    documents: list[ProjectDocumentCreate]


class ProjectDocumentResponse(BaseModel):
    id: str
    project_id: str

    document_id: str
    document: str

    file_path: str

    status: str

    creator: UserMiniResponse

    created_at: datetime

    class Config:
        from_attributes = True


class ProjectMemberResponse(BaseModel):
    id: int
    user_id: int
    name: str
    email: str

    class Config:
        from_attributes = True


class ProjectMemberCreate(BaseModel):
    user_id: int


class ProjectResponse(BaseModel):
    id: str

    category: str
    project: str

    creator: UserMiniResponse

    created_at: datetime

    documents: list[ProjectDocumentResponse]

    members: list[ProjectMemberResponse]

    is_member: bool

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    id: str

    category: str
    project: str

    created_by: str
    created_at: datetime

    total_documents: int
    completed_documents: int


class ProjectDocumentStatusUpdate(BaseModel):
    status: ProjectDocumentStatus


class MessageResponse(BaseModel):
    message: str


class ProjectUpdate(BaseModel):
    category: str | None = None
    project: str | None = None


class ProjectSummaryResponse(BaseModel):
    total_projects: int
    total_documents: int

    new_documents: int
    on_progress_documents: int
    finished_documents: int
