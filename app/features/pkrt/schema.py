from pydantic import BaseModel, field_validator
import re


class PkrtCreate(BaseModel):
    kode: str
    deskripsi: str
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

    @field_validator("periode")
    def validate_periode(cls, v):
        # Format: YYYYQ1-4 atau YYYYM1-12
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


class PkrtResponse(BaseModel):
    kode: str
    deskripsi: str
    periode: str
    nilai: float

    class Config:
        from_attributes = True
