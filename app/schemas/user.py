from pydantic import BaseModel, EmailStr
from enum import Enum


class UserRole(str, Enum):
    pkrt = "pkrt"
    pklnprt = "pklnprt"
    pkp = "pkp"
    pmtb = "pmtb"
    pi = "pi"
    xm = "xm"
    konsolidator = "konsolidator"
    direktur = "direktur"
    dnpeng = "dnpeng"
    lapres = "lapres"


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole  # 🔥 wajib & tervalidasi otomatis


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str

    class Config:
        from_attributes = True
