import pytest

from core.decorators.security import requires_role
from core.models.usuario import Rol, Usuario
from infrastructure.auth_context import set_current_user

# hash ficticio de 60 caracteres
HASH = "x" * 60


@requires_role(Rol.ADMIN)
def admin_only():
    return "OK"


def test_pass_when_role_matches():
    set_current_user(Usuario(id=1, username="adm", password_hash=HASH, rol=Rol.ADMIN))
    assert admin_only() == "OK"


def test_fail_when_not_logged():
    set_current_user(None)
    with pytest.raises(PermissionError):
        admin_only()


def test_fail_when_wrong_role():
    set_current_user(Usuario(id=2, username="usr", password_hash=HASH, rol=Rol.CAJERO))
    with pytest.raises(PermissionError):
        admin_only()
