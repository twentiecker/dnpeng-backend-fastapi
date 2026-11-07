from sqlalchemy.orm import Session
from sqlalchemy import (
    func,
    and_,
    or_,
)
from app.models.pklnprt import Pklnprt
from app.services.timeseries import parse_periode


def create_pklnprt(db: Session, data: Pklnprt):
    db.add(data)
    db.commit()
    db.refresh(data)
    return data


def filter_pklnprt(
    db: Session,
    kode_wilayah: str,
    kode: str | None = None,
    tahun: int | None = None,
    freq: str | None = None,
    period: int | None = None,
):
    query = db.query(Pklnprt)
    if kode:
        query = query.filter(Pklnprt.kode == kode)
    if tahun:
        query = query.filter(Pklnprt.tahun == tahun)
    if freq:
        query = query.filter(Pklnprt.freq == freq)
    if period:
        query = query.filter(Pklnprt.period == period)
    return (
        query.filter(Pklnprt.kode_wilayah == kode_wilayah)
        .order_by(Pklnprt.tahun, Pklnprt.period)
        .all()
    )


def get_pklnprt_by_kode(db: Session, kode_wilayah: str, kode: str):
    return (
        db.query(Pklnprt)
        .filter(Pklnprt.kode_wilayah == kode_wilayah, Pklnprt.kode == kode)
        .order_by(Pklnprt.tahun, Pklnprt.period)
        .all()
    )


def get_pklnprt_by_periode(db: Session, kode_wilayah: str, periode: str):
    tahun, freq, period = parse_periode(periode)
    return (
        db.query(Pklnprt)
        .filter(
            Pklnprt.kode_wilayah == kode_wilayah,
            Pklnprt.tahun == tahun,
            Pklnprt.freq == freq,
            Pklnprt.period == period,
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
    query = db.query(Pklnprt).filter(Pklnprt.kode_wilayah == kode_wilayah, Pklnprt.kode == kode)
    if start:
        tahun, freq, period = parse_periode(start)
        query = query.filter(
            or_(
                Pklnprt.tahun > tahun,
                and_(Pklnprt.tahun == tahun, Pklnprt.period >= period),
            )
        )
        query = query.filter(Pklnprt.freq == freq)
    if end:
        tahun, freq, period = parse_periode(end)
        query = query.filter(
            or_(
                Pklnprt.tahun < tahun,
                and_(Pklnprt.tahun == tahun, Pklnprt.period <= period),
            )
        )
        query = query.filter(Pklnprt.freq == freq)
    return query.order_by(Pklnprt.tahun, Pklnprt.period).all()


def get_indikator_list(db: Session, kode_wilayah: str):
    return (
        db.query(Pklnprt.kode, Pklnprt.deskripsi)
        .filter(Pklnprt.kode_wilayah == kode_wilayah)
        .distinct()
        .order_by(Pklnprt.kode)
        .all()
    )


def get_latest(db: Session, kode_wilayah: str):
    sub = (
        db.query(
            Pklnprt.id,
            func.row_number()
            .over(
                partition_by=(Pklnprt.kode, Pklnprt.freq),
                order_by=(Pklnprt.tahun.desc(), Pklnprt.period.desc()),
            )
            .label("rn"),
        )
        .filter(Pklnprt.kode_wilayah == kode_wilayah)
        .subquery()
    )
    data = (
        db.query(Pklnprt)
        .join(sub, Pklnprt.id == sub.c.id)
        .filter(sub.c.rn == 1)
        .order_by(Pklnprt.kode)
        .all()
    )
    return data
