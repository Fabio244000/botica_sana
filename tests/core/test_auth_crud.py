import pytest

from core.models.usuario import Rol, Usuario
from core.ports.hash_port import HashPort
from core.ports.repository_port import RepositoryPort
from core.services.auth_service import AuthService


class DummyHash(HashPort):
    def hash(self, pwd):
        # genera un hash ficticio de 60 caracteres
        return ("H-" + pwd).ljust(60, "_")

    def verify(self, pwd, h):
        return h == ("H-" + pwd).ljust(60, "_")


class InMemRepo(RepositoryPort[Usuario]):
    def __init__(self):
        self._db, self._pk = {}, 1

    def add(self, u):
        if u.id is None:
            u.id = self._pk
            self._pk += 1
        self._db[u.id] = u
        return u

    def get(self, i):
        return self._db.get(i)

    def list(self):
        return self._db.values()

    def delete(self, i):
        self._db.pop(i, None)


@pytest.fixture
def svc():
    return AuthService(InMemRepo(), DummyHash())


def test_create_and_list(svc):
    svc.create_user("admin", "123", Rol.ADMIN)
    users = svc.list_users()
    assert len(users) == 1 and users[0].username == "admin"


def test_set_active(svc):
    u = svc.create_user("user", "x", Rol.CAJERO)
    svc.set_active(u.id, False)
    assert svc.list_users()[0].activo is False


def test_delete(svc):
    u = svc.create_user("tmp", "pw", Rol.CAJERO)
    svc.delete_user(u.id)
    assert svc.list_users() == []
