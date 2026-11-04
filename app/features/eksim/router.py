from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session
from typing import Optional
from app.api.deps import get_db
from app.features.eksim.schema import (
    EksimCreate,
    EksimResponse,
    EksimAggregatorResponse,
)
from app.features.eksim import service

router = APIRouter()


@router.post("/data", response_model=EksimResponse)
def create_eksim(data: EksimCreate, db: Session = Depends(get_db)):
    return service.add_eksim(
        db,
        data.kode_wilayah,
        data.kode,
        data.deskripsi,
        data.satuan,
        data.konversi,
        data.periode,
        data.nilai,
    )


@router.get("/data", response_model=list[EksimResponse])
def eksim_data(
    kode_wilayah: str,
    kode: Optional[str] = Query(None),
    periode: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return service.get_eksim_data(db, kode_wilayah, kode, periode)


@router.get("/kode", response_model=list[EksimResponse])
def eksim_kode(kode_wilayah: str, kode: str, db: Session = Depends(get_db)):
    return service.get_eksim_kode(db, kode_wilayah, kode)


@router.get("/periode", response_model=list[EksimResponse])
def eksim_periode(kode_wilayah: str, periode: str, db: Session = Depends(get_db)):
    return service.get_eksim_periode(db, kode_wilayah, periode)


@router.get("/timeseries")
def eksim_timeseries(
    kode_wilayah: str,
    kode: str = Query(...),
    start: Optional[str] = None,
    end: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return service.get_timeseries(db, kode_wilayah, kode, start, end)


@router.get("/indikator")
def indikator_list(kode_wilayah: str, db: Session = Depends(get_db)):
    return service.get_indikator_list(db, kode_wilayah)


@router.get("/latest", response_model=list[EksimResponse])
def eksim_latest(kode_wilayah: str, db: Session = Depends(get_db)):
    return service.get_latest(db, kode_wilayah)


@router.get("/growth")
def eksim_growth(
    kode_wilayah: str, kode: str, type: str, db: Session = Depends(get_db)
):
    return service.get_growth_rate(db, kode_wilayah, kode, type)


@router.get("/quarter")
def eksim_quarter(kode_wilayah: str, kode: str, db: Session = Depends(get_db)):
    return service.get_quarter_data(db, kode_wilayah, kode)


@router.get("/annual")
def eksim_annual(kode_wilayah: str, kode: str, db: Session = Depends(get_db)):
    return service.get_annual_data(db, kode_wilayah, kode)


@router.get("/chart")
def eksim_chart(kode_wilayah: str, kode: str, db: Session = Depends(get_db)):
    return service.get_chart_data(db, kode_wilayah, kode)


@router.get("/growth/chart")
def eksim_growth_chart(
    kode_wilayah: str,
    kode: str,
    type: str = "qtoq",
    db: Session = Depends(get_db),
):
    return service.get_growth_chart(db, kode_wilayah, kode, type)


@router.get("/quarter/chart")
def eksim_quarter_chart(
    kode_wilayah: str,
    kode: str,
    db: Session = Depends(get_db),
):
    return service.get_quarter_chart(db, kode_wilayah, kode)


@router.get("/annual/chart")
def eksim_annual_chart(
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
    response_model=EksimAggregatorResponse,
)
def get_aggregated_data(
    kode_wilayah: str,
    db: Session = Depends(get_db),
):
    return service.get_aggregated_data(
        db,
        kode_wilayah,
    )
