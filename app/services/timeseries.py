def parse_periode(periode: str):
    try:
        tahun = int(periode[:4])
        freq = periode[4]
        period = int(periode[5:])
        if freq == "Q" and not (1 <= period <= 4):
            raise ValueError("Quarter harus 1-4")
        if freq == "M" and not (1 <= period <= 12):
            raise ValueError("Month harus 1-12")
        return tahun, freq, period
    except Exception:
        raise ValueError("Format periode tidak valid")


def detect_shift(data):
    first = data[0]
    if isinstance(first, dict):
        freq = first.get("freq", "Q")  # default Q biar aman
    else:
        freq = first.freq
    if freq == "M":
        return 12
    elif freq == "Q":
        return 4


def monthly_to_quarterly(data):
    result = []
    if not data:
        return result
    freq = data[0].freq
    # ✅ kalau sudah quarterly → return apa adanya
    if freq == "Q":
        return [
            {
                "periode": d.periode,
                "nilai": d.nilai,
                "freq": "Q",
                "period": d.period,
            }
            for d in data
        ]
    # lanjut hanya kalau monthly
    konversi = data[0].konversi
    if konversi == "NaN":
        return result  # skip semua
    for i in range(0, len(data), 3):
        chunk = data[i : i + 3]
        if len(chunk) < 3:
            continue
        values = [d.nilai for d in chunk]
        if konversi == "SUM":
            nilai = sum(values)
        elif konversi == "AVG":
            nilai = sum(values) / len(values)
        elif konversi == "LAST":
            nilai = values[-1]
        else:
            raise ValueError(f"Metode konversi tidak dikenali: {konversi}")
        result.append(
            {
                "periode": chunk[-1].periode,
                "nilai": nilai,
                "freq": "Q",
                "period": (i // 3) % 4 + 1,
            }
        )
    return result


def calc_growth(curr, prev):
    if prev == 0:
        return None
    return ((curr - prev) / prev) * 100


def compute_qtoq(data):
    result = []
    for i, d in enumerate(data):
        nilai = d["nilai"] if isinstance(d, dict) else d.nilai
        periode = d["periode"] if isinstance(d, dict) else d.periode
        if i == 0:
            growth = None
        else:
            prev = data[i - 1]
            prev_nilai = prev["nilai"] if isinstance(prev, dict) else prev.nilai
            growth = calc_growth(nilai, prev_nilai)
        result.append({"periode": periode, "nilai": nilai, "growth": growth})
    return result


def compute_yony(data):
    shift = detect_shift(data)
    result = []
    for i, d in enumerate(data):
        nilai = d["nilai"] if isinstance(d, dict) else d.nilai
        periode = d["periode"] if isinstance(d, dict) else d.periode
        if i < shift:
            growth = None
        else:
            prev = data[i - shift]
            prev_nilai = prev["nilai"] if isinstance(prev, dict) else prev.nilai
            growth = calc_growth(nilai, prev_nilai)
        result.append(
            {
                "periode": periode,
                "nilai": nilai,
                "growth": growth,
            }
        )
    return result


def compute_ctoc(data):
    shift = detect_shift(data)
    result = []
    for i, d in enumerate(data):
        nilai = d["nilai"] if isinstance(d, dict) else d.nilai
        periode = d["periode"] if isinstance(d, dict) else d.periode  # label
        period = d["period"] if isinstance(d, dict) else d.period  # angka
        if i < shift:
            growth = None
            current_sum = None
        else:
            current_sum = sum(
                (
                    data[i - j]["nilai"]
                    if isinstance(data[i - j], dict)
                    else data[i - j].nilai
                )
                for j in range(period)
            )
            prev_sum = sum(
                (
                    data[i - shift - j]["nilai"]
                    if isinstance(data[i - shift - j], dict)
                    else data[i - shift - j].nilai
                )
                for j in range(period)
            )
            growth = calc_growth(current_sum, prev_sum)
        result.append(
            {
                "periode": periode,
                "nilai": nilai,
                "cumulative": current_sum,
                "growth": growth,
            }
        )
    return result


def compute_annual(data):
    result = []
    konversi = data[0].konversi
    if konversi == "NaN":
        return result  # skip semua
    ctoc = compute_ctoc(data)
    shift = detect_shift(data)
    for row in ctoc:
        if row["periode"].endswith(str(shift)):
            result.append(
                {
                    "periode": row["periode"][:4],
                    "nilai": row["cumulative"],
                    "growth": row["growth"],
                }
            )
    return result
