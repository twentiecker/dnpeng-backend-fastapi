def parse_periode(periode: str):
    tahun = int(periode[:4])
    freq = periode[4]
    period = int(periode[5:])
    return tahun, freq, period


def detect_shift(data):
    if not data:
        return 1
    freq = data[0].freq
    if freq == "Q":
        return 4
    if freq == "M":
        return 12
    return 1


def calc_growth(curr, prev):
    if prev == 0:
        return None
    return ((curr - prev) / prev) * 100


def compute_qtoq(data):
    result = []
    for i, d in enumerate(data):
        if i == 0:
            growth = None
        else:
            growth = calc_growth(d.nilai, data[i - 1].nilai)
        result.append({"periode": d.periode, "nilai": d.nilai, "growth": growth})
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
