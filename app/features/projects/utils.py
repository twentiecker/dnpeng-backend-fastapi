from fastapi import (
    HTTPException,
    status,
)
from datetime import datetime
from uuid import uuid4
from app.core.config import settings
import os


def generate_document_id(category: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    suffix = uuid4().hex[:4]

    return f"{category}_{timestamp}_{suffix}"


def delete_file(file_path: str):
    if settings.ENV == "cpanel":
        base_path = settings.BASE_PATH_CPANEL
        relative_path = file_path.replace("public/files/", "")
    else:
        base_path = os.getcwd()
        relative_path = file_path

    file_path = os.path.join(base_path, relative_path)
    if not file_path.startswith(os.path.abspath(base_path)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid path"
        )

    if os.path.exists(file_path):
        os.remove(file_path)
