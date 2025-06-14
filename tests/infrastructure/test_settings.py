from pathlib import Path

from infrastructure.settings import Settings, get_settings


def test_default_sqlite_url(tmp_path, monkeypatch):
    # asegúrate de usar env=dev
    monkeypatch.setenv("ENV", "dev")
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "test.db"))
    settings = Settings()
    assert settings.sqlalchemy_url.startswith("sqlite:///")
    assert Path(settings.sqlite_path).name == "test.db"


def test_postgres_url(monkeypatch):
    monkeypatch.setenv("ENV", "prod")
    monkeypatch.setenv("PG_HOST", "db.example.com")
    monkeypatch.setenv("PG_USER", "user")
    monkeypatch.setenv("PG_PASSWORD", "pwd")
    monkeypatch.setenv("PG_DB", "botica")
    settings = Settings()
    assert settings.sqlalchemy_url == (
        "postgresql+psycopg2://user:pwd@db.example.com:5432/botica"
    )


def test_singleton_cache(monkeypatch):
    # cambia una variable de entorno para forzar valores distintos
    monkeypatch.setenv("STOCK_MIN_THRESHOLD", "99")

    # limpia la caché del singleton
    get_settings.cache_clear()

    s1 = get_settings()
    s2 = get_settings()

    assert s1 is s2  # misma instancia
    assert s1.stock_min_threshold == 99
