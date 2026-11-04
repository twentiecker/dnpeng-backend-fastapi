from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.db.base import Base


class MasterWilayah(Base):
    __tablename__ = "master_wilayah"

    id = Column(Integer, primary_key=True)

    # Contoh:
    # 00         -> Indonesia
    # 11         -> Aceh
    # 1101       -> Kab. Simeulue
    # 1101010    -> Kec. Teupah Selatan
    # 1101010001 -> Desa ...
    kode_wilayah = Column(
        String(20),
        nullable=False,
    )

    nama_wilayah = Column(
        String,
        nullable=False,
    )

    # NASIONAL | PROVINSI | KABKOT | KECAMATAN | DESA
    level = Column(
        String(20),
        nullable=False,
    )

    # NULL untuk root (Indonesia)
    parent_kode = Column(
        String(20),
        ForeignKey("master_wilayah.kode_wilayah"),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ==========================
    # Self Relationship
    # ==========================

    # Parent -> Children
    parent = relationship(
        "MasterWilayah",
        remote_side=[kode_wilayah],
        back_populates="children",
    )

    children = relationship(
        "MasterWilayah",
        back_populates="parent",
    )

    # ==========================
    # Dataset Relationship
    # ==========================

    # Relasi ke tabel EKSIM
    eksim = relationship(
        "Eksim",
        back_populates="wilayah",
        # lazy="selectin",
    )

    # Relasi ke tabel PDB
    pdb = relationship(
        "Pdb",
        back_populates="wilayah",
        # lazy="selectin",
    )

    # Relasi ke tabel PKP
    pkp = relationship(
        "Pkp",
        back_populates="wilayah",
        # lazy="selectin",
    )

    # Relasi ke tabel PKRT
    pkrt = relationship(
        "Pkrt",
        back_populates="wilayah",
        # lazy="selectin",
    )

    # Relasi ke tabel PMTB
    pmtb = relationship(
        "Pmtb",
        back_populates="wilayah",
        # lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint(
            "kode_wilayah",
            name="uq_master_wilayah_kode_wilayah",
        ),
        Index("idx_master_wilayah_level", "level"),
        Index("idx_master_wilayah_parent", "parent_kode"),
    )

    def __repr__(self):
        return (
            f"<MasterWilayah("
            f"kode='{self.kode_wilayah}', "
            f"nama='{self.nama_wilayah}', "
            f"level='{self.level}')>"
        )
