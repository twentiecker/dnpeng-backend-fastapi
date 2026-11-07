from sqlalchemy.orm import Session
from sqlalchemy import (
    func,
    and_,
    or_,
)
from app.models.inventori import Inventori
from app.services.timeseries import parse_periode


def create_inventori(db: Session, data: Inventori):
    db.add(data)
    db.commit()
    db.refresh(data)
    return data


def filter_inventori(
    db: Session,
    kode_wilayah: str,
    kode: str | None = None,
    tahun: int | None = None,
    freq: str | None = None,
    period: int | None = None,
):
    query = db.query(Inventori)
    if kode:
        query = query.filter(Inventori.kode == kode)
    if tahun:
        query = query.filter(Inventori.tahun == tahun)
    if freq:
        query = query.filter(Inventori.freq == freq)
    if period:
        query = query.filter(Inventori.period == period)
    return (
        query.filter(Inventori.kode_wilayah == kode_wilayah)
        .order_by(Inventori.tahun, Inventori.period)
        .all()
    )


def get_inventori_by_kode(db: Session, kode_wilayah: str, kode: str):
    return (
        db.query(Inventori)
        .filter(Inventori.kode_wilayah == kode_wilayah, Inventori.kode == kode)
        .order_by(Inventori.tahun, Inventori.period)
        .all()
    )


def get_inventori_by_periode(db: Session, kode_wilayah: str, periode: str):
    tahun, freq, period = parse_periode(periode)
    return (
        db.query(Inventori)
        .filter(
            Inventori.kode_wilayah == kode_wilayah,
            Inventori.tahun == tahun,
            Inventori.freq == freq,
            Inventori.period == period,
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
    query = db.query(Inventori).filter(Inventori.kode_wilayah == kode_wilayah, Inventori.kode == kode)
    if start:
        tahun, freq, period = parse_periode(start)
        query = query.filter(
            or_(
                Inventori.tahun > tahun,
                and_(Inventori.tahun == tahun, Inventori.period >= period),
            )
        )
        query = query.filter(Inventori.freq == freq)
    if end:
        tahun, freq, period = parse_periode(end)
        query = query.filter(
            or_(
                Inventori.tahun < tahun,
                and_(Inventori.tahun == tahun, Inventori.period <= period),
            )
        )
        query = query.filter(Inventori.freq == freq)
    return query.order_by(Inventori.tahun, Inventori.period).all()


def get_indikator_list(db: Session, kode_wilayah: str):
    return (
        db.query(Inventori.kode, Inventori.deskripsi)
        .filter(Inventori.kode_wilayah == kode_wilayah)
        .distinct()
        .order_by(Inventori.kode)
        .all()
    )


def get_latest(db: Session, kode_wilayah: str):
    sub = (
        db.query(
            Inventori.id,
            func.row_number()
            .over(
                partition_by=(Inventori.kode, Inventori.freq),
                order_by=(Inventori.tahun.desc(), Inventori.period.desc()),
            )
            .label("rn"),
        )
        .filter(Inventori.kode_wilayah == kode_wilayah)
        .subquery()
    )
    data = (
        db.query(Inventori)
        .join(sub, Inventori.id == sub.c.id)
        .filter(sub.c.rn == 1)
        .order_by(Inventori.kode)
        .all()
    )
    return data
