from datetime import date, timedelta

import pytest

from core.models.lote import Lote
from core.models.movimiento import Movimiento, TipoMovimiento
from core.ports.repository_port import RepositoryPort
from core.services.inventory_service import InventoryService


# ————————————————————————————————————————————————————————————————
#   Repos en memoria
# ————————————————————————————————————————————————————————————————
class InMemoryRepo(RepositoryPort):
    def __init__(self):
        self._db: dict[int, object] = {}
        self._pk = 1

    def add(self, entity):
        entity.id = self._pk
        self._db[self._pk] = entity
        self._pk += 1
        return entity

    def get(self, entity_id: int):
        return self._db.get(entity_id)

    def list(self):
        return self._db.values()


# ————————————————————————————————————————————————————————————————
#   FIFO selector dummy que elige el lote con fecha de vencimiento + id más antiguo
# ————————————————————————————————————————————————————————————————
class SimpleFIFO:
    def __init__(self, lote_repo: RepositoryPort[Lote]) -> None:
        self._repo = lote_repo

    def next_lote(self, medicamento_id: int) -> Lote | None:
        # seleccionar el lote más antiguo (menor fecha_venc y luego id)
        lotes = [
            l
            for l in self._repo.list()
            if l.medicamento_id == medicamento_id and l.stock > 0
        ]
        lotes.sort(key=lambda l: (l.fecha_vencimiento, l.id))
        return lotes[0] if lotes else None


# ————————————————————————————————————————————————————————————————
#   Fixture que provee InventoryService limpio por test
# ————————————————————————————————————————————————————————————————
@pytest.fixture
def inventory():
    lote_repo = InMemoryRepo()
    mov_repo = InMemoryRepo()
    fifo = SimpleFIFO(lote_repo)
    return InventoryService(lote_repo, mov_repo, fifo), lote_repo, mov_repo


# ————————————————————————————————————————————————————————————————
#   1. Prueba de entrada
# ————————————————————————————————————————————————————————————————
def test_entrada_movimiento(inventory):
    inv, lote_repo, mov_repo = inventory

    lote = lote_repo.add(
        Lote(
            codigo="LOT001",
            medicamento_id=1,
            fecha_vencimiento=date.today() + timedelta(days=90),
            stock=1,  # ← debe ser > 0 para PositiveInt
        )
    )
    mv = inv.entrada(lote, cantidad=10, motivo="compra")

    assert mv.tipo == TipoMovimiento.ENTRADA
    assert lote.stock == 11  # 1 (inicial) + 10 (entrada)

    # movimiento quedó persistido
    assert isinstance(mov_repo.get(mv.id), Movimiento)


# ————————————————————————————————————————————————————————————————
#   2. Salida FIFO consume lote más antiguo
# ————————————————————————————————————————————————————————————————
def test_salida_fifo(inventory):
    inv, lote_repo, _ = inventory
    hoy = date.today()

    # Lote A (vence antes)
    lote_a = lote_repo.add(
        Lote(
            codigo="LOT-A",
            medicamento_id=1,
            fecha_vencimiento=hoy + timedelta(days=30),
            stock=5,
        )
    )
    # Lote B (vence después)
    lote_b = lote_repo.add(
        Lote(
            codigo="LOT-B",
            medicamento_id=1,
            fecha_vencimiento=hoy + timedelta(days=60),
            stock=5,
        )
    )

    movimientos = inv.salida(medicamento_id=1, cantidad=7, motivo="venta")
    assert len(movimientos) == 2  # 2 lotes involucrados
    assert movimientos[0].lote_id == lote_a.id  # FIFO: primero el más antiguo
    assert movimientos[0].cantidad == 5
    assert movimientos[1].lote_id == lote_b.id
    assert movimientos[1].cantidad == 2
    # stocks actualizados
    assert lote_a.stock == 0
    assert lote_b.stock == 3


# ————————————————————————————————————————————————————————————————
#   3. Salida con stock insuficiente
# ————————————————————————————————————————————————————————————————
def test_salida_insuficiente_levanta_error(inventory):
    inv, lote_repo, _ = inventory
    lote_repo.add(
        Lote(
            codigo="LOT-X",
            medicamento_id=2,
            fecha_vencimiento=date.today() + timedelta(days=100),
            stock=3,
        )
    )
    with pytest.raises(ValueError):
        inv.salida(medicamento_id=2, cantidad=10, motivo="venta")
