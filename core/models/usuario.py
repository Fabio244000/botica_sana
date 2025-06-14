from datetime import datetime

from pydantic import BaseModel, Field

from .rol import Rol


class Usuario(BaseModel):
    id: int | None = None
    username: str = Field(min_length=3, max_length=50)
    password_hash: str = Field(min_length=60, max_length=128)
    rol: Rol = Rol.CAJERO
    activo: bool = True
    creado_en: datetime = Field(default_factory=datetime.utcnow)
