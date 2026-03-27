import os
from datetime import datetime

BASE_FOLDER = "public/files"


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


def get_files_by_category(category: str):
    folder_path = os.path.join(BASE_FOLDER, category)

    if not os.path.exists(folder_path):
        return []

    result = []

    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)

        if os.path.isfile(filepath):
            name_no_ext = filename.replace(".pdf", "")
            parts = name_no_ext.split("_")

            name = parts[0]
            date_raw = parts[1] if len(parts) > 1 else None

            size = os.path.getsize(filepath)

            result.append(
                {
                    "file_name": name,
                    "date": format_date(date_raw) if date_raw else "-",
                    "size": format_size(size),
                    "path": f"/files/{category}/{filename}",
                    "original_name": filename,
                }
            )

    return result
