from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session
from typing import Optional
from app.api.deps import get_db
from app.features.pdb.schema import PdbCreate, PdbResponse
from app.features.pdb import service

router = APIRouter()


@router.post("/data", response_model=PdbResponse)
def create_pdb(data: PdbCreate, db: Session = Depends(get_db)):
    return service.add_pdb(
        db, data.kode, data.deskripsi, data.jenis, data.periode, data.nilai
    )


@router.get("/data")
def pdb_data(
    kode: Optional[int] = Query(None),
    jenis: Optional[str] = Query(None),
    periode: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return service.get_pdb_data(db, kode, jenis, periode)


@router.get("/kode")
def pdb_kode(
    kode: int, jenis: Optional[str] = Query(None), db: Session = Depends(get_db)
):
    return service.get_pdb_kode(db, kode, jenis)


@router.get("/periode")
def pdb_periode(
    periode: str, jenis: Optional[str] = Query(None), db: Session = Depends(get_db)
):
    return service.get_pdb_periode(db, periode, jenis)


@router.get("/timeseries")
def pdb_timeseries(
    kode: int = Query(...),
    jenis: Optional[str] = Query(None),
    start: Optional[str] = None,
    end: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return service.get_timeseries(db, kode, jenis, start, end)


@router.get("/indikator")
def indikator_list(db: Session = Depends(get_db)):
    return service.get_indikator_list(db)


@router.get("/latest")
def pdb_latest(jenis: Optional[str] = Query(None), db: Session = Depends(get_db)):
    return service.get_latest(db, jenis)


@router.get("/growth")
def pdb_growth(kode: int, jenis: str, type: str, db: Session = Depends(get_db)):
    return service.get_growth_rate(db, kode, jenis, type)


@router.get("/annual")
def pdb_annual(kode: int, jenis: str, db: Session = Depends(get_db)):
    return service.get_annual_data(db, kode, jenis)


@router.get("/chart")
def pdb_chart(kode: int, jenis: str, db: Session = Depends(get_db)):
    return service.get_chart_data(db, kode, jenis)


@router.get("/growth/chart")
def pdb_growth_chart(
    kode: int,
    jenis: str,
    type: str = "qtoq",
    db: Session = Depends(get_db),
):
    return service.get_growth_chart(db, kode, jenis, type)


@router.get("/annual/chart")
def pdb_annual_chart(
    kode: int,
    jenis: str,
    db: Session = Depends(get_db),
):
    return service.get_annual_chart(db, kode, jenis)
