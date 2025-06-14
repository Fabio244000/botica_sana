import pytest

from core.services.auth_service import AuthService
from infrastructure.db import Base, SessionLocal, engine
from infrastructure.hash_bcrypt import BcryptHashAdapter
from infrastructure.models import *  # noqa
from infrastructure.repos import UsuarioRepo


def setup_module():
    Base.metadata.create_all(bind=engine)


def teardown_module():
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def auth():
    user_repo = UsuarioRepo(SessionLocal())
    hasher = BcryptHashAdapter()
    return AuthService(user_repo, hasher)


def test_create_and_login(auth):
    user = auth.create_user("eva", "secret", "admin")
    assert user.id is not None
    assert auth.login("eva", "secret") is True


def test_change_password(auth):
    u = auth.create_user("leo", "oldpwd", "cajero")
    auth.change_password(u.id, "newpwd")
    assert auth.login("leo", "newpwd") is True
