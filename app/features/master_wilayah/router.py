from fastapi import (
    APIRouter,
    Depends,
)
from typing import Optional
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.features.master_wilayah.schema import MasterWilayahResponse
from app.features.master_wilayah import service

router = APIRouter()


@router.get(
    "",
    response_model=list[MasterWilayahResponse],
    summary="Mengambil data master wilayah",
)
def get_master_wilayah(
    level: Optional[str] = None,
    parent_kode: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return service.get_master_wilayah(
        db=db,
        level=level,
        parent_kode=parent_kode,
        search=search,
    )


@router.get(
    "/nasional",
    response_model=list[MasterWilayahResponse],
    summary="Mengambil data nasional",
)
def get_nasional(
    db: Session = Depends(get_db),
):
    return service.get_master_wilayah(
        db=db,
        level="NASIONAL",
    )


@router.get(
    "/provinsi",
    response_model=list[MasterWilayahResponse],
    summary="Mengambil daftar provinsi",
)
def get_provinsi(
    search: str | None = None,
    db: Session = Depends(get_db),
):
    return service.get_master_wilayah(
        db=db,
        level="PROVINSI",
        search=search,
    )


@router.get(
    "/kabkot",
    response_model=list[MasterWilayahResponse],
    summary="Mengambil daftar kabupaten/kota",
)
def get_kabkot(
    parent_kode: str,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    return service.get_master_wilayah(
        db=db,
        level="KABKOT",
        parent_kode=parent_kode,
        search=search,
    )


@router.get(
    "/kecamatan",
    response_model=list[MasterWilayahResponse],
    summary="Mengambil daftar kecamatan",
)
def get_kecamatan(
    parent_kode: str,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    return service.get_master_wilayah(
        db=db,
        level="KECAMATAN",
        parent_kode=parent_kode,
        search=search,
    )


@router.get(
    "/desa",
    response_model=list[MasterWilayahResponse],
    summary="Mengambil daftar desa",
)
def get_desa(
    parent_kode: str,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    return service.get_master_wilayah(
        db=db,
        level="DESA",
        parent_kode=parent_kode,
        search=search,
    )
