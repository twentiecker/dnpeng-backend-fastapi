from pydantic import BaseModel, Field
from typing import Optional


# =====================================
# BASE
# =====================================
class MonitoringBase(BaseModel):
    komponen: str = Field(..., example="PKRT")
    no: int = Field(..., example=1)

    nama_data: str = Field(..., example="Nilai Impor")

    internal_external: Optional[str] = Field(None, example="Eksternal")

    pjk_neraca: Optional[str] = Field(None, example="PJK")

    penanggung_jawab: Optional[str] = Field(
        None, example="Direktorat Statistik Distribusi"
    )

    jumlah_data: int = Field(..., example=13)
    jumlah_datum: int = Field(..., example=23)

    tahun: int = Field(..., example=2026)
    bulan: Optional[int] = Field(None, example=1)

    nilai: Optional[float] = Field(None, example=21)

    freq: str = Field(..., example="MONTHLY")

    keterangan: Optional[str] = Field(None, example="Angka sementara")

    source_file: Optional[str] = None
    uploaded_by: Optional[str] = None


# =====================================
# CREATE
# =====================================
class MonitoringCreate(MonitoringBase):
    pass


# =====================================
# UPDATE / UPSERT
# =====================================
class MonitoringUpsert(MonitoringBase):
    pass


# =====================================
# RESPONSE
# =====================================
class MonitoringResponse(MonitoringBase):
    id: int

    class Config:
        from_attributes = True
