from fastapi import (
    APIRouter,
    Depends,
    Query,
    UploadFile,
    File,
    Form,
)
from sqlalchemy.orm import Session
from typing import Optional, List

from app.api.deps import get_db

from app.features.monitoring.schema import (
    MonitoringCreate,
    MonitoringUpsert,
    MonitoringResponse,
)

from app.features.monitoring import service


router = APIRouter()


# =====================================
# UPLOAD EXCEL
# =====================================
@router.post("/upload")
def upload_excel(
    file: UploadFile = File(...),
    uploaded_by: str = Form(...),
    db: Session = Depends(get_db),
):
    return service.upload_monitoring_excel(db=db, file=file, uploaded_by=uploaded_by)


# =====================================
# GET ALL
# =====================================
@router.get("/", response_model=List[MonitoringResponse])
def get_all(db: Session = Depends(get_db)):
    return service.get_all_monitoring(db)


# =====================================
# FILTER
# =====================================
@router.get("/filter", response_model=List[MonitoringResponse])
def get_filter(
    tahun: Optional[int] = Query(None),
    bulan: Optional[int] = Query(None),
    freq: Optional[str] = Query(None),
    komponen: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return service.get_monitoring_by_filter(
        db=db, tahun=tahun, bulan=bulan, freq=freq, komponen=komponen
    )


# =====================================
# CREATE
# =====================================
@router.post("/", response_model=MonitoringResponse)
def create(payload: MonitoringCreate, db: Session = Depends(get_db)):
    return service.create_monitoring(db=db, payload=payload)


# =====================================
# UPSERT SINGLE
# =====================================
@router.post("/upsert")
def upsert(payload: MonitoringUpsert, db: Session = Depends(get_db)):
    return service.upsert_monitoring(db=db, payload=payload)


# =====================================
# DELETE BY YEAR
# =====================================
@router.delete("/year/{tahun}")
def delete_by_year(tahun: int, db: Session = Depends(get_db)):
    return service.delete_monitoring_by_year(db=db, tahun=tahun)


# =====================================
# PROGRESS
# =====================================
@router.get("/progress")
def progress(group_by: str, triwulan: int = None, db: Session = Depends(get_db)):
    cols = group_by.split(",")
    data = service.get_progress_service(db, cols, triwulan)
    return data


# =====================================
# CHART PROGRESS
# =====================================
@router.get("/chart")
def chart(group_by: str, triwulan: int = None, db: Session = Depends(get_db)):
    cols = group_by.split(",")
    data = service.get_chart_service(db, cols, triwulan)
    return data


# =====================================
# SUMMARY
# =====================================
@router.get("/summary/{tahun}")
def summary(tahun: int, db: Session = Depends(get_db)):
    return service.get_summary_monthly(db=db, tahun=tahun)
