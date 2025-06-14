from datetime import datetime, timedelta

import pydantic
import pytest

from core.models.rol import Rol
from core.models.usuario import Usuario


# ————————————————————————————————————————————————————————————————
#   1. Creación válida
# ————————————————————————————————————————————————————————————————
def test_usuario_valido() -> None:
    user = Usuario(
        username="fabio",
        password_hash="X" * 60,  # hash de longitud mínima
    )
    assert user.id is None
    assert user.username == "fabio"
    assert user.rol == Rol.CAJERO  # valor por defecto
    assert user.activo is True  # valor por defecto
    assert datetime.utcnow() - user.creado_en < timedelta(seconds=5)


# ————————————————————————————————————————————————————————————————
#   2. Username < 3 caracteres
# ————————————————————————————————————————————————————————————————
@pytest.mark.parametrize("uname", ["", "ab", "a" * 51])
def test_username_longitud(uname) -> None:
    with pytest.raises(pydantic.ValidationError):
        Usuario(
            username=uname,
            password_hash="H" * 60,
        )


# ————————————————————————————————————————————————————————————————
#   3. Password hash longitud inválida (< 60 o > 128)
# ————————————————————————————————————————————————————————————————
@pytest.mark.parametrize("phash", ["H" * 59, "H" * 129])
def test_password_hash_longitud(phash) -> None:
    with pytest.raises(pydantic.ValidationError):
        Usuario(
            username="usuario_ok",
            password_hash=phash,
        )


# ————————————————————————————————————————————————————————————————
#   4. Rol inválido
# ————————————————————————————————————————————————————————————————
def test_rol_invalido() -> None:
    with pytest.raises(pydantic.ValidationError):
        Usuario(
            username="fabio",
            password_hash="Y" * 60,
            rol="superuser",  # no existe en enum Rol
        )
