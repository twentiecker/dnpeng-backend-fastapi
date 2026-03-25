from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.api.deps import get_db
from app.features.pkrt.schema import PkrtCreate
from app.features.pkrt import service

router = APIRouter()


@router.post("/data")
def create_pkrt(data: PkrtCreate, db: Session = Depends(get_db)):
    return service.add_pkrt(db, data.kode, data.deskripsi, data.periode, data.nilai)


@router.get("/data")
def pkrt_data(
    kode: Optional[str] = Query(None),
    periode: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return service.get_pkrt_data(db, kode, periode)


@router.get("/kode")
def pkrt_kode(kode: str, db: Session = Depends(get_db)):
    return service.get_pkrt_kode(db, kode)


@router.get("/periode")
def pkrt_periode(periode: str, db: Session = Depends(get_db)):
    return service.get_pkrt_periode(db, periode)


@router.get("/timeseries")
def pkrt_timeseries(
    kode: str = Query(...),
    start: Optional[str] = None,
    end: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return service.get_timeseries(db, kode, start, end)


@router.get("/indikator")
def indikator_list(db: Session = Depends(get_db)):
    return service.get_indikator_list(db)


@router.get("/latest")
def indikator_list(db: Session = Depends(get_db)):
    return service.get_latest(db)


@router.get("/growth")
def pkrt_growth(kode: str, type: str, db: Session = Depends(get_db)):
    return service.get_growth_rate(db, kode, type)


@router.get("/annual")
def pkrt_annual(kode: str, db: Session = Depends(get_db)):
    return service.get_annual_data(db, kode)


@router.get("/chart")
def pkrt_chart(kode: str, db: Session = Depends(get_db)):
    return service.get_chart_data(db, kode)


@router.get("/growth/chart")
def pkrt_growth_chart(
    kode: str,
    type: str = "qtoq",
    db: Session = Depends(get_db),
):
    return service.get_growth_chart(db, kode, type)


@router.get("/annual/chart")
def pkrt_annual_chart(
    kode: str,
    db: Session = Depends(get_db),
):
    return service.get_annual_chart(db, kode)
