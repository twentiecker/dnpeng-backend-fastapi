from pydantic import BaseModel


class PkrtCreate(BaseModel):
    kode: str
    deskripsi: str
    periode: str
    nilai: float


class PkrtResponse(BaseModel):
    kode: str
    deskripsi: str
    periode: str
    nilai: float

    class Config:
        from_attributes = True
