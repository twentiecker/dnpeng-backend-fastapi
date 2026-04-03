from pydantic import BaseModel
from typing import Optional

class FileUploadResponse(BaseModel):
    filename: str
    file_path: str
    jenis_file: str
    size: int