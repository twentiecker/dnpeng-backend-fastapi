from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from urllib.parse import unquote
from app.features.files.schema import FileUploadResponse
from app.features.files.service import get_files_by_category, upload_document
from app.api.deps import get_db, get_current_user
from app.core.config import settings
import os

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
def upload_file(
    user=Depends(get_current_user),
    file: UploadFile = File(...),
    jenis_file: str = Form(...),
    tanggal_rilis: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        result = upload_document(file, jenis_file, tanggal_rilis, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{category}")
def get_files(category: str):
    return get_files_by_category(category)


# -----------------------------
# Router untuk Development
# -----------------------------
@router.get("/download/{category}/{filename}")
def download_file(category: str, filename: str):
    # 🔒 validasi category
    if category not in settings.ALLOWED_CATEGORIES:
        raise HTTPException(status_code=404, detail="Category not found")
    # __file__ ada di app/features/ → naik dua level ke project root
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    file_path = os.path.join(project_root, "public", "files", category, filename)
    # 🔒 validasi file ada
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    return FileResponse(
        path=file_path, filename=filename, media_type="application/octet-stream"
    )


# -----------------------------
# Router untuk CPanel
# -----------------------------
@router.get("/download/{category}/{filename}")
def download_file(category: str, filename: str):
    filename = unquote(filename)
    if category not in settings.ALLOWED_CATEGORIES:
        raise HTTPException(status_code=404, detail="Category not found")
    file_path = os.path.join(settings.BASE_PATH_CPANEL, category, filename)
    try:
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/octet-stream",
        )
    except Exception as e:
        # ini untuk debug sementara
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")


# -----------------------------
# Router untuk Development
# -----------------------------
@router.get("/view/{category}/{filename}")
def view_file(category: str, filename: str):
    # 🔒 validasi category
    if category not in settings.ALLOWED_CATEGORIES:
        raise HTTPException(status_code=404, detail="Category not found")
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    file_path = os.path.join(project_root, "public", "files", category, filename)
    # 🔒 validasi file ada
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    # FileResponse tanpa 'attachment' → browser akan coba buka langsung
    return FileResponse(
        path=file_path,
        media_type="application/pdf",  # ganti sesuai tipe dokumen, misal 'application/msword' untuk .doc
    )


# -----------------------------
# Router untuk CPanel
# -----------------------------
@router.get("/view/{category}/{filename}")
def download_file(category: str, filename: str):
    filename = unquote(filename)
    if category not in settings.ALLOWED_CATEGORIES:
        raise HTTPException(status_code=404, detail="Category not found")
    file_path = os.path.join(settings.BASE_PATH_CPANEL, category, filename)
    try:
        return FileResponse(
            path=file_path,
            media_type="application/pdf",
        )
    except Exception as e:
        # ini untuk debug sementara
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")
