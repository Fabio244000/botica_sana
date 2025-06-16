from typing import Iterable, List, Mapping, Tuple

from pydantic import SecretStr
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.models.lote import Lote
from core.models.medicamento import Medicamento
from core.models.movimiento import Movimiento
from core.models.usuario import Usuario
from core.ports.repository_port import RepositoryPort
from infrastructure.db import SessionLocal
from infrastructure.models import (LoteSQL, MedicamentoSQL, MovimientoSQL,
                                   UsuarioSQL)


def as_dict(obj):
    """Convierte un modelo SQLAlchemy a dict plano."""
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


class MovimientoRepo(RepositoryPort[Movimiento]):
    def __init__(self, db: Session | None = None):
        self._db = db or SessionLocal()

    def add(self, entity: Movimiento) -> Movimiento:
        sql = MovimientoSQL(**entity.model_dump(exclude={"id"}))
        self._db.add(sql)
        self._db.commit()
        self._db.refresh(sql)
        return Movimiento(**as_dict(sql))

    def get(self, entity_id: int) -> Movimiento | None:
        sql = self._db.get(MovimientoSQL, entity_id)
        return Movimiento(**as_dict(sql)) if sql else None

    def list(self) -> Iterable[Movimiento]:
        rows = (
            self._db.query(MovimientoSQL).order_by(MovimientoSQL.creado_en.desc()).all()
        )
        return (Movimiento(**as_dict(m)) for m in rows)

    def delete(self, entity_id: int) -> None:
        obj = self._db.get(MovimientoSQL, entity_id)
        if obj:
            self._db.delete(obj)
            self._db.commit()

    def list_recent(self, limit: int = 100) -> Iterable[Movimiento]:
        rows = (
            self._db.query(MovimientoSQL)
            .order_by(MovimientoSQL.creado_en.desc())
            .limit(limit)
            .all()
        )
        return (Movimiento(**as_dict(m)) for m in rows)


class LoteRepo(RepositoryPort[Lote]):
    def __init__(self, db: Session | None = None):
        self._db = db or SessionLocal()

    def add(self, entity: Lote) -> Lote:
        if entity.id is None:
            sql = LoteSQL(**entity.model_dump(exclude={"id"}))
            self._db.add(sql)
        else:
            sql = self._db.get(LoteSQL, entity.id)
            if not sql:
                sql = LoteSQL(**entity.model_dump(exclude={"id"}))
                self._db.add(sql)
            else:
                for k, v in entity.model_dump(exclude={"id"}).items():
                    setattr(sql, k, v)
        self._db.commit()
        self._db.refresh(sql)
        return Lote(**as_dict(sql))

    def get(self, entity_id: int) -> Lote | None:
        sql = self._db.get(LoteSQL, entity_id)
        return Lote(**as_dict(sql)) if sql else None

    def list(self) -> Iterable[Lote]:
        return (Lote(**as_dict(l)) for l in self._db.query(LoteSQL).all())

    def delete(self, entity_id: int) -> None:
        obj = self._db.get(LoteSQL, entity_id)
        if obj:
            self._db.delete(obj)
            self._db.commit()


class UsuarioRepo(RepositoryPort[Usuario]):
    def __init__(self, db: Session | None = None):
        self._db = db or SessionLocal()

    def add(self, entity: Usuario) -> Usuario:
        # Preparamos dict excluyendo id y desenrollamos SecretStr
        data = entity.model_dump(exclude={"id"})
        for k, v in data.items():
            if isinstance(v, SecretStr):
                data[k] = v.get_secret_value()

        if entity.id is None:
            sql = UsuarioSQL(**data)
            self._db.add(sql)
        else:
            sql = self._db.get(UsuarioSQL, entity.id)
            if not sql:
                sql = UsuarioSQL(**data)
                self._db.add(sql)
            else:
                for k, v in data.items():
                    setattr(sql, k, v)

        self._db.commit()
        self._db.refresh(sql)

        # Mapear password_hash de SQL a SecretStr password
        raw = as_dict(sql)
        raw["password"] = SecretStr(raw.pop("password_hash"))
        return Usuario(**raw)

    def get(self, entity_id: int) -> Usuario | None:
        sql = self._db.get(UsuarioSQL, entity_id)
        if not sql:
            return None
        raw = as_dict(sql)
        raw["password"] = SecretStr(raw.pop("password_hash"))
        return Usuario(**raw)

    def list(self) -> Iterable[Usuario]:
        for u in self._db.query(UsuarioSQL).all():
            raw = as_dict(u)
            raw["password"] = SecretStr(raw.pop("password_hash"))
            yield Usuario(**raw)

    def delete(self, entity_id: int) -> None:
        obj = self._db.get(UsuarioSQL, entity_id)
        if obj:
            self._db.delete(obj)
            self._db.commit()


class MedicamentoRepo(RepositoryPort[Medicamento]):
    def __init__(self, db: Session | None = None):
        self._db = db or SessionLocal()

    def add(self, entity: Medicamento) -> Medicamento:
        data = entity.model_dump(exclude={"id"})
        if entity.id is None:
            sql = MedicamentoSQL(**data)
            self._db.add(sql)
        else:
            sql = self._db.get(MedicamentoSQL, entity.id)
            if not sql:
                sql = MedicamentoSQL(**data)
                self._db.add(sql)
            else:
                for k, v in data.items():
                    setattr(sql, k, v)
        try:
            self._db.commit()
        except IntegrityError:
            self._db.rollback()
            raise ValueError("El código ya está registrado")
        self._db.refresh(sql)
        return Medicamento(**as_dict(sql))

    def get(self, entity_id: int) -> Medicamento | None:
        sql = self._db.get(MedicamentoSQL, entity_id)
        return Medicamento(**as_dict(sql)) if sql else None

    def list(self) -> Iterable[Medicamento]:
        return (Medicamento(**as_dict(m)) for m in self._db.query(MedicamentoSQL).all())

    def delete(self, entity_id: int) -> None:
        obj = self._db.get(MedicamentoSQL, entity_id)
        if obj:
            self._db.delete(obj)
            self._db.commit()

    def list_paginated(
        self,
        limit: int,
        offset: int = 0,
        filters: Mapping[str, object] | None = None,
    ) -> Tuple[List[Medicamento], int]:
        query = self._db.query(MedicamentoSQL)
        if filters:
            if text := filters.get("nombre_codigo"):
                pattern = f"%{text}%"
                query = query.filter(
                    MedicamentoSQL.nombre.ilike(pattern)
                    | MedicamentoSQL.codigo.ilike(pattern)
                )
            if lab := filters.get("laboratorio"):
                query = query.filter(MedicamentoSQL.laboratorio == lab)
            if typ := filters.get("tipo"):
                query = query.filter(MedicamentoSQL.tipo == typ)
        total = query.with_entities(func.count()).scalar() or 0
        items_sql = (
            query.order_by(MedicamentoSQL.creado_en.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        items = [Medicamento(**as_dict(m)) for m in items_sql]
        return items, total
