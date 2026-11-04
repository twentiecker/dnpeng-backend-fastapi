from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Index,
    UniqueConstraint,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base


class Pdb(Base):
    __tablename__ = "pdb"

    id = Column(Integer, primary_key=True, index=True)

    kode_wilayah = Column(
        String(20),
        ForeignKey("master_wilayah.kode_wilayah"),
        nullable=False,
        index=True,
    )

    kode = Column(Integer, index=True, nullable=False)
    deskripsi = Column(String, nullable=False)
    satuan = Column(String, nullable=False)
    konversi = Column(String, nullable=False)
    jenis = Column(String(4), index=True, nullable=False)
    tahun = Column(Integer, index=True, nullable=False)
    freq = Column(String(1), index=True, nullable=False)  # M / Q / Y
    period = Column(Integer, index=True, nullable=False)  # 1-12 / 1-4
    nilai = Column(Float, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship
    wilayah = relationship(
        "MasterWilayah",
        back_populates="pdb",
        # lazy="selectin",
    )

    __table_args__ = (
        Index(
            "idx_pdb_lookup",
            "kode_wilayah",
            "kode",
            "jenis",
            "freq",
            "tahun",
            "period",
        ),
        UniqueConstraint(
            "kode_wilayah",
            "kode",
            "jenis",
            "tahun",
            "freq",
            "period",
            name="uq_pdb_kode_time",
        ),
    )

    @property
    def periode(self):
        return f"{self.tahun}{self.freq}{self.period}"
