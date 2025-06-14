from datetime import date, datetime

from pydantic import BaseModel, Field, NonNegativeInt, PositiveInt


class Lote(BaseModel):
    """Lote de un medicamento; usado para caducidad y FIFO."""

    id: int | None = None
    codigo: str = Field(min_length=3, max_length=50)
    medicamento_id: PositiveInt
    fecha_vencimiento: date
    stock: NonNegativeInt
    creado_en: datetime = Field(default_factory=datetime.utcnow)
