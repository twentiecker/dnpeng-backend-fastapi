from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session
from typing import Optional
from app.api.deps import get_db
from app.features.eksim.schema import EksimCreate, EksimResponse
from app.features.eksim import service

router = APIRouter()


@router.post("/data", response_model=EksimResponse)
def create_eksim(data: EksimCreate, db: Session = Depends(get_db)):
    return service.add_eksim(
        db,
        data.kode,
        data.deskripsi,
        data.satuan,
        data.konversi,
        data.periode,
        data.nilai,
    )


@router.get("/data")
def eksim_data(
    kode: Optional[str] = Query(None),
    periode: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return service.get_eksim_data(db, kode, periode)


@router.get("/kode")
def eksim_kode(kode: str, db: Session = Depends(get_db)):
    return service.get_eksim_kode(db, kode)


@router.get("/periode")
def eksim_periode(periode: str, db: Session = Depends(get_db)):
    return service.get_eksim_periode(db, periode)


@router.get("/timeseries")
def eksim_timeseries(
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
def eksim_latest(db: Session = Depends(get_db)):
    return service.get_latest(db)


@router.get("/growth")
def eksim_growth(kode: str, type: str, db: Session = Depends(get_db)):
    return service.get_growth_rate(db, kode, type)


@router.get("/quarter")
def eksim_quarter(kode: str, db: Session = Depends(get_db)):
    return service.get_quarter_data(db, kode)


@router.get("/annual")
def eksim_annual(kode: str, db: Session = Depends(get_db)):
    return service.get_annual_data(db, kode)


@router.get("/chart")
def eksim_chart(kode: str, db: Session = Depends(get_db)):
    return service.get_chart_data(db, kode)


@router.get("/growth/chart")
def eksim_growth_chart(
    kode: str,
    type: str = "qtoq",
    db: Session = Depends(get_db),
):
    return service.get_growth_chart(db, kode, type)


@router.get("/quarter/chart")
def eksim_quarter_chart(
    kode: str,
    db: Session = Depends(get_db),
):
    return service.get_quarter_chart(db, kode)


@router.get("/annual/chart")
def eksim_annual_chart(
    kode: str,
    db: Session = Depends(get_db),
):
    return service.get_annual_chart(db, kode)
