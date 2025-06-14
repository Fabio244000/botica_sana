from datetime import datetime

from pydantic import BaseModel, Field, PositiveInt

from .enums import TipoMovimiento


class Movimiento(BaseModel):
    """Entrada o salida de inventario."""

    id: int | None = None
    lote_id: PositiveInt
    tipo: TipoMovimiento
    cantidad: PositiveInt
    motivo: str = Field(max_length=120)
    creado_en: datetime = Field(default_factory=datetime.utcnow)
