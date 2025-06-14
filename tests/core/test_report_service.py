from datetime import date, timedelta
from pathlib import Path

import pytest

from core.models.lote import Lote
from core.models.movimiento import Movimiento, TipoMovimiento
from core.ports.file_export_port import FileExportPort
from core.ports.repository_port import RepositoryPort
from core.services.report_service import ReportService


# ————————————————————————————————————————————————————————————————
#   Repos genéricos en memoria
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
#   Exportador CSV dummy
# ————————————————————————————————————————————————————————————————
class DummyExporter(FileExportPort):
    def export_csv(self, rows, path: Path) -> Path:
        # escribe cada dict como línea str() separada por newline
        with path.open("w", encoding="utf-8") as fp:
            for r in rows:
                fp.write(str(r) + "\n")
        return path


# ————————————————————————————————————————————————————————————————
#   Fixture ReportService con datos cargados
# ————————————————————————————————————————————————————————————————
@pytest.fixture
def reporte(tmp_path):
    lote_repo = InMemoryRepo()
    mov_repo = InMemoryRepo()
    exporter = DummyExporter()

    hoy = date.today()

    # Lote 1
    lote1 = lote_repo.add(
        Lote(
            codigo="L10",
            medicamento_id=1,
            fecha_vencimiento=hoy + timedelta(days=60),
            stock=20,
        )
    )
    # Lote 2
    lote2 = lote_repo.add(
        Lote(
            codigo="L20",
            medicamento_id=2,
            fecha_vencimiento=hoy + timedelta(days=120),
            stock=15,
        )
    )

    # Movimientos
    mov_repo.add(
        Movimiento(
            lote_id=lote1.id,
            tipo=TipoMovimiento.ENTRADA,
            cantidad=20,
            motivo="compra",
        )
    )
    mov_repo.add(
        Movimiento(
            lote_id=lote2.id,
            tipo=TipoMovimiento.SALIDA,
            cantidad=5,
            motivo="venta",
        )
    )

    return ReportService(lote_repo, mov_repo, exporter), lote_repo, tmp_path


# ————————————————————————————————————————————————————————————————
#   1. Inventario actual
# ————————————————————————————————————————————————————————————————
def test_inventario_actual(reporte):
    rs, lote_repo, _ = reporte
    rows = list(rs.inventario())
    assert len(rows) == len(list(lote_repo.list()))
    campos = {"lote_id", "medicamento_id", "stock", "vence"}
    assert campos.issubset(rows[0].keys())


# ————————————————————————————————————————————————————————————————
#   2. Kardex filtrado por lote_id
# ————————————————————————————————————————————————————————————————
def test_kardex_por_lote_id(reporte):
    rs, lote_repo, _ = reporte
    lote1 = next(iter(lote_repo.list()))
    kardex = list(rs.kardex(lote1.id))
    assert all(m.lote_id == lote1.id for m in kardex)
    assert kardex[0].tipo == TipoMovimiento.ENTRADA


# ————————————————————————————————————————————————————————————————
#   3. Exportar CSV
# ————————————————————————————————————————————————————————————————
def test_export_csv_crea_archivo(reporte):
    rs, lote_repo, tmp_path = reporte
    out_path = tmp_path / "inventario.csv"
    result = rs.export_inventario_csv(out_path)
    assert result.exists()
    # líneas = número de lotes
    with result.open(encoding="utf-8") as fp:
        lineas = fp.readlines()
    assert len(lineas) == len(list(lote_repo.list()))
    # limpiar archivo tmp
    result.unlink()
