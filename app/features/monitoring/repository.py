from sqlalchemy import func, text
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.models.monitoring import Monitoring
from app.features.monitoring.utils import build_monitoring_progress_query


def get_all(db: Session):
    return db.query(Monitoring).all()


def get_by_filter(
    db: Session,
    tahun: int = None,
    bulan: int = None,
    freq: str = None,
    komponen: str = None,
):
    query = db.query(Monitoring)

    if tahun:
        query = query.filter(Monitoring.tahun == tahun)

    if bulan:
        query = query.filter(Monitoring.bulan == bulan)

    if freq:
        query = query.filter(Monitoring.freq == freq)

    if komponen:
        query = query.filter(Monitoring.komponen == komponen)

    return query.all()


def create(db: Session, payload: dict):

    obj = Monitoring(**payload)

    db.add(obj)
    db.commit()
    db.refresh(obj)

    return obj


def upsert(db: Session, payload: dict):

    existing = (
        db.query(Monitoring)
        .filter(
            Monitoring.komponen == payload["komponen"],
            Monitoring.no == payload["no"],
            Monitoring.tahun == payload["tahun"],
            Monitoring.bulan == payload["bulan"],
        )
        .first()
    )

    action = "updated" if existing else "inserted"

    stmt = insert(Monitoring).values(**payload)

    stmt = stmt.on_conflict_do_update(
        constraint="uq_monitoring_periode",
        set_={
            "nama_data": stmt.excluded.nama_data,
            "internal_external": stmt.excluded.internal_external,
            "pjk_neraca": stmt.excluded.pjk_neraca,
            "penanggung_jawab": stmt.excluded.penanggung_jawab,
            "jumlah_data": stmt.excluded.jumlah_data,
            "jumlah_datum": stmt.excluded.jumlah_datum,
            "nilai": stmt.excluded.nilai,
            "freq": stmt.excluded.freq,
            "keterangan": stmt.excluded.keterangan,
            "source_file": stmt.excluded.source_file,
            "uploaded_by": stmt.excluded.uploaded_by,
        },
    )

    db.execute(stmt)
    db.commit()

    return action


def bulk_upsert(db: Session, rows: list[dict]):

    if not rows:
        return

    stmt = insert(Monitoring).values(rows)

    stmt = stmt.on_conflict_do_update(
        constraint="uq_monitoring_periode",
        set_={
            "nama_data": stmt.excluded.nama_data,
            "internal_external": stmt.excluded.internal_external,
            "pjk_neraca": stmt.excluded.pjk_neraca,
            "penanggung_jawab": stmt.excluded.penanggung_jawab,
            "jumlah_data": stmt.excluded.jumlah_data,
            "jumlah_datum": stmt.excluded.jumlah_datum,
            "nilai": stmt.excluded.nilai,
            "freq": stmt.excluded.freq,
            "keterangan": stmt.excluded.keterangan,
            "source_file": stmt.excluded.source_file,
            "uploaded_by": stmt.excluded.uploaded_by,
        },
    )

    db.execute(stmt)
    db.commit()


def delete_by_year(db: Session, tahun: int):

    deleted_rows = (
        db.query(Monitoring)
        .filter(Monitoring.tahun == tahun)
        .delete(synchronize_session=False)
    )

    db.commit()

    return deleted_rows


def get_monitoring_progress(db, group_by, triwulan):
    sql = build_monitoring_progress_query(group_by, triwulan)
    result = db.execute(text(sql))
    return result.mappings().all()


def get_monitoring_chart(db, group_by, triwulan):
    return get_monitoring_progress(db, group_by, triwulan)
