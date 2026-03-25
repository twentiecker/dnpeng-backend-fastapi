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
    if not data:
        return 1
    freq = data[0].freq
    if freq == "Q":
        return 4
    if freq == "M":
        return 12
    return 1


def monthly_to_quarterly(data):
    result = []
    for i in range(0, len(data), 3):
        chunk = data[i : i + 3]
        if len(chunk) < 3:
            continue
        total = sum(d.nilai for d in chunk)
        result.append(
            {
                "periode": chunk[-1].periode,  # pakai bulan terakhir sebagai label
                "nilai": total,
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
        if i < shift:
            growth = None
        else:
            growth = calc_growth(d.nilai, data[i - shift].nilai)
        result.append(
            {
                "periode": d.periode,
                "nilai": d.nilai,
                "growth": growth,
            }
        )
    return result


def compute_ctoc(data):
    shift = detect_shift(data)
    result = []
    for i, d in enumerate(data):
        if i < shift:
            growth = None
            current_sum = None
        else:
            current_sum = sum(data[i - j].nilai for j in range(d.period))
            prev_sum = sum(data[i - shift - j].nilai for j in range(d.period))
            growth = calc_growth(current_sum, prev_sum)
        result.append(
            {
                "periode": d.periode,
                "nilai": d.nilai,
                "cumulative": current_sum,
                "growth": growth,
            }
        )
    return result


def compute_annual(data):
    ctoc = compute_ctoc(data)
    shift = detect_shift(data)
    result = []
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
