from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.features.master_wilayah import repository as repo

VALID_LEVELS = {
    "NASIONAL",
    "PROVINSI",
    "KABKOT",
    "KECAMATAN",
    "DESA",
}


def get_master_wilayah(
    db: Session,
    level: str | None = None,
    parent_kode: str | None = None,
    search: str | None = None,
):
    if level:
        level = level.strip().upper()

        if level not in VALID_LEVELS:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Parameter level tidak valid. "
                    f"Gunakan salah satu: {', '.join(sorted(VALID_LEVELS))}"
                ),
            )

    if search:
        search = search.strip()

    return repo.get_master_wilayah(
        db=db,
        level=level,
        parent_kode=parent_kode,
        search=search,
    )
