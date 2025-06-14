import pytest

from core.models.medicamento import Medicamento
from core.ports.repository_port import RepositoryPort
from core.services.catalog_service import CatalogService


# ————————————————————————————————————————————————————————————————
#   Repo en memoria reutilizable
# ————————————————————————————————————————————————————————————————
class InMemoryRepo(RepositoryPort[Medicamento]):
    _db: dict[int, Medicamento]
    _pk: int

    def __init__(self) -> None:
        self._db = {}
        self._pk = 1

    def add(self, entity: Medicamento) -> Medicamento:
        entity.id = self._pk
        self._db[self._pk] = entity
        self._pk += 1
        return entity

    def get(self, entity_id: int):
        return self._db.get(entity_id)

    def list(self):
        return self._db.values()


# ————————————————————————————————————————————————————————————————
#   Fixture: servicio con repo limpio por test
# ————————————————————————————————————————————————————————————————
@pytest.fixture
def catalog():
    repo = InMemoryRepo()
    service = CatalogService(repo)
    return service


# ————————————————————————————————————————————————————————————————
#   1. Alta y lectura básica (test existente)
# ————————————————————————————————————————————————————————————————
def test_catalog_add_and_get(catalog) -> None:
    med = Medicamento(
        nombre="Ibuprofeno",
        principio_activo="Ibuprofeno",
        presentacion="tableta",
        precio_venta=3.0,
    )
    saved = catalog.add(med)
    assert saved.id == 1

    found = catalog.get(1)
    assert found.nombre == "Ibuprofeno"


# ————————————————————————————————————————————————————————————————
#   2. Listado tras varias altas
# ————————————————————————————————————————————————————————————————
def test_catalog_list(catalog) -> None:
    medicamentos = [
        Medicamento(
            nombre="Paracetamol",
            principio_activo="Acetaminofén",
            presentacion="tableta",
            precio_venta=2.5,
        ),
        Medicamento(
            nombre="Diclofenaco",
            principio_activo="Diclofenaco sódico",
            presentacion="capsula",
            precio_venta=4.0,
        ),
    ]
    for m in medicamentos:
        catalog.add(m)

    listado = list(catalog.list())
    assert len(listado) == 2
    assert {m.nombre for m in listado} == {"Paracetamol", "Diclofenaco"}


# ————————————————————————————————————————————————————————————————
#   3. Búsqueda de ID inexistente
# ————————————————————————————————————————————————————————————————
def test_catalog_get_not_found(catalog) -> None:
    assert catalog.get(99) is None


# ————————————————————————————————————————————————————————————————
#   4. Validación Pydantic (nombre demasiado corto)
# ————————————————————————————————————————————————————————————————
import pydantic


def test_catalog_validation_error(catalog) -> None:
    with pytest.raises(pydantic.ValidationError):
        catalog.add(
            Medicamento(
                nombre="Ib",  # ← menos de 3 caracteres
                principio_activo="X",
                presentacion="tableta",
                precio_venta=1.0,
            )
        )
