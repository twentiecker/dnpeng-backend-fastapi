from sqlalchemy import (
    Column,
    Integer,
    String,
    UniqueConstraint,
)
from app.db.base import Base


class Files(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    jenis_file = Column(String, index=True, nullable=False)
    size = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("filename", "jenis_file", name="uq_filename_jenis"),
    )
