from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session
from typing import Optional
from app.api.deps import get_db
from app.features.pmtb.schema import (
    PmtbCreate,
    PmtbResponse,
    PmtbAggregatorResponse,
)
from app.features.pmtb import service

router = APIRouter()


@router.post("/data", response_model=PmtbResponse)
def create_pmtb(data: PmtbCreate, db: Session = Depends(get_db)):
    return service.add_pmtb(
        db,
        data.kode_wilayah,
        data.kode,
        data.deskripsi,
        data.satuan,
        data.konversi,
        data.periode,
        data.nilai,
    )


@router.get("/data", response_model=list[PmtbResponse])
def pmtb_data(
    kode_wilayah: str,
    kode: Optional[str] = Query(None),
    periode: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return service.get_pmtb_data(db, kode_wilayah, kode, periode)


@router.get("/kode", response_model=list[PmtbResponse])
def pmtb_kode(kode_wilayah: str, kode: str, db: Session = Depends(get_db)):
    return service.get_pmtb_kode(db, kode_wilayah, kode)


@router.get("/periode", response_model=list[PmtbResponse])
def pmtb_periode(kode_wilayah: str, periode: str, db: Session = Depends(get_db)):
    return service.get_pmtb_periode(db, kode_wilayah, periode)


@router.get("/timeseries")
def pmtb_timeseries(
    kode_wilayah: str,
    kode: str = Query(...),
    start: Optional[str] = None,
    end: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return service.get_timeseries(db, kode_wilayah, kode, start, end)


@router.get("/indikator")
def indikator_list(kode_wilayah: str, db: Session = Depends(get_db)):
    return service.get_indikator_list(
        db,
        kode_wilayah,
    )


@router.get("/latest", response_model=list[PmtbResponse])
def pmtb_latest(kode_wilayah: str, db: Session = Depends(get_db)):
    return service.get_latest(db, kode_wilayah)


@router.get("/growth")
def pmtb_growth(kode_wilayah: str, kode: str, type: str, db: Session = Depends(get_db)):
    return service.get_growth_rate(db, kode_wilayah, kode, type)


@router.get("/quarter")
def pmtb_quarter(kode_wilayah: str, kode: str, db: Session = Depends(get_db)):
    return service.get_quarter_data(db, kode_wilayah, kode)


@router.get("/annual")
def pmtb_annual(kode_wilayah: str, kode: str, db: Session = Depends(get_db)):
    return service.get_annual_data(db, kode_wilayah, kode)


@router.get("/chart")
def pmtb_chart(kode_wilayah: str, kode: str, db: Session = Depends(get_db)):
    return service.get_chart_data(db, kode_wilayah, kode)


@router.get("/growth/chart")
def pmtb_growth_chart(
    kode_wilayah: str,
    kode: str,
    type: str = "qtoq",
    db: Session = Depends(get_db),
):
    return service.get_growth_chart(db, kode_wilayah, kode, type)


@router.get("/quarter/chart")
def pmtb_quarter_chart(
    kode_wilayah: str,
    kode: str,
    db: Session = Depends(get_db),
):
    return service.get_quarter_chart(db, kode_wilayah, kode)


@router.get("/annual/chart")
def pmtb_annual_chart(
    kode_wilayah: str,
    kode: str,
    db: Session = Depends(get_db),
):
    return service.get_annual_chart(db, kode_wilayah, kode)


# =====================================
# Aggregator Router
# =====================================
@router.get(
    "/aggregated",
    response_model=PmtbAggregatorResponse,
)
def get_aggregated_data(
    kode_wilayah: str,
    db: Session = Depends(get_db),
):
    return service.get_aggregated_data(
        db,
        kode_wilayah,
    )
