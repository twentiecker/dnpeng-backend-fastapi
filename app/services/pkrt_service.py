from sqlalchemy.orm import Session
from collections import defaultdict
from app.models.pkrt import Pkrt
from app.repositories import pkrt_repository as repo
from app.utils.helper import (
    parse_periode,
    compute_qtoq,
    compute_yony,
    compute_ctoc,
    compute_annual,
)


def add_pkrt(db: Session, kode: str, deskripsi: str, periode: str, nilai: float):

    tahun, freq, period = parse_periode(periode)

    data = Pkrt(
        kode=kode,
        deskripsi=deskripsi,
        tahun=tahun,
        freq=freq,
        period=period,
        nilai=nilai,
    )

    return repo.create_pkrt(db, data)


def get_pkrt_data(db: Session, kode: str | None, periode: str | None):
    return repo.filter_pkrt(db, kode, periode)


def get_pkrt_kode(db: Session, kode: str):
    return repo.get_pkrt_by_kode(db, kode)


def get_pkrt_periode(db: Session, periode: str):
    return repo.get_pkrt_by_periode(db, periode)


def get_timeseries(db: Session, kode: str, start: int | None, end: int | None):

    data = repo.query_timeseries(db, kode, start, end)

    return {
        "kode": kode,
        "data": [{"periode": d.periode, "nilai": d.nilai} for d in data],
    }


def get_indikator_list(db: Session):
    data = repo.get_indikator_list(db)
    return [{"kode": d.kode, "deskripsi": d.deskripsi} for d in data]


def get_latest(db: Session):
    return repo.get_latest(db)


def get_growth_rate(db: Session, kode: str, type: str):
    data = repo.query_timeseries(db, kode, None, None)
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
    return {"kode": kode, "type": type, "data": result}


def get_annual_data(db: Session, kode: str):
    data = repo.query_timeseries(db, kode, None, None)
    annual = defaultdict(list)
    for d in data:
        year = d.periode[:4]
        annual[year].append(d.nilai)
    result = []
    for year, values in annual.items():
        result.append({"tahun": year, "nilai": sum(values)})
    return {"kode": kode, "data": result}


def get_chart_data(db: Session, kode: str):
    data = repo.query_timeseries(db, kode, None, None)
    periode = []
    values = []
    for d in data:
        periode.append(d.periode)
        values.append(d.nilai)
    return {"kode": kode, "xAxis": periode, "series": [{"name": kode, "data": values}]}


def get_growth_chart(db: Session, kode: str, type: str):
    result = get_growth_rate(db, kode, type)
    periode = []
    nilai = []
    growth = []
    for row in result["data"]:
        periode.append(row["periode"])
        nilai.append(row["nilai"])
        growth.append(row["growth"])
    return {
        "kode": kode,
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


def get_annual_chart(db: Session, kode: str):
    result = get_annual_data(db, kode)
    tahun = []
    nilai = []
    for row in result["data"]:
        tahun.append(row["tahun"])
        nilai.append(row["nilai"])
    return {
        "kode": kode,
        "xAxis": tahun,
        "series": [
            {
                "name": "annual",
                "data": nilai,
            }
        ],
    }
