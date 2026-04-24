import pandas as pd


MONTH_MAP = {
    "JAN": 1,
    "FEB": 2,
    "MAR": 3,
    "APR": 4,
    "MEI": 5,
    "JUN": 6,
    "JUL": 7,
    "AGU": 8,
    "SEP": 9,
    "OKT": 10,
    "NOV": 11,
    "DES": 12,
}


def parse_monitoring_excel(file, filename: str, uploaded_by: str):

    df = pd.read_excel(file, sheet_name=0)

    # rapikan nama kolom
    df.columns = [str(col).strip().upper() for col in df.columns]

    # buang row kosong total
    df = df.dropna(how="all")

    # skip header duplikat di tengah
    df = df[df["KOMPONEN"] != "KOMPONEN"]

    # forward fill komponen
    df["KOMPONEN"] = df["KOMPONEN"].ffill()

    rows = []

    for _, row in df.iterrows():

        for month_name, month_num in MONTH_MAP.items():

            if month_name not in df.columns:
                continue

            value = row.get(month_name)

            if pd.isna(value):
                # continue
                value = 0

            rows.append(
                {
                    "komponen": row.get("KOMPONEN"),
                    "no": int(row.get("NO")),
                    "nama_data": row.get("NAMA DATA"),
                    "internal_external": row.get("INTERNAL/EXTERNAL"),
                    "pjk_neraca": row.get("PJK/ NERACA"),
                    "penanggung_jawab": row.get("PENANGGUNG JAWAB DATA"),
                    "jumlah_data": row.get("JUMLAH DATA"),
                    "jumlah_datum": row.get("JUMLAH DATUM"),
                    "bulan": month_num,
                    "tahun": int(row.get("TAHUN")),
                    "nilai": float(value),
                    "freq": str(row.get("FREQ")).upper(),
                    "keterangan": row.get("KETERANGAN"),
                    "source_file": filename,
                    "uploaded_by": uploaded_by,
                }
            )

    return rows


def build_monitoring_progress_query(group_by_cols: list[str], triwulan=None):

    cols = ", ".join(group_by_cols)

    # COALESCE select
    select_cols = ",\n".join([f"COALESCE(t.{c}, m.{c}) AS {c}" for c in group_by_cols])

    # JOIN condition
    join_cond = "\nAND ".join([f"t.{c} = m.{c}" for c in group_by_cols])

    # =========================
    # DINAMIS WHERE
    # =========================

    where_clause = ""

    if triwulan == 1:
        bulan_list = "1,2,3"
    elif triwulan == 2:
        bulan_list = "4,5,6"
    elif triwulan == 3:
        bulan_list = "7,8,9"
    elif triwulan == 4:
        bulan_list = "10,11,12"
    else:
        bulan_list = ""

    if triwulan:
        where_clause = f"""
    WHERE (
        LOWER(freq) = 'annual'
        AND bulan IN ({bulan_list})
        AND COALESCE(nilai,0) > 0
    )
    OR (
        LOWER(freq) <> 'annual'
        AND bulan IN ({bulan_list})
    )
    """

    # ORDER BY
    order_by = ", ".join(group_by_cols)

    # =========================
    # DINAMIS DISTINCT
    # =========================

    # kolom default target
    target_base_cols = [
        "nama_data",
        "internal_external",
        "pjk_neraca",
        "penanggung_jawab",
        "jumlah_data",
        "jumlah_datum",
        "tahun",
        "freq",
    ]

    # kolom default masuk
    masuk_base_cols = [
        "nama_data",
        "internal_external",
        "pjk_neraca",
        "penanggung_jawab",
        "jumlah_data",
        "jumlah_datum",
        "tahun",
        "bulan",
        "nilai",
        "freq",
    ]

    # gabungkan group_by_cols + base_cols
    # dict.fromkeys = hilangkan duplicate tapi urutan tetap
    target_distinct_cols = ",\n            ".join(
        dict.fromkeys(group_by_cols + target_base_cols)
    )

    masuk_distinct_cols = ",\n            ".join(
        dict.fromkeys(group_by_cols + masuk_base_cols)
    )

    query = f"""
WITH target AS (
    SELECT {cols},
           SUM(jumlah_datum) AS jumlah_target
    FROM (
        SELECT DISTINCT
            {target_distinct_cols}
        FROM monitoring
        {where_clause}
    ) t
    GROUP BY {cols}
),

masuk AS (
    SELECT {cols},
           SUM(nilai) AS jumlah_data_masuk
    FROM (
        SELECT DISTINCT
            {masuk_distinct_cols}
        FROM monitoring
        {where_clause}
    ) t
    GROUP BY {cols}
)

SELECT
    {select_cols},
    t.jumlah_target,
    m.jumlah_data_masuk,

    ROUND(
        100.0 * m.jumlah_data_masuk / NULLIF(t.jumlah_target,0),
        2
    ) AS progress_persen

FROM target t
FULL OUTER JOIN masuk m
ON {join_cond}

ORDER BY {order_by}
"""
    return query


def format_chart_data(rows, group_by_cols):
    labels = []
    values = []

    for row in rows:

        # gabungkan multi group jadi label
        label = " - ".join(str(row[col]) for col in group_by_cols)

        labels.append(label)
        values.append(float(row["progress_persen"] or 0))

    return {"labels": labels, "datasets": [{"label": "Progress %", "data": values}]}
