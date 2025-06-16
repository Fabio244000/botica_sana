from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, NonNegativeInt, PositiveInt


class Lote(BaseModel):
    """Lote de un medicamento (control de caducidad, FIFO)."""

    id: Optional[int] = None
    codigo: str = Field(min_length=3, max_length=50)
    medicamento_id: PositiveInt
    fecha_vencimiento: date
    stock: NonNegativeInt  # puede ser 0 al ingresar el producto
    creado_en: datetime = Field(default_factory=datetime.utcnow)
