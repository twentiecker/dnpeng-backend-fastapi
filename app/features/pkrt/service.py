from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from collections import defaultdict
from app.models.pkrt import Pkrt
from app.features.pkrt import repository as repo
from app.services.timeseries import (
    parse_periode,
    monthly_to_quarterly,
    compute_qtoq,
    compute_yony,
    compute_ctoc,
    compute_annual,
)


def add_pkrt(
    db: Session,
    kode: str,
    deskripsi: str,
    satuan: str,
    konversi: str,
    periode: str,
    nilai: float,
):
    try:
        tahun, freq, period = parse_periode(periode)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    data = Pkrt(
        kode=kode,
        deskripsi=deskripsi,
        satuan=satuan,
        konversi=konversi,
        tahun=tahun,
        freq=freq,
        period=period,
        nilai=nilai,
    )
    return repo.create_pkrt(db, data)


def get_pkrt_data(db: Session, kode: str | None, periode: str | None):
    tahun = None
    freq = None
    period = None
    if periode:
        tahun, freq, period = parse_periode(periode)
    return repo.filter_pkrt(db, kode, tahun, freq, period)


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
    if not data:
        return {"kode": kode, "type": type, "data": []}
    period_type = data[0].freq  # M atau Q
    if type == "qtoq" or type == "mtom":
        if period_type == "M" and type == "qtoq":
            quarterly_data = monthly_to_quarterly(data)
            result = compute_qtoq(quarterly_data)
        elif (period_type == "Q" and type == "qtoq") or (
            period_type == "M" and type == "mtom"
        ):
            result = compute_qtoq(data)
        else:
            result = []
    elif type == "yony" or type == "yony_m":
        if period_type == "M" and type == "yony":
            quarterly_data = monthly_to_quarterly(data)
            result = compute_yony(quarterly_data)
        elif (period_type == "Q" and type == "yony") or (
            period_type == "M" and type == "yony_m"
        ):
            result = compute_yony(data)
    elif type == "ctoc" or type == "ytod":
        if period_type == "M" and type == "ctoc":
            quarterly_data = monthly_to_quarterly(data)
            result = compute_ctoc(quarterly_data)
        elif (period_type == "Q" and type == "ctoc") or (
            period_type == "M" and type == "ytod"
        ):
            result = compute_ctoc(data)
    elif type == "annual":
        result = compute_annual(data)
    else:
        result = []
    return {"kode": kode, "type": type, "data": result}


def get_quarter_data(db: Session, kode: str):
    data = repo.query_timeseries(db, kode, None, None)
    if not data:
        return {"kode": kode, "data": []}
    result = monthly_to_quarterly(data)
    return {"kode": kode, "data": result}


def get_annual_data(db: Session, kode: str):
    data = repo.query_timeseries(db, kode, None, None)
    if not data:
        return {"kode": kode, "data": []}
    konversi = data[0].konversi  # ✅ ambil sekali
    annual = defaultdict(list)
    # grouping per tahun
    for d in data:
        year = d.periode[:4]
        annual[year].append(d)
    result = []
    for year, items in annual.items():
        values = [d.nilai for d in items]
        if konversi == "SUM":
            nilai = sum(values)
        elif konversi == "AVG":
            nilai = sum(values) / len(values)
        elif konversi == "last":
            # ambil periode terakhir dalam tahun
            last_item = sorted(items, key=lambda x: x.periode)[-1]
            nilai = last_item.nilai
        else:
            raise ValueError(f"Metode konversi tidak dikenali: {konversi}")
        result.append({"tahun": year, "nilai": nilai})
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


def get_quarter_chart(db: Session, kode: str):
    result = get_quarter_data(db, kode)
    periode = []
    nilai = []
    for row in result["data"]:
        periode.append(row["periode"])
        nilai.append(row["nilai"])
    return {
        "kode": kode,
        "xAxis": periode,
        "series": [
            {
                "name": "quarter",
                "data": nilai,
            }
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
