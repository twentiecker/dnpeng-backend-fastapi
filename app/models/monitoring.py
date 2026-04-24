from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Text,
    Numeric,
    DateTime,
    Boolean,
    UniqueConstraint,
    Index,
)

from sqlalchemy.sql import func
from app.db.base import Base


class Monitoring(Base):
    __tablename__ = "monitoring"

    id = Column(BigInteger, primary_key=True, index=True)

    # Metadata dataset
    komponen = Column(String(100), nullable=False)
    no = Column(Integer, nullable=False)
    nama_data = Column(Text, nullable=False)

    internal_external = Column(String(30), nullable=True)
    pjk_neraca = Column(String(30), nullable=True)
    penanggung_jawab = Column(Text, nullable=True)
    jumlah_data = Column(Integer, nullable=False)
    jumlah_datum = Column(Integer, nullable=False)

    # Period
    tahun = Column(Integer, nullable=False)
    bulan = Column(Integer, nullable=True)  # null = annual

    # Value
    nilai = Column(Numeric(20, 2), nullable=True)

    # MONTHLY / QUARTERLY / ANNUAL
    freq = Column(String(20), nullable=False)

    # Notes
    keterangan = Column(Text, nullable=True)

    # Audit
    source_file = Column(String(255), nullable=True)
    uploaded_by = Column(String(100), nullable=True)

    is_locked = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # ===========================
    # Constraint + Index
    # ===========================
    __table_args__ = (
        # prevent duplicate period
        UniqueConstraint(
            "komponen", "no", "tahun", "bulan", name="uq_monitoring_periode"
        ),
        # dashboard query
        Index("idx_monitoring_tahun_bulan", "tahun", "bulan"),
        # filter by freq
        Index("idx_monitoring_freq", "freq"),
        # lookup dataset
        Index("idx_monitoring_dataset", "komponen", "no"),
        # frequent filter
        Index("idx_monitoring_tahun_freq", "tahun", "freq"),
    )
