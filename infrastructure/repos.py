from typing import Iterable

from sqlalchemy.orm import Session

from core.models.lote import Lote
from core.models.medicamento import Medicamento
from core.models.movimiento import Movimiento
from core.models.usuario import Usuario
from core.ports.repository_port import RepositoryPort
from infrastructure.db import SessionLocal
from infrastructure.models import (LoteSQL, MedicamentoSQL, MovimientoSQL,
                                   UsuarioSQL)


# ——— Helper ————————————————————————————————————————————————
def as_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


# ——— Medicamento repo ——————————————————————————————————————
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
        return (Movimiento(**as_dict(m)) for m in self._db.query(MovimientoSQL).all())

    def delete(self, entity_id: int) -> None:
        obj = self._db.get(MedicamentoSQL, entity_id)
        if obj:
            self._db.delete(obj)
            self._db.commit()


# ——— Lote repo ————————————————————————————————————————————
class LoteRepo(RepositoryPort[Lote]):
    def __init__(self, db: Session | None = None):
        self._db = db or SessionLocal()

    def add(self, entity: Lote) -> Lote:
        """
        • Si entity.id es None  → INSERT
        • Si entity.id existe   → UPDATE
        """
        if entity.id is None:  # ---------- INSERT ----------
            sql = LoteSQL(**entity.model_dump(exclude={"id"}))
            self._db.add(sql)
        else:  # ---------- UPDATE ----------
            sql = self._db.get(LoteSQL, entity.id)
            if not sql:  # id inexistente → insert
                sql = LoteSQL(**entity.model_dump(exclude={"id"}))
                self._db.add(sql)
            else:  # copiar campos que cambian
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
        """Insertar nuevo o actualizar existente."""
        if entity.id is None:  # ---------- INSERT ----------
            sql = UsuarioSQL(**entity.model_dump(exclude={"id"}))
            self._db.add(sql)
        else:  # ---------- UPDATE ----------
            sql = self._db.get(UsuarioSQL, entity.id)
            if not sql:  # id no existe → insertar
                sql = UsuarioSQL(**entity.model_dump(exclude={"id"}))
                self._db.add(sql)
            else:  # copiar campos modificados
                for k, v in entity.model_dump(exclude={"id"}).items():
                    setattr(sql, k, v)
        self._db.commit()
        self._db.refresh(sql)
        return Usuario(**as_dict(sql))

    def get(self, entity_id: int) -> Usuario | None:
        sql = self._db.get(UsuarioSQL, entity_id)
        return Usuario(**as_dict(sql)) if sql else None

    def list(self) -> Iterable[Usuario]:
        return (Usuario(**as_dict(u)) for u in self._db.query(UsuarioSQL).all())

    def delete(self, entity_id: int) -> None:
        obj = self._db.get(UsuarioSQL, entity_id)
        if obj:
            self._db.delete(obj)
            self._db.commit()


class MedicamentoRepo(RepositoryPort[Medicamento]):
    def __init__(self, db: Session | None = None):
        self._db = db or SessionLocal()

    def add(self, entity: Medicamento) -> Medicamento:
        sql = MedicamentoSQL(**entity.model_dump(exclude={"id"}))
        self._db.add(sql)
        self._db.commit()
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
