"""
Pequeño helper que guarda al usuario autenticado durante
la petición / thread / ejecución actual.
"""

from contextvars import ContextVar
from typing import Optional

from core.models.usuario import Usuario

_current_user: ContextVar[Optional[Usuario]] = ContextVar("_current_user", default=None)


def set_current_user(user: Optional[Usuario]) -> None:
    """Establece el usuario logueado (o None para limpiar)."""
    _current_user.set(user)


def get_current_user() -> Optional[Usuario]:
    """Devuelve el usuario actual o None si no hay sesión."""
    return _current_user.get()
