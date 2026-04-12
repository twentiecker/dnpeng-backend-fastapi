from sqlalchemy.orm import Session
from sqlalchemy import (
    func,
    and_,
    or_,
)
from app.models.pdb import Pdb
from app.services.timeseries import parse_periode


def create_pdb(db: Session, data: Pdb):
    db.add(data)
    db.commit()
    db.refresh(data)
    return data


def filter_pdb(
    db: Session,
    kode: int | None = None,
    jenis: str | None = None,
    tahun: int | None = None,
    freq: str | None = None,
    period: int | None = None,
):
    query = db.query(Pdb)
    if kode:
        query = query.filter(Pdb.kode == kode)
    if jenis:
        query = query.filter(Pdb.jenis == jenis)
    if tahun:
        query = query.filter(Pdb.tahun == tahun)
    if freq:
        query = query.filter(Pdb.freq == freq)
    if period:
        query = query.filter(Pdb.period == period)
    return query.order_by(Pdb.kode, Pdb.tahun, Pdb.period).all()


def get_pdb_by_kode(
    db: Session,
    kode: int,
    jenis: str | None = None,
):
    query = db.query(Pdb)
    if jenis:
        query = query.filter(Pdb.jenis == jenis)
    return (
        query.filter(Pdb.kode == kode).order_by(Pdb.kode, Pdb.tahun, Pdb.period).all()
    )


def get_pdb_by_periode(
    db: Session,
    periode: str,
    jenis: str | None = None,
):
    tahun, freq, period = parse_periode(periode)

    query = db.query(Pdb)
    if jenis:
        query = query.filter(Pdb.jenis == jenis)

    return (
        query.filter(
            Pdb.tahun == tahun,
            Pdb.freq == freq,
            Pdb.period == period,
        )
        .order_by(Pdb.kode)
        .all()
    )


def query_timeseries(
    db: Session,
    kode: int,
    jenis: str | None = None,
    start_year: str | None = None,
    end_year: str | None = None,
):
    query = db.query(Pdb).filter(Pdb.kode == kode)
    if jenis:
        query = query.filter(Pdb.jenis == jenis)
    if start_year:
        tahun, freq, period = parse_periode(start_year)
        query = query.filter(
            or_(
                Pdb.tahun > tahun,
                and_(Pdb.tahun == tahun, Pdb.period >= period),
            )
        )
        query = query.filter(Pdb.freq == freq)
    if end_year:
        tahun, freq, period = parse_periode(end_year)
        query = query.filter(
            or_(
                Pdb.tahun < tahun,
                and_(Pdb.tahun == tahun, Pdb.period <= period),
            )
        )
        query = query.filter(Pdb.freq == freq)
    return query.order_by(Pdb.tahun, Pdb.period).all()


def get_indikator_list(db: Session):
    return db.query(Pdb.kode, Pdb.deskripsi).distinct().order_by(Pdb.kode).all()


def get_latest(db: Session, jenis: str | None = None):
    sub = db.query(
        Pdb.id,
        func.row_number()
        .over(
            partition_by=(Pdb.kode, Pdb.jenis, Pdb.freq),
            order_by=(Pdb.tahun.desc(), Pdb.period.desc()),
        )
        .label("rn"),
    ).subquery()
    query = db.query(Pdb)
    if jenis:
        query = query.filter(Pdb.jenis == jenis)
    data = (
        query.join(sub, Pdb.id == sub.c.id)
        .filter(sub.c.rn == 1)
        .order_by(Pdb.kode)
        .all()
    )
    return data
