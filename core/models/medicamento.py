from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, PositiveFloat

from .enums import Presentacion


class Medicamento(BaseModel):
    """Entidad de dominio: descripción detallada del medicamento."""

    # --- Identificación ---
    id: Optional[int] = Field(default=None)  # asignado por la BD
    nombre: str = Field(min_length=3, max_length=120)
    codigo: str = Field(min_length=3, max_length=50)  # código interno / catálogo
    tipo: str = Field(min_length=3, max_length=50)  # analgésico, antibiótico, etc.

    # --- Composición y presentación ---
    principio_activo: str = Field(min_length=2, max_length=120)
    laboratorio: Optional[str] = Field(default=None, max_length=120)
    presentacion: Presentacion
    concentracion: Optional[str] = Field(default=None, max_length=50)  # 500 mg
    forma_farmaceutica: Optional[str] = Field(
        default=None, max_length=50
    )  # cápsula, jarabe…
    via_administracion: Optional[str] = Field(
        default=None, max_length=50
    )  # oral, tópica…

    # --- Información clínica ---
    indicaciones: Optional[str] = Field(default=None, max_length=255)
    contraindicaciones: Optional[str] = Field(default=None, max_length=255)

    # --- Logística ---
    condiciones_almacenamiento: Optional[str] = Field(
        default=None, max_length=255
    )  # conservar en frío
    imagen_url: Optional[str] = None

    # --- Comercio ---
    precio_venta: PositiveFloat

    # --- Metadatos ---
    creado_en: datetime = Field(default_factory=datetime.utcnow)
