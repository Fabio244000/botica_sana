from datetime import date, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.models.lote import Lote
from core.services.inventory_service import FIFOSelector, InventoryService
from infrastructure.db import Base
from infrastructure.repos import LoteRepo, MovimientoRepo


def _session():
    eng = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=eng)
    return sessionmaker(bind=eng, expire_on_commit=False, future=True)()


def test_fifo_stock_consistency():
    db = _session()
    lote_repo = LoteRepo(db)
    mov_repo = MovimientoRepo(db)

    lote = lote_repo.add(
        Lote(
            codigo="FIFO",
            medicamento_id=1,
            fecha_vencimiento=date.today() + timedelta(days=30),
            stock=10,
        )
    )
    inv = InventoryService(lote_repo, mov_repo, FIFOSelector(lote_repo))

    inv.salida(1, 4, "venta")

    lote = lote_repo.get(lote.id)

    inv.entrada(lote, 6, "compra")

    assert lote_repo.get(lote.id).stock == 12  # 10 - 4 + 6
    assert len(list(mov_repo.list())) == 2
