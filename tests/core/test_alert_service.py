from datetime import date, timedelta

import pytest

from core.models.lote import Lote
from core.ports.repository_port import RepositoryPort
from core.services.alert_service import AlertService


# ————————————————————————————————————————————————————————————————
#   Repositorio en memoria especializado para Lote
# ————————————————————————————————————————————————————————————————
class InMemoryLoteRepo(RepositoryPort[Lote]):
    def __init__(self) -> None:
        self._db: dict[int, Lote] = {}
        self._pk: int = 1

    def add(self, entity: Lote) -> Lote:
        entity.id = self._pk
        self._db[self._pk] = entity
        self._pk += 1
        return entity

    def get(self, entity_id: int):
        return self._db.get(entity_id)

    def list(self):
        return self._db.values()


# ————————————————————————————————————————————————————————————————
#   Fixture con datos de prueba
# ————————————————————————————————————————————————————————————————
@pytest.fixture
def alerta():
    repo = InMemoryLoteRepo()
    hoy = date.today()

    repo.add(
        Lote(
            codigo="L01",  # 3 caracteres
            medicamento_id=1,
            fecha_vencimiento=hoy + timedelta(days=10),
            stock=2,
        )
    )
    repo.add(
        Lote(
            codigo="L02",
            medicamento_id=2,
            fecha_vencimiento=hoy + timedelta(days=5),
            stock=50,
        )
    )
    repo.add(
        Lote(
            codigo="L03",
            medicamento_id=3,
            fecha_vencimiento=hoy + timedelta(days=90),
            stock=1,
        )
    )
    repo.add(
        Lote(
            codigo="L04",
            medicamento_id=4,
            fecha_vencimiento=hoy + timedelta(days=120),
            stock=100,
        )
    )

    return AlertService(repo)


# ————————————————————————————————————————————————————————————————
#   Tests de stock mínimo
# ————————————————————————————————————————————————————————————————
def test_stock_minimo(alerta):
    assert {l.codigo for l in alerta.stock_minimo(5)} == {"L01", "L03"}


def test_stock_minimo_umbral_exacto(alerta):
    exact = list(alerta.stock_minimo(umbral=2))
    assert {l.codigo for l in exact} == {"L01", "L03"}


# ————————————————————————————————————————————————————————————————
#   Tests de caducidad
# ————————————————————————————————————————————————————————————————
def test_por_vencer_30_dias(alerta):
    assert {l.codigo for l in alerta.por_vencer()} == {"L01", "L02"}


def test_por_vencer_7_dias(alerta):
    assert {l.codigo for l in alerta.por_vencer(dias=7)} == {"L02"}


# ————————————————————————————————————————————————————————————————
#   Lote que cumple ambas condiciones
# ————————————————————————————————————————————————————————————————
def test_lote_cumple_ambas_condiciones(alerta):
    low = {l.codigo for l in alerta.stock_minimo(5)}
    soon = {l.codigo for l in alerta.por_vencer()}
    assert low & soon == {"L01"}
