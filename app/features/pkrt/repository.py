from sqlalchemy.orm import Session
from sqlalchemy import (
    func,
    and_,
    or_,
)
from app.models.pkrt import Pkrt
from app.services.timeseries import parse_periode


def create_pkrt(db: Session, data: Pkrt):
    db.add(data)
    db.commit()
    db.refresh(data)
    return data


def filter_pkrt(
    db: Session,
    kode_wilayah: str,
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
    return (
        query.filter(Pkrt.kode_wilayah == kode_wilayah)
        .order_by(Pkrt.tahun, Pkrt.period)
        .all()
    )


def get_pkrt_by_kode(db: Session, kode_wilayah: str, kode: str):
    return (
        db.query(Pkrt)
        .filter(Pkrt.kode_wilayah == kode_wilayah, Pkrt.kode == kode)
        .order_by(Pkrt.tahun, Pkrt.period)
        .all()
    )


def get_pkrt_by_periode(db: Session, kode_wilayah: str, periode: str):
    tahun, freq, period = parse_periode(periode)
    return (
        db.query(Pkrt)
        .filter(
            Pkrt.kode_wilayah == kode_wilayah,
            Pkrt.tahun == tahun,
            Pkrt.freq == freq,
            Pkrt.period == period,
        )
        .all()
    )


def query_timeseries(
    db: Session,
    kode_wilayah: str,
    kode: str,
    start: str | None = None,
    end: str | None = None,
):
    query = db.query(Pkrt).filter(Pkrt.kode_wilayah == kode_wilayah, Pkrt.kode == kode)
    if start:
        tahun, freq, period = parse_periode(start)
        query = query.filter(
            or_(
                Pkrt.tahun > tahun,
                and_(Pkrt.tahun == tahun, Pkrt.period >= period),
            )
        )
        query = query.filter(Pkrt.freq == freq)
    if end:
        tahun, freq, period = parse_periode(end)
        query = query.filter(
            or_(
                Pkrt.tahun < tahun,
                and_(Pkrt.tahun == tahun, Pkrt.period <= period),
            )
        )
        query = query.filter(Pkrt.freq == freq)
    return query.order_by(Pkrt.tahun, Pkrt.period).all()


def get_indikator_list(db: Session, kode_wilayah: str):
    return (
        db.query(Pkrt.kode, Pkrt.deskripsi)
        .filter(Pkrt.kode_wilayah == kode_wilayah)
        .distinct()
        .order_by(Pkrt.kode)
        .all()
    )


def get_latest(db: Session, kode_wilayah: str):
    sub = (
        db.query(
            Pkrt.id,
            func.row_number()
            .over(
                partition_by=(Pkrt.kode, Pkrt.freq),
                order_by=(Pkrt.tahun.desc(), Pkrt.period.desc()),
            )
            .label("rn"),
        )
        .filter(Pkrt.kode_wilayah == kode_wilayah)
        .subquery()
    )
    data = (
        db.query(Pkrt)
        .join(sub, Pkrt.id == sub.c.id)
        .filter(sub.c.rn == 1)
        .order_by(Pkrt.kode)
        .all()
    )
    return data
