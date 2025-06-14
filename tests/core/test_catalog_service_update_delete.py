from core.models.enums import Presentacion
from core.models.medicamento import Medicamento
from core.ports.repository_port import RepositoryPort
from core.services.catalog_service import CatalogService


class InMemoryRepo(RepositoryPort[Medicamento]):
    def __init__(self):
        self._db: dict[int, Medicamento] = {}
        self._pk = 1

    def add(self, e: Medicamento) -> Medicamento:
        if e.id is None:
            e.id = self._pk
            self._pk += 1
        self._db[e.id] = e
        return e

    def get(self, i: int):
        return self._db.get(i)

    def list(self):
        return self._db.values()

    def delete(self, i: int):
        self._db.pop(i, None)


def test_update_and_delete():
    repo = InMemoryRepo()
    svc = CatalogService(repo)

    med = svc.add(
        Medicamento(
            nombre="Paracetamol",
            principio_activo="Acetaminofén",
            presentacion=Presentacion.TABLETA,
            precio_venta=2.5,
        )
    )

    # update
    updated = svc.update(med.id, {"precio_venta": 3.0})
    assert updated.precio_venta == 3.0

    # delete
    svc.delete(med.id)
    assert svc.get(med.id) is None
