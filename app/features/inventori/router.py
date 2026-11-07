from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session
from typing import Optional
from app.api.deps import get_db
from app.features.inventori.schema import (
    InventoriCreate,
    InventoriResponse,
    InventoriAggregatorResponse,
)
from app.features.inventori import service

router = APIRouter()


@router.post("/data", response_model=InventoriResponse)
def create_inventori(data: InventoriCreate, db: Session = Depends(get_db)):
    return service.add_inventori(
        db,
        data.kode_wilayah,
        data.kode,
        data.deskripsi,
        data.satuan,
        data.konversi,
        data.periode,
        data.nilai,
    )


@router.get("/data", response_model=list[InventoriResponse])
def inventori_data(
    kode_wilayah: Optional[str] = Query(None),
    kode: Optional[str] = Query(None),
    periode: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return service.get_inventori_data(db, kode_wilayah, kode, periode)


@router.get("/kode", response_model=list[InventoriResponse])
def inventori_kode(kode_wilayah: str, kode: str, db: Session = Depends(get_db)):
    return service.get_inventori_kode(db, kode_wilayah, kode)


@router.get("/periode", response_model=list[InventoriResponse])
def inventori_periode(kode_wilayah: str, periode: str, db: Session = Depends(get_db)):
    return service.get_inventori_periode(db, kode_wilayah, periode)


@router.get("/timeseries")
def inventori_timeseries(
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


@router.get("/latest", response_model=list[InventoriResponse])
def inventori_latest(kode_wilayah: str, db: Session = Depends(get_db)):
    return service.get_latest(db, kode_wilayah)


@router.get("/growth")
def inventori_growth(kode_wilayah: str, kode: str, type: str, db: Session = Depends(get_db)):
    return service.get_growth_rate(db, kode_wilayah, kode, type)

@router.get("/quarter")
def inventori_quarter(kode_wilayah: str, kode: str, db: Session = Depends(get_db)):
    return service.get_quarter_data(db, kode_wilayah, kode)


@router.get("/annual")
def inventori_annual(kode_wilayah: str, kode: str, db: Session = Depends(get_db)):
    return service.get_annual_data(db, kode_wilayah, kode)


@router.get("/chart")
def inventori_chart(kode_wilayah: str, kode: str, db: Session = Depends(get_db)):
    return service.get_chart_data(db, kode_wilayah, kode)


@router.get("/growth/chart")
def inventori_growth_chart(
    kode_wilayah: str,
    kode: str,
    type: str = "qtoq",
    db: Session = Depends(get_db),
):
    return service.get_growth_chart(db, kode_wilayah, kode, type)


@router.get("/quarter/chart")
def inventori_quarter_chart(
    kode_wilayah: str,
    kode: str,
    db: Session = Depends(get_db),
):
    return service.get_quarter_chart(db, kode_wilayah, kode)


@router.get("/annual/chart")
def inventori_annual_chart(
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
    response_model=InventoriAggregatorResponse,
)
def get_aggregated_data(
    kode_wilayah: str,
    db: Session = Depends(get_db),
):
    return service.get_aggregated_data(
        db,
        kode_wilayah,
    )
