import hashlib

import pytest

from core.models.usuario import Usuario
from core.ports.hash_port import HashPort
from core.ports.repository_port import RepositoryPort
from core.services.auth_service import AuthService


# ————————————————————————————————————————————————————————————————
#   Repo de usuarios en memoria
# ————————————————————————————————————————————————————————————————
class InMemoryUserRepo(RepositoryPort[Usuario]):
    def __init__(self) -> None:
        self._db: dict[int, Usuario] = {}
        self._pk = 1

    def add(self, entity: Usuario) -> Usuario:
        entity.id = self._pk
        self._db[self._pk] = entity
        self._pk += 1
        return entity

    def get(self, entity_id: int):
        return self._db.get(entity_id)

    def list(self):
        return self._db.values()


# ————————————————————————————————————————————————————————————————
#   Hash dummy (determinista)
# ————————————————————————————————————————————————————————————————
class DummyHash(HashPort):
    def hash(self, plain: str) -> str:
        # Hash SHA-256 (64 hex chars) → cumple longitud mínima
        return hashlib.sha256(plain.encode()).hexdigest()

    def verify(self, plain: str, hashed: str) -> bool:
        return hashed == self.hash(plain)


# ————————————————————————————————————————————————————————————————
#   Fixture AuthService con dependencias fake
# ————————————————————————————————————————————————————————————————
@pytest.fixture
def auth():
    return AuthService(InMemoryUserRepo(), DummyHash())


# ————————————————————————————————————————————————————————————————
#   1. Crear usuario
# ————————————————————————————————————————————————————————————————
def test_create_user(auth):
    user = auth.create_user("fabio", "1234", "admin")
    assert user.id == 1
    assert len(user.password_hash) == 64
    assert user.rol == "admin"


# ————————————————————————————————————————————————————————————————
#   2. Login exitoso
# ————————————————————————————————————————————————————————————————
def test_login_success(auth):
    auth.create_user("ana", "pass", "cajero")
    assert auth.login("ana", "pass") is True


# ————————————————————————————————————————————————————————————————
#   3. Login fallido (usuario o password incorrectos)
# ————————————————————————————————————————————————————————————————
def test_login_failure_wrong_password(auth):
    auth.create_user("luis", "abcd", "cajero")
    assert auth.login("luis", "xxxx") is False


def test_login_failure_user_not_found(auth):
    assert auth.login("ghost", "123") is False


# ————————————————————————————————————————————————————————————————
#   4. Usuario inactivo
# ————————————————————————————————————————————————————————————————
def test_login_inactivo(auth):
    u = auth.create_user("maria", "1111", "auditor")
    u.activo = False
    auth._repo.add(u)  # persiste cambio
    assert auth.login("maria", "1111") is False


# ————————————————————————————————————————————————————————————————
#   5. Cambio de contraseña
# ————————————————————————————————————————————————————————————————
def test_change_password(auth):
    user = auth.create_user("pablo", "old", "cajero")

    updated = auth.change_password(user.id, "new")

    # ✅ compara con el hash que realmente genera el adapter
    assert updated.password_hash == auth._hash.hash("new")

    # ⬇️  el resto sigue igual
    assert auth.login("pablo", "new") is True
