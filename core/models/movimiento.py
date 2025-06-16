from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, PositiveInt

from .enums import TipoMovimiento


class Movimiento(BaseModel):
    """Registro de entrada o salida de inventario."""

    id: Optional[int] = None
    lote_id: PositiveInt
    usuario_id: PositiveInt
    tipo: TipoMovimiento
    cantidad: PositiveInt
    motivo: str = Field(max_length=120)
    creado_en: datetime = Field(default_factory=datetime.utcnow)
