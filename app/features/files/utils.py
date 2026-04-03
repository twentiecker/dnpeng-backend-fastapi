import os
import shutil
from fastapi import UploadFile
from datetime import datetime
from app.core.config import settings


def format_date(date_str):
    dt = datetime.strptime(date_str, "%d%m%Y")
    return dt.strftime("%d %b %Y")


def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{round(size_bytes / 1024, 1)} KB"
    else:
        return f"{round(size_bytes / (1024 * 1024), 1)} MB"


def validate_file_extension(filename: str):
    ext = os.path.splitext(filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise ValueError("Format file tidak didukung")


def validate_date_format(tanggal: str):
    if len(tanggal) != 8 or not tanggal.isdigit():
        raise ValueError("Format tanggal harus ddmmyyyy")


def generate_filename(filename: str, tanggal_rilis: str):
    name = os.path.splitext(filename)[0]
    ext = os.path.splitext(filename)[1].lower()
    return f"{name}_{tanggal_rilis}{ext}"


def save_file(file: UploadFile, jenis_file: str, tanggal_rilis: str):
    validate_file_extension(file.filename)
    validate_date_format(tanggal_rilis)

    folder_path = os.path.join(settings.BASE_PATH, jenis_file)

    # buat folder kalau belum ada
    os.makedirs(folder_path, exist_ok=True)

    new_filename = generate_filename(file.filename.replace("_", " "), tanggal_rilis)
    file_path = os.path.join(folder_path, new_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": new_filename,
        "file_path": file_path,
        "size": os.path.getsize(file_path),
    }
