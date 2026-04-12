import os
from datetime import datetime
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.features.files.utils import (
    extract_date_from_filename,
    save_file,
    format_date,
    format_size,
)
from app.features.files.repository import get_all_files, save
from app.core.config import settings


def get_recent_files(limit: int, db: Session):
    files = get_all_files(db)

    enriched_files = []

    for file in files:
        file_date = extract_date_from_filename(file.filename)

        if file_date:
            enriched_files.append(
                {
                    "id": file.id,
                    "filename": file.filename,
                    "file_path": file.file_path,
                    "jenis_file": file.jenis_file,
                    "size": format_size(file.size),
                    "date_obj": file_date,
                }
            )

    # sort descending (terbaru dulu)
    sorted_files = sorted(enriched_files, key=lambda x: x["date_obj"], reverse=True)

    # ✅ baru format setelah sorting
    result = []
    for file in sorted_files[:limit]:
        result.append(
            {
                "id": file["id"],
                "filename": file["filename"],
                "file_path": file["file_path"],
                "jenis_file": file["jenis_file"],
                "size": file["size"],
                "date": file["date_obj"].strftime("%d %b %Y"),
            }
        )

    return result


def get_files_by_category(category: str):
    folder_path = os.path.join(settings.BASE_PATH, category)

    if not os.path.exists(folder_path):
        return []

    result = []

    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)

        if os.path.isfile(filepath):
            # ✅ ambil extension
            name, ext = os.path.splitext(filename)

            # ❌ skip kalau bukan file yang diizinkan
            if ext.lower() not in settings.ALLOWED_EXTENSIONS:
                continue

            parts = name.split("_")

            name = parts[0]
            date_raw = parts[1] if len(parts) > 1 else None

            size = os.path.getsize(filepath)

            # 👉 parsing datetime untuk sorting
            date_obj = None
            if date_raw:
                try:
                    date_obj = datetime.strptime(date_raw, "%d%m%Y")
                except:
                    pass

            result.append(
                {
                    "file_name": name,
                    "ext_name": ext,
                    "date": format_date(date_raw) if date_raw else "-",
                    "size": format_size(size),
                    "path": f"/files/{category}/{filename}",
                    "original_name": filename,
                    "_date_obj": date_obj,  # 👉 field bantu
                }
            )

    # ✅ sorting: terbaru di atas
    result.sort(
        key=lambda x: x["_date_obj"] if x["_date_obj"] else datetime.min,
        reverse=True,
    )

    return result


def upload_document(file: UploadFile, jenis_file: str, tanggal_rilis: str, db: Session):
    result = save_file(file, jenis_file, tanggal_rilis)

    data = {
        "filename": result["filename"],
        "file_path": result["file_path"],
        "jenis_file": jenis_file,
        "size": result["size"],
    }

    # jika pakai DB
    if db:
        save(db, data)

    return data
