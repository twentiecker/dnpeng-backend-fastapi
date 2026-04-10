from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from collections import defaultdict
from app.models.pdb import Pdb
from app.features.pdb import repository as repo
from app.services.timeseries import (
    parse_periode,
    compute_qtoq,
    compute_yony,
    compute_ctoc,
    compute_annual,
)


def add_pdb(
    db: Session, kode: int, deskripsi: str, jenis: str, periode: str, nilai: float
):
    try:
        tahun, freq, period = parse_periode(periode)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    data = Pdb(
        kode=kode,
        deskripsi=deskripsi,
        jenis=jenis,
        tahun=tahun,
        freq=freq,
        period=period,
        nilai=nilai,
    )
    return repo.create_pdb(db, data)


def get_pdb_data(db: Session, kode: int | None, jenis: str | None, periode: str | None):
    tahun = None
    freq = None
    period = None
    if periode:
        tahun, freq, period = parse_periode(periode)
    return repo.filter_pdb(db, kode, jenis, tahun, freq, period)


def get_pdb_kode(db: Session, kode: int, jenis: str | None):
    return repo.get_pdb_by_kode(db, kode, jenis)


def get_pdb_periode(db: Session, periode: str, jenis: str | None):
    return repo.get_pdb_by_periode(db, periode, jenis)


def get_timeseries(
    db: Session, kode: int, jenis: str | None, start: int | None, end: int | None
):
    data = repo.query_timeseries(db, kode, jenis, start, end)
    return {
        "kode": kode,
        "jenis": jenis,
        "data": [
            {"jenis": d.jenis, "periode": d.periode, "nilai": d.nilai} for d in data
        ],
    }


def get_indikator_list(db: Session):
    data = repo.get_indikator_list(db)
    return [{"kode": d.kode, "deskripsi": d.deskripsi} for d in data]


def get_latest(db: Session, jenis: str | None):
    return repo.get_latest(db, jenis)


def get_growth_rate(db: Session, kode: int, jenis: str, type: str):
    data = repo.query_timeseries(db, kode, jenis)
    if not data:
        return {"kode": kode, "type": type, "data": []}
    if type == "qtoq":
        result = compute_qtoq(data)
    elif type == "yony":
        result = compute_yony(data)
    elif type == "ctoc":
        result = compute_ctoc(data)
    elif type == "annual":
        result = compute_annual(data)
    else:
        result = []
    return {"kode": kode, "jenis": jenis, "type": type, "data": result}


def get_annual_data(db: Session, kode: int, jenis: str):
    data = repo.query_timeseries(db, kode, jenis)
    annual = defaultdict(list)
    for d in data:
        year = d.periode[:4]
        annual[year].append(d.nilai)
    result = []
    for year, values in annual.items():
        result.append({"tahun": year, "nilai": sum(values)})
    return {"kode": kode, "jenis": jenis, "data": result}


def get_chart_data(db: Session, kode: int, jenis: str):
    data = repo.query_timeseries(db, kode, jenis)
    periode = []
    values = []
    for d in data:
        periode.append(d.periode)
        values.append(d.nilai)
    return {
        "kode": kode,
        "jenis": jenis,
        "xAxis": periode,
        "series": [{"name": kode, "data": values}],
    }


def get_growth_chart(db: Session, kode: int, jenis: str, type: str):
    result = get_growth_rate(db, kode, jenis, type)
    periode = []
    nilai = []
    growth = []
    for row in result["data"]:
        periode.append(row["periode"])
        nilai.append(row["nilai"])
        growth.append(row["growth"])
    return {
        "kode": kode,
        "jenis": jenis,
        "type": type,
        "xAxis": periode,
        "series": [
            {
                "name": "nilai",
                "data": nilai,
            },
            {
                "name": f"{type}_growth",
                "data": growth,
            },
        ],
    }


def get_annual_chart(db: Session, kode: int, jenis: str):
    result = get_annual_data(db, kode, jenis)
    tahun = []
    nilai = []
    for row in result["data"]:
        tahun.append(row["tahun"])
        nilai.append(row["nilai"])
    return {
        "kode": kode,
        "jenis": jenis,
        "xAxis": tahun,
        "series": [
            {
                "name": "annual",
                "data": nilai,
            }
        ],
    }
