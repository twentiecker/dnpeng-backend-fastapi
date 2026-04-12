from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session
from typing import Optional
from app.api.deps import get_db
from app.features.pmtb.schema import PmtbCreate, PmtbResponse
from app.features.pmtb import service

router = APIRouter()


@router.post("/data", response_model=PmtbResponse)
def create_pmtb(data: PmtbCreate, db: Session = Depends(get_db)):
    return service.add_pmtb(
        db,
        data.kode,
        data.deskripsi,
        data.satuan,
        data.konversi,
        data.periode,
        data.nilai,
    )


@router.get("/data")
def pmtb_data(
    kode: Optional[str] = Query(None),
    periode: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return service.get_pmtb_data(db, kode, periode)


@router.get("/kode")
def pmtb_kode(kode: str, db: Session = Depends(get_db)):
    return service.get_pmtb_kode(db, kode)


@router.get("/periode")
def pmtb_periode(periode: str, db: Session = Depends(get_db)):
    return service.get_pmtb_periode(db, periode)


@router.get("/timeseries")
def pmtb_timeseries(
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
def pmtb_latest(db: Session = Depends(get_db)):
    return service.get_latest(db)


@router.get("/growth")
def pmtb_growth(kode: str, type: str, db: Session = Depends(get_db)):
    return service.get_growth_rate(db, kode, type)


@router.get("/quarter")
def pmtb_quarter(kode: str, db: Session = Depends(get_db)):
    return service.get_quarter_data(db, kode)


@router.get("/annual")
def pmtb_annual(kode: str, db: Session = Depends(get_db)):
    return service.get_annual_data(db, kode)


@router.get("/chart")
def pmtb_chart(kode: str, db: Session = Depends(get_db)):
    return service.get_chart_data(db, kode)


@router.get("/growth/chart")
def pmtb_growth_chart(
    kode: str,
    type: str = "qtoq",
    db: Session = Depends(get_db),
):
    return service.get_growth_chart(db, kode, type)


@router.get("/quarter/chart")
def pmtb_quarter_chart(
    kode: str,
    db: Session = Depends(get_db),
):
    return service.get_quarter_chart(db, kode)


@router.get("/annual/chart")
def pmtb_annual_chart(
    kode: str,
    db: Session = Depends(get_db),
):
    return service.get_annual_chart(db, kode)
