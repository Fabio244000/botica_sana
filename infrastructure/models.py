from datetime import date, datetime
from typing import Optional

from sqlalchemy import CheckConstraint  # ← NUEVO
from sqlalchemy import (Boolean, Date, DateTime, Enum, Float, ForeignKey,
                        Integer, String, UniqueConstraint, func)
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym

from core.models.enums import Presentacion, TipoMovimiento
from core.models.rol import Rol
from infrastructure.db import Base

# ==============================================================
#  Medicamento
# ==============================================================


class MedicamentoSQL(Base):
    __tablename__ = "medicamentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)

    codigo: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )  # código interno
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)  # analgésico, etc.

    principio_activo: Mapped[str] = mapped_column(String(120), nullable=False)
    laboratorio: Mapped[str | None] = mapped_column(String(120))
    presentacion: Mapped[Presentacion] = mapped_column(
        Enum(Presentacion), nullable=False
    )

    concentracion: Mapped[str | None] = mapped_column(String(50))  # 500 mg
    forma_farmaceutica: Mapped[str | None] = mapped_column(
        String(50)
    )  # cápsula, jarabe…
    via_administracion: Mapped[str | None] = mapped_column(String(50))  # oral, tópica…
    indicaciones: Mapped[str | None] = mapped_column(String(255))
    contraindicaciones: Mapped[str | None] = mapped_column(String(255))
    condiciones_almacenamiento: Mapped[str | None] = mapped_column(String(255))
    imagen_url: Mapped[str | None] = mapped_column(String(255))  # URL opcional

    precio_venta: Mapped[float] = mapped_column(Float, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # 1-N
    lotes: Mapped[list["LoteSQL"]] = relationship(back_populates="medicamento")


# ==============================================================
#  Lote
# ==============================================================


class LoteSQL(Base):
    __tablename__ = "lotes"
    __table_args__ = (UniqueConstraint("codigo"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(50), nullable=False)

    medicamento_id: Mapped[int] = mapped_column(
        ForeignKey("medicamentos.id", ondelete="CASCADE"), nullable=False
    )

    fecha_vencimiento: Mapped[date] = mapped_column(Date, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)  # puede ser 0
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    medicamento: Mapped["MedicamentoSQL"] = relationship(back_populates="lotes")
    movimientos: Mapped[list["MovimientoSQL"]] = relationship(back_populates="lote")


# ==============================================================
#  Movimiento
# ==============================================================


class MovimientoSQL(Base):
    __tablename__ = "movimientos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lote_id: Mapped[int] = mapped_column(
        ForeignKey("lotes.id", ondelete="CASCADE"), nullable=False
    )

    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)

    tipo: Mapped[TipoMovimiento] = mapped_column(Enum(TipoMovimiento), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    motivo: Mapped[str] = mapped_column(String(120), nullable=False)

    creado_en: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    lote: Mapped["LoteSQL"] = relationship(back_populates="movimientos")
    usuario: Mapped["UsuarioSQL"] = relationship()


# ==============================================================
#  Usuario
# ==============================================================


class UsuarioSQL(Base):
    __tablename__ = "usuarios"

    __table_args__ = (
        UniqueConstraint("username"),
        # Sólo caracteres alfanuméricos (SQLite usa GLOB; en PostgreSQL sería ~)
        CheckConstraint(
            "username GLOB '[A-Za-z0-9]*'",
            name="chk_username_alnum",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Username: único, alfanumérico (valida también a nivel app vía Pydantic)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    nombre_completo: Mapped[str] = mapped_column(String(120), nullable=False)
    dni: Mapped[Optional[str]] = mapped_column(String(12), unique=True)

    # Password ya viene hasheada (bcrypt, Argon2…)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    password = synonym("password_hash")

    # Datos de contacto
    email: Mapped[str] = mapped_column(String(120), nullable=False)
    celular: Mapped[str] = mapped_column(String(15), nullable=False)
    direccion: Mapped[str] = mapped_column(String(255), nullable=False)

    # Rol y estado
    rol: Mapped[Rol] = mapped_column(Enum(Rol), nullable=False, default=Rol.CAJERO)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    creado_en: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
