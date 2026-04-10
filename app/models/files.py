from sqlalchemy import (
    Column,
    Integer,
    String,
)
from app.db.base import Base


class Files(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    file_path = Column(String)
    jenis_file = Column(String)
    size = Column(Integer)
