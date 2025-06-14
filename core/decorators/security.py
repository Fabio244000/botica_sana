import functools
from typing import Callable

from core.models.rol import Rol
from infrastructure.auth_context import get_current_user


def requires_role(*roles: Rol):
    """
    Decorador: garantiza que el usuario actual tenga uno de los
    roles indicados.  Si no, lanza PermissionError.
    """
    allowed = set(roles)

    def decorator(fn: Callable):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if user is None:
                raise PermissionError("No autenticado")
            if user.rol not in allowed:
                raise PermissionError("Permiso denegado")
            return fn(*args, **kwargs)

        return wrapper

    return decorator
