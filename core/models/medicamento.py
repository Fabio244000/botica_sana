from datetime import datetime

from pydantic import BaseModel, Field, PositiveFloat

from .enums import Presentacion


class Medicamento(BaseModel):
    """Entidad de dominio: descripción básica del producto."""

    id: int | None = Field(default=None)  # asignado por la BD
    nombre: str = Field(min_length=3, max_length=120)
    principio_activo: str = Field(min_length=2, max_length=120)
    laboratorio: str | None = Field(default=None, max_length=120)
    presentacion: Presentacion
    precio_venta: PositiveFloat
    creado_en: datetime = Field(default_factory=datetime.utcnow)
