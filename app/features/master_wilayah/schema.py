from pydantic import BaseModel


class MasterWilayahResponse(BaseModel):
    kode_wilayah: str
    nama_wilayah: str
    level: str
    parent_kode: str | None

    class Config:
        from_attributes = True


class MiniWilayahResponse(BaseModel):
    kode_wilayah: str
    nama_wilayah: str

    class Config:
        from_attributes = True
