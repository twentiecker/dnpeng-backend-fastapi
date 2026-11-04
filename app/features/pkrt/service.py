from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from collections import defaultdict
from app.models.pkrt import Pkrt
from app.features.pkrt import repository as repo
from app.services.timeseries import (
    parse_periode,
    monthly_to_quarterly,
    compute_period_growth,
    compute_yony,
    compute_ctoc,
    compute_annual,
)


def add_pkrt(
    db: Session,
    kode_wilayah: str,
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
        kode_wilayah=kode_wilayah,
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


def get_pkrt_data(
    db: Session, kode_wilayah: str | None, kode: str | None, periode: str | None
):
    tahun = None
    freq = None
    period = None
    if periode:
        tahun, freq, period = parse_periode(periode)
    return repo.filter_pkrt(db, kode_wilayah, kode, tahun, freq, period)


def get_pkrt_kode(db: Session, kode_wilayah: str, kode: str):
    return repo.get_pkrt_by_kode(db, kode_wilayah, kode)


def get_pkrt_periode(db: Session, kode_wilayah: str, periode: str):
    return repo.get_pkrt_by_periode(db, kode_wilayah, periode)


# def get_timeseries(
#     db: Session,
#     kode_wilayah: str,
#     kode: str,
#     start: str | None,
#     end: str | None,
# ):
#     data = repo.query_timeseries(db, kode_wilayah, kode, start, end)
#     return {
#         "kode": kode,
#         "data": [{"periode": d.periode, "nilai": d.nilai} for d in data],
#     }


def get_timeseries(
    db: Session,
    kode_wilayah: str,
    kode: str,
    start: str | None,
    end: str | None,
):
    # Validasi start dan end harus memiliki frequency yang sama
    if start and end:
        try:
            start_tahun, start_freq, start_period = parse_periode(start)
            end_tahun, end_freq, end_period = parse_periode(end)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

        if start_freq != end_freq:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start dan end harus memiliki frekuensi yang sama (M dengan M atau Q dengan Q)",
            )

        if start_tahun > end_tahun or (
            start_tahun == end_tahun and start_period > end_period
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start tidak boleh lebih besar dari end",
            )

    data = repo.query_timeseries(
        db,
        kode_wilayah,
        kode,
        start,
        end,
    )

    return {
        "kode": kode,
        "data": [{"periode": d.periode, "nilai": d.nilai} for d in data],
    }


def get_indikator_list(db: Session, kode_wilayah: str):
    data = repo.get_indikator_list(db, kode_wilayah)
    return [{"kode": d.kode, "deskripsi": d.deskripsi} for d in data]


def get_latest(db: Session, kode_wilayah: str):
    return repo.get_latest(db, kode_wilayah)


# def get_growth_rate(db: Session, kode_wilayah: str, kode: str, type: str):
#     data = repo.query_timeseries(db, kode_wilayah, kode)

#     if not data:
#         return {"kode": kode, "type": type, "data": []}

#     period_type = data[0].freq  # "M" atau "Q"

#     # 🔥 Mapping transform
#     transform_map = {
#         ("M", "qtoq"): monthly_to_quarterly,
#         ("M", "yony"): monthly_to_quarterly,
#         ("M", "ctoc"): monthly_to_quarterly,
#     }

#     # 🔥 Mapping compute function
#     compute_map = {
#         "qtoq": compute_period_growth,
#         "mtom": compute_period_growth,
#         "yony": compute_yony,
#         "yony_m": compute_yony,
#         "ctoc": compute_ctoc,
#         "ytod": compute_ctoc,
#         "annual": compute_annual,
#     }

#     # default result
#     result = []

#     # 🔥 Step 1: transform data kalau perlu
#     transform_fn = transform_map.get((period_type, type))
#     processed_data = transform_fn(data) if transform_fn else data

#     # 🔥 Step 2: ambil compute function
#     compute_fn = compute_map.get(type)

