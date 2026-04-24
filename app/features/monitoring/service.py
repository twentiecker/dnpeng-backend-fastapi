from sqlalchemy.orm import Session
from io import BytesIO
from app.features.monitoring import repository as repo
from app.features.monitoring.utils import parse_monitoring_excel, format_chart_data


# =====================================
# UPLOAD FILE EXCEL
# =====================================
def upload_monitoring_excel(db, file, uploaded_by: str):
    content = file.file.read()

    excel_file = BytesIO(content)

    rows = parse_monitoring_excel(
        file=excel_file, filename=file.filename, uploaded_by=uploaded_by
    )

    if not rows:
        return {"message": "Tidak ada data ditemukan"}

    repo.bulk_upsert(db, rows)

    return {
        "message": "Upload berhasil",
        "filename": file.filename,
        "rows_processed": len(rows),
    }


# ======================================
# GET ALL DATA
# ======================================
def get_all_monitoring(db: Session):
    return repo.get_all(db)


# ======================================
# FILTER DATA
# ======================================
def get_monitoring_by_filter(
    db: Session,
    tahun: int = None,
    bulan: int = None,
    freq: str = None,
    komponen: str = None,
):
    return repo.get_by_filter(
        db=db, tahun=tahun, bulan=bulan, freq=freq, komponen=komponen
    )


# ======================================
# CREATE SINGLE DATA
# ======================================
def create_monitoring(db: Session, payload):
    if payload.tahun < 2000:
        raise Exception("Tahun tidak valid")

    if payload.bulan:
        if payload.bulan < 1 or payload.bulan > 12:
            raise Exception("Bulan harus 1 - 12")

    if payload.freq not in ["MONTHLY", "QUARTERLY", "ANNUAL"]:
        raise Exception("Frekuensi data tidak valid")

    return repo.create(db, payload.dict())


# ======================================
# UPSERT SINGLE
# ======================================
def upsert_monitoring(db: Session, payload):

    data = payload.dict()

    action = repo.upsert(db, data)

    return {
        "success": True,
        "action": action,
        "key": {
            "komponen": data["komponen"],
            "no": data["no"],
            "tahun": data["tahun"],
            "bulan": data["bulan"],
        },
        "message": (
            "Data baru berhasil ditambahkan"
            if action == "inserted"
            else "Data berhasil diperbarui"
        ),
    }


# ======================================
# BULK UPSERT
# ======================================
def bulk_upsert_monitoring(db: Session, rows: list[dict]):

    if not rows:
        return {"message": "Tidak ada data diproses"}

    repo.bulk_upsert(db, rows)

    return {"message": f"{len(rows)} data berhasil diproses"}


# ======================================
# DELETE DATA BY YEAR
# ======================================
def delete_monitoring_by_year(db: Session, tahun: int):

    repo.delete_by_year(db, tahun)

    return {"message": f"Data tahun {tahun} berhasil dihapus"}


# ======================================
# PROGRESS DATA BY FIELD
# ======================================
def format_progress_data(rows, group_by_cols):
    result = []
    for row in rows:
        item = {}

        # isi kolom group by dinamis
        for col in group_by_cols:
            item[col] = row[col]

        # kolom tetap
        item["jumlah_target"] = row["jumlah_target"]
        item["jumlah_data_masuk"] = row["jumlah_data_masuk"]
        item["progress_persen"] = row["progress_persen"]

        result.append(item)

    return result


def get_progress_service(db, group_by, triwulan):
    data = repo.get_monitoring_progress(db, group_by, triwulan)
    return format_progress_data(data, group_by)


# ======================================
# CHART PROGRESS DATA BY FIELD
# ======================================
def get_chart_service(db, group_by, triwulan):
    rows = repo.get_monitoring_chart(db, group_by, triwulan)
    return format_chart_data(rows, group_by)


# ======================================
# SUMMARY BULANAN
# ======================================
def get_summary_monthly(db: Session, tahun: int):

    result = repo.get_summary_by_month(db, tahun)

    return {"tahun": tahun, "bulan_terisi": [x[0] for x in result]}
