from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ─────────────────── App metadata ───────────────────
    app_name: str = "Botica Sana"
    env: Literal["dev", "prod"] = "dev"

    # ─────────────────── Database ────────────────────────
    # SQLite para desarrollo; PostgreSQL para producción.
    sqlite_path: Path = Path(__file__).resolve().parent.parent / "botica.db"
    pg_host: str = "localhost"
    pg_port: int = 5432
    pg_db: str = "botica"
    pg_user: str = "botica_user"
    pg_password: str = "botica_pass"

    # ─────────────────── Inventario ──────────────────────
    stock_min_threshold: PositiveInt = Field(5, description="Stock bajo alerta")
    caducidad_dias: PositiveInt = Field(30, description="Días antes de vencer")

    # ─────────────────── Métodos utilitarios ─────────────
    @property
    def sqlalchemy_url(self) -> str:
        """Devuelve la URL adecuada según el entorno."""
        if self.env == "dev":
            return f"sqlite:///{self.sqlite_path}"
        return (
            "postgresql+psycopg2://"
            f"{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_db}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Para que Path se tome de env vars tipo str
        arbitrary_types_allowed = True


# Singleton – una sola instancia durante el proceso
@lru_cache(maxsize=1)
def get_settings() -> Settings:  # pragma: no cover
    return Settings()