#     if compute_fn:
#         # special case annual (nggak butuh transform logic tambahan)
#         result = compute_fn(processed_data)

#     return {
#         "kode": kode,
#         "type": type,
#         "data": result,
#     }

VALID_GROWTH_TYPES = {
    "mtom",
    "yony_m",
    "ytod",
    "qtoq",
    "yony",
    "ctoc",
    "annual",
}


def prepare_growth_data(data, growth_type):
    freq = data[0].freq

    if freq == "M":
        if growth_type in {"qtoq", "yony", "ctoc"}:
            return monthly_to_quarterly(data)

        return data

    if freq == "Q":
        return data

    raise ValueError(f"Frequency tidak didukung: {freq}")


# def get_growth_rate(
#     db: Session,
#     kode_wilayah: str,
#     kode: str,
# type: str,
# ):
#     if type not in VALID_GROWTH_TYPES:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Tipe growth tidak dikenali: {type}",
#         )

#     data = repo.query_timeseries(db, kode_wilayah, kode)

#     if not data:
#         return {
#             "kode": kode,
#             "type": type,
#             "data": [],
#         }

#     processed_data = prepare_growth_data(data, type)

#     compute_map = {
#         "mtom": compute_period_growth,
#         "qtoq": compute_period_growth,
#         "yony_m": compute_yony,
#         "yony": compute_yony,
#         "ytod": compute_ctoc,
#         "ctoc": compute_ctoc,
#         "annual": compute_annual,
#     }

#     # compute_fn = compute_map.get(type)

#     # if not compute_fn:
#     #     raise HTTPException(
#     #         status_code=status.HTTP_400_BAD_REQUEST,
#     #         detail=f"Tipe growth tidak dikenali: {type}",
#     #     )

#     # result = compute_fn(processed_data)

#     result = compute_map[type](processed_data)

#     return {
#         "kode": kode,
#         "type": type,
#         "data": result,
#     }


def compute_growth(data, growth_type):
    if not data:
        return []

    processed_data = prepare_growth_data(
        data,
        growth_type,
    )

    compute_map = {
        "mtom": compute_period_growth,
        "qtoq": compute_period_growth,
        "yony_m": compute_yony,
        "yony": compute_yony,
        "ytod": compute_ctoc,
        "ctoc": compute_ctoc,
        "annual": compute_annual,
    }

    return compute_map[growth_type](processed_data)


def get_growth_rate(
    db: Session,
    kode_wilayah: str,
    kode: str,
    type: str,
):
    if type not in VALID_GROWTH_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipe growth tidak dikenali: {type}",
        )

    data = repo.query_timeseries(
        db,
        kode_wilayah,
        kode,
    )

    result = compute_growth(
        data,
        type,
    )

    return {
        "kode": kode,
        "type": type,
        "data": result,
    }


def get_quarter_data(db: Session, kode_wilayah: str, kode: str):
    data = repo.query_timeseries(db, kode_wilayah, kode)
    if not data:
        return {"kode": kode, "data": []}
    result = monthly_to_quarterly(data)
    return {"kode": kode, "data": result}


def get_annual_data(db: Session, kode_wilayah: str, kode: str):
    data = repo.query_timeseries(db, kode_wilayah, kode)
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
        elif konversi == "LAST":
            # ambil periode terakhir dalam tahun
            last_item = sorted(items, key=lambda x: x.periode)[-1]
            nilai = last_item.nilai
        else:
            raise ValueError(f"Metode konversi tidak dikenali: {konversi}")
        result.append({"tahun": year, "nilai": nilai})
    return {"kode": kode, "data": result}


def get_chart_data(db: Session, kode_wilayah: str, kode: str):
    data = repo.query_timeseries(db, kode_wilayah, kode)
    periode = []
    values = []
    for d in data:
        periode.append(d.periode)
        values.append(d.nilai)
    return {"kode": kode, "xAxis": periode, "series": [{"name": kode, "data": values}]}


