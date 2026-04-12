from sqlalchemy.orm import Session
from sqlalchemy import (
    func,
    and_,
    or_,
)
from app.models.eksim import Eksim
from app.services.timeseries import parse_periode


def create_eksim(db: Session, data: Eksim):
    db.add(data)
    db.commit()
    db.refresh(data)
    return data


def filter_eksim(
    db: Session,
    kode: str | None = None,
    tahun: int | None = None,
    freq: str | None = None,
    period: int | None = None,
):
    query = db.query(Eksim)
    if kode:
        query = query.filter(Eksim.kode == kode)
    if tahun:
        query = query.filter(Eksim.tahun == tahun)
    if freq:
        query = query.filter(Eksim.freq == freq)
    if period:
        query = query.filter(Eksim.period == period)
    return query.order_by(Eksim.tahun, Eksim.period).all()


def get_eksim_by_kode(db: Session, kode: str):
    return (
        db.query(Eksim)
        .filter(Eksim.kode == kode)
        .order_by(Eksim.tahun, Eksim.period)
        .all()
    )


def get_eksim_by_periode(db: Session, periode: str):
    tahun, freq, period = parse_periode(periode)
    return (
        db.query(Eksim)
        .filter(
            Eksim.tahun == tahun,
            Eksim.freq == freq,
            Eksim.period == period,
        )
        .all()
    )


def query_timeseries(
    db: Session,
    kode: str,
    start_year: str | None = None,
    end_year: str | None = None,
):
    query = db.query(Eksim).filter(Eksim.kode == kode)
    if start_year:
        tahun, freq, period = parse_periode(start_year)
        query = query.filter(
            or_(
                Eksim.tahun > tahun,
                and_(Eksim.tahun == tahun, Eksim.period >= period),
            )
        )
        query = query.filter(Eksim.freq == freq)
    if end_year:
        tahun, freq, period = parse_periode(end_year)
        query = query.filter(
            or_(
                Eksim.tahun < tahun,
                and_(Eksim.tahun == tahun, Eksim.period <= period),
            )
        )
        query = query.filter(Eksim.freq == freq)
    return query.order_by(Eksim.tahun, Eksim.period).all()


def get_indikator_list(db: Session):
    return db.query(Eksim.kode, Eksim.deskripsi).distinct().order_by(Eksim.kode).all()


def get_latest(db: Session):
    sub = db.query(
        Eksim.id,
        func.row_number()
        .over(
            partition_by=(Eksim.kode, Eksim.freq),
            order_by=(Eksim.tahun.desc(), Eksim.period.desc()),
        )
        .label("rn"),
    ).subquery()
    data = db.query(Eksim).join(sub, Eksim.id == sub.c.id).filter(sub.c.rn == 1).all()
    return data
