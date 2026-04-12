from sqlalchemy.orm import Session
from sqlalchemy import (
    func,
    and_,
    or_,
)
from app.models.pkp import Pkp
from app.services.timeseries import parse_periode


def create_pkp(db: Session, data: Pkp):
    db.add(data)
    db.commit()
    db.refresh(data)
    return data


def filter_pkp(
    db: Session,
    kode: str | None = None,
    tahun: int | None = None,
    freq: str | None = None,
    period: int | None = None,
):
    query = db.query(Pkp)
    if kode:
        query = query.filter(Pkp.kode == kode)
    if tahun:
        query = query.filter(Pkp.tahun == tahun)
    if freq:
        query = query.filter(Pkp.freq == freq)
    if period:
        query = query.filter(Pkp.period == period)
    return query.order_by(Pkp.tahun, Pkp.period).all()


def get_pkp_by_kode(db: Session, kode: str):
    return db.query(Pkp).filter(Pkp.kode == kode).order_by(Pkp.tahun, Pkp.period).all()


def get_pkp_by_periode(db: Session, periode: str):
    tahun, freq, period = parse_periode(periode)
    return (
        db.query(Pkp)
        .filter(
            Pkp.tahun == tahun,
            Pkp.freq == freq,
            Pkp.period == period,
        )
        .all()
    )


def query_timeseries(
    db: Session,
    kode: str,
    start_year: str | None = None,
    end_year: str | None = None,
):
    query = db.query(Pkp).filter(Pkp.kode == kode)
    if start_year:
        tahun, freq, period = parse_periode(start_year)
        query = query.filter(
            or_(
                Pkp.tahun > tahun,
                and_(Pkp.tahun == tahun, Pkp.period >= period),
            )
        )
        query = query.filter(Pkp.freq == freq)
    if end_year:
        tahun, freq, period = parse_periode(end_year)
        query = query.filter(
            or_(
                Pkp.tahun < tahun,
                and_(Pkp.tahun == tahun, Pkp.period <= period),
            )
        )
        query = query.filter(Pkp.freq == freq)
    return query.order_by(Pkp.tahun, Pkp.period).all()


def get_indikator_list(db: Session):
    return db.query(Pkp.kode, Pkp.deskripsi).distinct().order_by(Pkp.kode).all()


def get_latest(db: Session):
    sub = db.query(
        Pkp.id,
        func.row_number()
        .over(
            partition_by=(Pkp.kode, Pkp.freq),
            order_by=(Pkp.tahun.desc(), Pkp.period.desc()),
        )
        .label("rn"),
    ).subquery()
    data = db.query(Pkp).join(sub, Pkp.id == sub.c.id).filter(sub.c.rn == 1).all()
    return data