def get_growth_chart(db: Session, kode_wilayah: str, kode: str, type: str):
    result = get_growth_rate(db, kode_wilayah, kode, type)
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


def get_quarter_chart(db: Session, kode_wilayah: str, kode: str):
    result = get_quarter_data(db, kode_wilayah, kode)
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


def get_annual_chart(db: Session, kode_wilayah: str, kode: str):
    result = get_annual_data(db, kode_wilayah, kode)
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


# ==================================================
# Aggregator Service
# ==================================================
def group_by_kode(data):
    grouped = defaultdict(list)

    for row in data:
        grouped[row.kode].append(row)

    return grouped


def build_indicator(data):
    if not data:
        return {}

    first = data[0]

    return {
        "kode": first.kode,
        "deskripsi": first.deskripsi,
        "satuan": first.satuan,
        "freq": first.freq,
        "konversi": first.konversi,
    }


def build_series_data(data):
    return {
        "periods": [d.periode for d in data],
        "data": [d.nilai for d in data],
    }


def build_series(data):
    if not data:
        return {
            "monthly": {
                "periods": [],
                "data": [],
            },
            "quarterly": {
                "periods": [],
                "data": [],
            },
            "yearly": {
                "periods": [],
                "data": [],
            },
        }

    freq = data[0].freq

    if freq == "M":
        quarterly_data = monthly_to_quarterly(data)
        yearly_data = compute_annual(data)

        return {
            "monthly": build_series_data(data),
            "quarterly": {
                "periods": [d["periode"] for d in quarterly_data],
                "data": [d["nilai"] for d in quarterly_data],
            },
            "yearly": {
                "periods": [d["periode"] for d in yearly_data],
                "data": [d["nilai"] for d in yearly_data],
            },
        }

    if freq == "Q":
        yearly_data = compute_annual(data)

        return {
            "monthly": {
                "periods": [],
                "data": [],
            },
            "quarterly": build_series_data(data),
            "yearly": {
                "periods": [d["periode"] for d in yearly_data],
                "data": [d["nilai"] for d in yearly_data],
            },
        }

    raise ValueError(f"Frequency tidak didukung: {freq}")


def build_growth_data(data):
    return {
        "periods": [d["periode"] for d in data],
        "data": [d["growth"] for d in data],
    }


GROWTH_TYPES = (
    "mtom",
    "yony_m",
    "ytod",
    "qtoq",
    "yony",
    "ctoc",
    "annual",
)


# def build_growth(
#     db: Session,
#     kode_wilayah: str,
#     kode: str,
# ):
#     result = {}

#     for growth_type in GROWTH_TYPES:
#         growth_data = get_growth_rate(
#             db,
#             kode_wilayah,
#             kode,
#             growth_type,
#         )

#         result[growth_type] = build_growth_data(growth_data["data"])

#     return result


def build_growth(data):
    result = {}

    for growth_type in GROWTH_TYPES:
        growth_data = compute_growth(
            data,
            growth_type,
        )

        result[growth_type] = build_growth_data(growth_data)

    return result


def get_aggregated_data(
    db: Session,
    kode_wilayah: str,
):
    import time

    start = time.perf_counter()

    data = repo.filter_pkrt(
        db,
        kode_wilayah=kode_wilayah,
    )

    print(
        "DB:",
        time.perf_counter() - start,
    )

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data PKRT tidak ditemukan",
        )

    start = time.perf_counter()

    grouped = group_by_kode(data)

    print(
        "GROUP:",
        time.perf_counter() - start,
    )

    result = {}

    start = time.perf_counter()

    for kode, rows in grouped.items():
        result[kode] = {
            "indikator": build_indicator(rows),
            "series": build_series(rows),
            # "growth": build_growth(
            #     db,
            #     kode_wilayah,
            #     kode,
            # ),
            "growth": build_growth(rows),
        }

    print(
        "CALC:",
        time.perf_counter() - start,
    )

    return {
        "data": result,
    }
