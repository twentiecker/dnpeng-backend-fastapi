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
    filename = Column(String)
    file_path = Column(String)
    jenis_file = Column(String, index=True)
    size = Column(Integer)

    __table_args__ = (
        UniqueConstraint("filename", "jenis_file", name="uq_filename_jenis"),
    )
