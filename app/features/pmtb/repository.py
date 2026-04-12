from sqlalchemy.orm import Session
from sqlalchemy import (
    func,
    and_,
    or_,
)
from app.models.pmtb import Pmtb
from app.services.timeseries import parse_periode


def create_pmtb(db: Session, data: Pmtb):
    db.add(data)
    db.commit()
    db.refresh(data)
    return data


def filter_pmtb(
    db: Session,
    kode: str | None = None,
    tahun: int | None = None,
    freq: str | None = None,
    period: int | None = None,
):
    query = db.query(Pmtb)
    if kode:
        query = query.filter(Pmtb.kode == kode)
    if tahun:
        query = query.filter(Pmtb.tahun == tahun)
    if freq:
        query = query.filter(Pmtb.freq == freq)
    if period:
        query = query.filter(Pmtb.period == period)
    return query.order_by(Pmtb.tahun, Pmtb.period).all()


def get_pmtb_by_kode(db: Session, kode: str):
    return (
        db.query(Pmtb).filter(Pmtb.kode == kode).order_by(Pmtb.tahun, Pmtb.period).all()
    )


def get_pmtb_by_periode(db: Session, periode: str):
    tahun, freq, period = parse_periode(periode)
    return (
        db.query(Pmtb)
        .filter(
            Pmtb.tahun == tahun,
            Pmtb.freq == freq,
            Pmtb.period == period,
        )
        .all()
    )


def query_timeseries(
    db: Session,
    kode: str,
    start_year: str | None = None,
    end_year: str | None = None,
):
    query = db.query(Pmtb).filter(Pmtb.kode == kode)
    if start_year:
        tahun, freq, period = parse_periode(start_year)
        query = query.filter(
            or_(
                Pmtb.tahun > tahun,
                and_(Pmtb.tahun == tahun, Pmtb.period >= period),
            )
        )
        query = query.filter(Pmtb.freq == freq)
    if end_year:
        tahun, freq, period = parse_periode(end_year)
        query = query.filter(
            or_(
                Pmtb.tahun < tahun,
                and_(Pmtb.tahun == tahun, Pmtb.period <= period),
            )
        )
        query = query.filter(Pmtb.freq == freq)
    return query.order_by(Pmtb.tahun, Pmtb.period).all()


def get_indikator_list(db: Session):
    return db.query(Pmtb.kode, Pmtb.deskripsi).distinct().order_by(Pmtb.kode).all()


def get_latest(db: Session):
    sub = db.query(
        Pmtb.id,
        func.row_number()
        .over(
            partition_by=(Pmtb.kode, Pmtb.freq),
            order_by=(Pmtb.tahun.desc(), Pmtb.period.desc()),
        )
        .label("rn"),
    ).subquery()
    data = db.query(Pmtb).join(sub, Pmtb.id == sub.c.id).filter(sub.c.rn == 1).all()
    return data
