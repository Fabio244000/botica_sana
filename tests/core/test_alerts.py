from datetime import date, timedelta

from core.models.lote import Lote
from core.ports.repository_port import RepositoryPort
from core.services.alert_service import AlertService


class InMem(RepositoryPort[Lote]):
    def __init__(self, lotes):
        self._lotes = lotes

    def list(self):
        return self._lotes

    def add(self, e): ...
    def get(self, _): ...
    def delete(self, _): ...


def test_alert_service():
    hoy = date.today()
    lotes = [
        Lote(
            codigo="LOT-A",
            medicamento_id=1,
            fecha_vencimiento=hoy + timedelta(days=2),
            stock=10,
        ),
        Lote(
            codigo="LOT-B",
            medicamento_id=1,
            fecha_vencimiento=hoy + timedelta(days=90),
            stock=1,
        ),
    ]
    svc = AlertService(InMem(lotes))
    res = svc.alertas(umbral=5, dias=30)
    assert len(res["vencimiento"]) == 1
    assert len(res["stock"]) == 1
