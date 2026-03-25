from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.pkrt import Pkrt
from app.features.pkrt.utils import parse_periode


def create_pkrt(db: Session, data: Pkrt):
    db.add(data)
    db.commit()
    db.refresh(data)
    return data


def filter_pkrt(
    db: Session,
    kode: str | None = None,
    tahun: int | None = None,
    freq: str | None = None,
    period: int | None = None,
):
    query = db.query(Pkrt)
    if kode:
        query = query.filter(Pkrt.kode == kode)
    if tahun:
        query = query.filter(Pkrt.tahun == tahun)
    if freq:
        query = query.filter(Pkrt.freq == freq)
    if period:
        query = query.filter(Pkrt.period == period)
    return query.order_by(Pkrt.tahun, Pkrt.period).all()


def get_pkrt_by_kode(db: Session, kode: str):
    return (
        db.query(Pkrt).filter(Pkrt.kode == kode).order_by(Pkrt.tahun, Pkrt.period).all()
    )


def get_pkrt_by_periode(db: Session, periode: str):
    tahun, freq, period = parse_periode(periode)
    return (
        db.query(Pkrt)
        .filter(
            Pkrt.tahun == tahun,
            Pkrt.freq == freq,
            Pkrt.period == period,
        )
        .all()
    )


def query_timeseries(
    db: Session,
    kode: str,
    start_year: int | None,
    end_year: int | None,
):
    query = db.query(Pkrt).filter(Pkrt.kode == kode)
    if start_year:
        tahun, freq, period = parse_periode(start_year)
        query = query.filter(
            Pkrt.tahun >= tahun,
            Pkrt.freq == freq,
            Pkrt.period >= period,
        )
    if end_year:
        tahun, freq, period = parse_periode(end_year)
        query = query.filter(
            Pkrt.tahun <= tahun,
            Pkrt.freq == freq,
            Pkrt.period <= period,
        )
    return query.order_by(Pkrt.tahun, Pkrt.period).all()


def get_indikator_list(db: Session):
    return db.query(Pkrt.kode, Pkrt.deskripsi).distinct().all()


def get_latest(db: Session):
    sub = db.query(
        Pkrt.id,
        func.row_number()
        .over(
            partition_by=(Pkrt.kode, Pkrt.freq),
            order_by=(Pkrt.tahun.desc(), Pkrt.period.desc()),
        )
        .label("rn"),
    ).subquery()
    data = db.query(Pkrt).join(sub, Pkrt.id == sub.c.id).filter(sub.c.rn == 1).all()
    return data
