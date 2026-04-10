from pydantic import BaseModel, field_validator
import re


class PdbCreate(BaseModel):
    kode: int
    deskripsi: str
    periode: str
    nilai: float
    jenis: str

    @field_validator("kode")
    def validate_kode(cls, v):
        if v is None:
            raise ValueError("kode tidak boleh kosong")
        if v <= 0:
            raise ValueError("kode harus lebih dari 0")
        return v

    @field_validator("deskripsi")
    def validate_deskripsi(cls, v):
        if not v.strip():
            raise ValueError("deskripsi tidak boleh kosong")
        return v

    @field_validator("jenis")
    def validate_jenis(cls, v):
        if not v.strip():
            raise ValueError("jenis tidak boleh kosong")
        if v not in {"ADHB", "ADHK"}:
            raise ValueError("jenis data hanya boleh ADHB atau ADHK")
        return v

    @field_validator("periode")
    def validate_periode(cls, v):
        if not re.match(r"^\d{4}Q[1-4]$", v):
            raise ValueError("periode harus format YYYYQ1-4 (contoh: 2020Q1)")
        return v

    @field_validator("nilai")
    def validate_nilai(cls, v):
        if v is None:
            raise ValueError("nilai tidak boleh kosong")
        if not isinstance(v, (int, float)):
            raise ValueError("nilai harus berupa angka")
        return v


class PdbResponse(BaseModel):
    kode: int
    deskripsi: str
    periode: str
    nilai: float
    jenis: str

    class Config:
        from_attributes = True
