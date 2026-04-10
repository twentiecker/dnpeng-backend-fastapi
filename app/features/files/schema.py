from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    filename: str
    file_path: str
    jenis_file: str
    size: int
