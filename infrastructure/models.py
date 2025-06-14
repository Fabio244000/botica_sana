from datetime import date, datetime

from sqlalchemy import (Boolean, Date, DateTime, Enum, Float, ForeignKey,
                        Integer, String, UniqueConstraint, func)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.enums import Presentacion, TipoMovimiento
from core.models.rol import Rol
from infrastructure.db import Base


class MedicamentoSQL(Base):
    __tablename__ = "medicamentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    principio_activo: Mapped[str] = mapped_column(String(120), nullable=False)
    laboratorio: Mapped[str | None] = mapped_column(String(120))
    presentacion: Mapped[Presentacion] = mapped_column(
        Enum(Presentacion), nullable=False
    )
    precio_venta: Mapped[float] = mapped_column(Float, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    lotes: Mapped[list["LoteSQL"]] = relationship(back_populates="medicamento")


class LoteSQL(Base):
    __tablename__ = "lotes"
    __table_args__ = (UniqueConstraint("codigo"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(50), nullable=False)
    medicamento_id: Mapped[int] = mapped_column(
        ForeignKey("medicamentos.id", ondelete="CASCADE"), nullable=False
    )
    fecha_vencimiento: Mapped[date] = mapped_column(Date, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    medicamento: Mapped["MedicamentoSQL"] = relationship(back_populates="lotes")
    movimientos: Mapped[list["MovimientoSQL"]] = relationship(back_populates="lote")


class MovimientoSQL(Base):
    __tablename__ = "movimientos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lote_id: Mapped[int] = mapped_column(
        ForeignKey("lotes.id", ondelete="CASCADE"), nullable=False
    )
    tipo: Mapped[TipoMovimiento] = mapped_column(Enum(TipoMovimiento), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    motivo: Mapped[str] = mapped_column(String(120), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    lote: Mapped["LoteSQL"] = relationship(back_populates="movimientos")


class UsuarioSQL(Base):
    __tablename__ = "usuarios"
    __table_args__ = (UniqueConstraint("username"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    rol: Mapped[Rol] = mapped_column(Enum(Rol), nullable=False, default=Rol.CAJERO)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
