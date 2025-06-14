# tests/infrastructure/test_repos_inmemory.py
from datetime import date, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.models import (Lote, Medicamento, Movimiento, Presentacion,
                         TipoMovimiento, Usuario)
from infrastructure.db import Base
from infrastructure.hash_bcrypt import BcryptHasher
from infrastructure.repos import (LoteRepo, MedicamentoRepo, MovimientoRepo,
                                  UsuarioRepo)


def _memory_session():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, expire_on_commit=False, future=True)()


def test_repos_crud_roundtrip():
    db = _memory_session()

    med_repo = MedicamentoRepo(db)
    lote_repo = LoteRepo(db)
    mov_repo = MovimientoRepo(db)
    user_repo = UsuarioRepo(db)

    med = med_repo.add(
        Medicamento(
            nombre="Diclofenaco",
            principio_activo="Diclofenaco sódico",
            presentacion=Presentacion.TABLETA,
            precio_venta=4.0,
        )
    )
    lote = lote_repo.add(
        Lote(
            codigo="L100",
            medicamento_id=med.id,
            fecha_vencimiento=date.today() + timedelta(days=200),
            stock=20,
        )
    )
    mov_repo.add(
        Movimiento(
            lote_id=lote.id,
            tipo=TipoMovimiento.ENTRADA,
            cantidad=20,
            motivo="compra inicial",
        )
    )
    hasher = BcryptHasher()
    user = user_repo.add(
        Usuario(
            username="admin",
            password_hash=hasher.hash("secret"),
            rol="admin",
        )
    )

    # asserts rápidos
    assert med_repo.get(med.id).nombre == "Diclofenaco"
    assert lote_repo.get(lote.id).stock == 20
    assert len(list(mov_repo.list())) == 1
    assert user_repo.get(user.id).username == "admin"
