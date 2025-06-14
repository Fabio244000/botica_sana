from datetime import datetime

import pytest

from core.decorators.security import requires_role
from core.models.usuario import Rol, Usuario
from core.ports.hash_port import HashPort
from core.ports.repository_port import RepositoryPort
from core.services.auth_service import AuthService
from infrastructure.auth_context import get_current_user, set_current_user

# ------------------------------------------------------------------
#  Helpers (hash y repo en memoria)
# ------------------------------------------------------------------
HASH60 = lambda s: ("H-" + s).ljust(60, "_")  # 60 chars


class DummyHash(HashPort):
    def hash(self, p):
        return HASH60(p)

    def verify(self, p, h):
        return h == HASH60(p)


class InMemRepo(RepositoryPort[Usuario]):
    def __init__(self):
        self._db = {}
        self._pk = 1

    def add(self, u):
        if u.id is None:
            u.id, self._pk = self._pk, self._pk + 1
        self._db[u.id] = u
        return u

    def get(self, i):
        return self._db.get(i)

    def list(self):
        return self._db.values()

    def delete(self, i):
        self._db.pop(i, None)


# ------------------------------------------------------------------
#  Servicio con 2 usuarios: admin activo / cajero inactivo
# ------------------------------------------------------------------


@pytest.fixture
def svc():
    repo = InMemRepo()
    s = AuthService(repo, DummyHash())
    s.create_user("admin", "123", Rol.ADMIN)
    caj = s.create_user("cajero", "abc", Rol.CAJERO)
    s.set_active(caj.id, False)  # lo deja inactivo
    return s


# ------------------------------------------------------------------
#  Decorado de ejemplo
# ------------------------------------------------------------------


@requires_role(Rol.ADMIN)
def accion_admin():
    return "OK"


# ------------------------------------------------------------------
#  Pruebas
# ------------------------------------------------------------------


def test_login_success_sets_context(svc):
    assert svc.login("admin", "123") is True
    assert get_current_user().username == "admin"


def test_login_wrong_password(svc):
    assert svc.login("admin", "999") is False
    assert get_current_user() is None


def test_login_inactive_user(svc):
    assert svc.login("cajero", "abc") is False
    assert get_current_user() is None


def test_requires_role_pass(svc):
    svc.login("admin", "123")
    assert accion_admin() == "OK"


def test_requires_role_denied(svc):
    # simula cajero activo
    set_current_user(
        Usuario(id=3, username="c01", password_hash=HASH60("x"), rol=Rol.CAJERO)
    )
    with pytest.raises(PermissionError):
        accion_admin()
