from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Index,
    UniqueConstraint,
)
from datetime import datetime, timezone
from app.db.base import Base


class Pdb(Base):
    __tablename__ = "pdb"

    id = Column(Integer, primary_key=True, index=True)
    kode = Column(Integer, index=True, nullable=False)
    deskripsi = Column(String, nullable=False)
    satuan = Column(String, nullable=False)
    jenis = Column(String(4), index=True, nullable=False)
    tahun = Column(Integer, index=True, nullable=False)
    freq = Column(String(1), index=True, nullable=False)  # M / Q / Y
    period = Column(Integer, index=True, nullable=False)  # 1-12 / 1-4
    nilai = Column(Float, nullable=False)

    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        Index("idx_pdb_lookup", "kode", "jenis", "freq", "tahun", "period"),
        UniqueConstraint(
            "kode", "jenis", "tahun", "freq", "period", name="uq_pdb_kode_time"
        ),
    )

    @property
    def periode(self):
        return f"{self.tahun}{self.freq}{self.period}"
