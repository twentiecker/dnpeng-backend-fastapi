from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session
from typing import Optional
from app.api.deps import get_db
from app.features.pkp.schema import PkpCreate, PkpResponse
from app.features.pkp import service

router = APIRouter()


@router.post("/data", response_model=PkpResponse)
def create_pkp(data: PkpCreate, db: Session = Depends(get_db)):
    return service.add_pkp(
        db,
        data.kode,
        data.deskripsi,
        data.satuan,
        data.konversi,
        data.periode,
        data.nilai,
    )


@router.get("/data")
def pkp_data(
    kode: Optional[str] = Query(None),
    periode: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return service.get_pkp_data(db, kode, periode)


@router.get("/kode")
def pkp_kode(kode: str, db: Session = Depends(get_db)):
    return service.get_pkp_kode(db, kode)


@router.get("/periode")
def pkp_periode(periode: str, db: Session = Depends(get_db)):
    return service.get_pkp_periode(db, periode)


@router.get("/timeseries")
def pkp_timeseries(
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
def pkp_latest(db: Session = Depends(get_db)):
    return service.get_latest(db)


@router.get("/growth")
def pkp_growth(kode: str, type: str, db: Session = Depends(get_db)):
    return service.get_growth_rate(db, kode, type)


@router.get("/quarter")
def pkp_quarter(kode: str, db: Session = Depends(get_db)):
    return service.get_quarter_data(db, kode)


@router.get("/annual")
def pkp_annual(kode: str, db: Session = Depends(get_db)):
    return service.get_annual_data(db, kode)


@router.get("/chart")
def pkp_chart(kode: str, db: Session = Depends(get_db)):
    return service.get_chart_data(db, kode)


@router.get("/growth/chart")
def pkp_growth_chart(
    kode: str,
    type: str = "qtoq",
    db: Session = Depends(get_db),
):
    return service.get_growth_chart(db, kode, type)


@router.get("/quarter/chart")
def pkp_quarter_chart(
    kode: str,
    db: Session = Depends(get_db),
):
    return service.get_quarter_chart(db, kode)


@router.get("/annual/chart")
def pkp_annual_chart(
    kode: str,
    db: Session = Depends(get_db),
):
    return service.get_annual_chart(db, kode)
