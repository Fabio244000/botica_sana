from datetime import date, timedelta

from core.models import Lote, Medicamento, Movimiento, TipoMovimiento
from infrastructure.db import Base, SessionLocal, engine
from infrastructure.models import *  # noqa
from infrastructure.repos import LoteRepo, MedicamentoRepo, MovimientoRepo


def setup_module():
    Base.metadata.create_all(bind=engine)


def teardown_module():
    Base.metadata.drop_all(bind=engine)


def test_movimiento_roundtrip():
    db = SessionLocal()
    med_repo = MedicamentoRepo(db)
    lote_repo = LoteRepo(db)
    mov_repo = MovimientoRepo(db)

    med = med_repo.add(
        Medicamento(
            nombre="Aspirina",
            principio_activo="Ácido acetilsalicílico",
            presentacion="tableta",
            precio_venta=1.5,
        )
    )
    lote = lote_repo.add(
        Lote(
            codigo="LOT900",
            medicamento_id=med.id,
            fecha_vencimiento=date.today() + timedelta(days=365),
            stock=100,
        )
    )
    mv = mov_repo.add(
        Movimiento(
            lote_id=lote.id,
            tipo=TipoMovimiento.SALIDA,
            cantidad=5,
            motivo="venta",
        )
    )
    assert mov_repo.get(mv.id).cantidad == 5
    assert len(list(mov_repo.list())) == 1
