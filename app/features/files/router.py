from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.features.files.service import get_files_by_category
import os

router = APIRouter()

BASE_FOLDER = "public/files"
ALLOWED_CATEGORIES = ["bri", "bi", "kemenkeu", "mandiri", "intl"]


@router.get("/{category}")
def get_files(category: str):
    return get_files_by_category(category)


@router.get("/download/{category}/{filename}")
def download_file(category: str, filename: str):
    # 🔒 validasi category
    if category not in ALLOWED_CATEGORIES:
        raise HTTPException(status_code=404, detail="Category not found")

    file_path = os.path.join(BASE_FOLDER, category, filename)

    # 🔒 validasi file ada
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream",  # paksa download
    )
