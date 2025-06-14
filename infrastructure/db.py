from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker

from infrastructure.settings import get_settings

settings = get_settings()

# Engine (SQLite por defecto)
engine = create_engine(settings.sqlalchemy_url, echo=False, future=True)

# Declarative base


class Base(DeclarativeBase): ...


# Session factory (scoped para threads/GUI)
SessionLocal = scoped_session(
    sessionmaker(bind=engine, expire_on_commit=False, autoflush=False, future=True)
)
