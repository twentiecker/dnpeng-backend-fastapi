from sqlalchemy.orm import Session
from app.models.master_wilayah import MasterWilayah


def get_master_wilayah(
    db: Session,
    level: str | None = None,
    parent_kode: str | None = None,
    search: str | None = None,
):
    query = db.query(MasterWilayah)

    if level:
        query = query.filter(MasterWilayah.level == level)

    if parent_kode is not None:
        query = query.filter(MasterWilayah.parent_kode == parent_kode)

    if search:
        query = query.filter(MasterWilayah.nama_wilayah.ilike(f"%{search}%"))

    return query.order_by(MasterWilayah.kode_wilayah).all()
