from pydantic import BaseModel, field_validator
from enum import Enum
import re


class KonversiEnum(str, Enum):
    AVG = "AVG"
    SUM = "SUM"
    LAST = "LAST"


class PmtbCreate(BaseModel):
    kode: str
    deskripsi: str
    satuan: str
    konversi: KonversiEnum
    periode: str
    nilai: float

    @field_validator("kode")
    def validate_kode(cls, v):
        if not re.match(r"^[A-Za-z0-9]+$", v):
            raise ValueError("kode hanya boleh huruf dan angka")
        if len(v) > 10:
            raise ValueError("kode maksimal 10 karakter")
        return v

    @field_validator("deskripsi")
    def validate_deskripsi(cls, v):
        if not v.strip():
            raise ValueError("deskripsi tidak boleh kosong")
        return v

    @field_validator("satuan")
    def validate_satuan(cls, v):
        if not v.strip():
            raise ValueError("satuan tidak boleh kosong")
        if not re.match(r"^[A-Za-z0-9/%\s]+$", v):
            raise ValueError("satuan hanya boleh huruf, angka, spasi, /, %")
        return v

    @field_validator("konversi", mode="before")
    def normalize_konversi(cls, v):
        if isinstance(v, str):
            return v.upper()
        return v

    @field_validator("periode")
    def validate_periode(cls, v):
        if not re.match(r"^\d{4}(Q[1-4]|M([1-9]|1[0-2]))$", v):
            raise ValueError(
                "periode harus format YYYYQ1-4 atau YYYYM1-12 (contoh: 2019Q1 atau 2019M12)"
            )
        return v

    @field_validator("nilai")
    def validate_nilai(cls, v):
        if v is None:
            return v  # ⬅️ boleh kosong
        if not isinstance(v, (int, float)):
            raise ValueError("nilai harus berupa angka")
        return v


class PmtbResponse(BaseModel):
    kode: str
    deskripsi: str
    satuan: str
    konversi: str
    periode: str
    nilai: float

    class Config:
        from_attributes = True
