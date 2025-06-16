import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, SecretStr, constr, validator

from .rol import Rol

# ⬇⬇  CAMBIO:  regex → pattern  ⬇⬇
CelularStr = constr(min_length=6, max_length=15, pattern=r"^\+?\d{6,15}$")
UsernameStr = constr(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9]+$")


class Usuario(BaseModel):
    """Cuenta de usuario del sistema de botica."""

    id: Optional[int] = None
    username: UsernameStr
    nombre_completo: constr(min_length=3, max_length=120)
    dni: Optional[constr(min_length=1, max_length=12, pattern=r"^[A-Za-z0-9]*$")] = None

    password: SecretStr = Field(
        ..., description="Contraseña en texto plano; se cifrará antes de guardar."
    )

    email: EmailStr
    celular: CelularStr
    direccion: str = Field(min_length=5, max_length=255)

    rol: Rol = Rol.CAJERO
    activo: bool = True
    creado_en: datetime = Field(default_factory=datetime.utcnow)

    # Validación de complejidad
    @validator("password")
    def validar_password(cls, v: SecretStr) -> SecretStr:
        pwd = v.get_secret_value()
        if (
            len(pwd) < 8
            or not re.search(r"[A-Z]", pwd)
            or not re.search(r"[a-z]", pwd)
            or not re.search(r"\d", pwd)
            or not re.search(r"[^\w]", pwd)
        ):
            raise ValueError(
                "La contraseña debe tener al menos 8 caracteres y contener "
                "mayúsculas, minúsculas, números y símbolos."
            )
        return v
