import csv
import os
from datetime import datetime

from core.models.movimiento import Movimiento, TipoMovimiento
from core.ports.repository_port import RepositoryPort
from core.services.report_service import ReportService


class RepoMock(RepositoryPort[Movimiento]):
    def __init__(self, movs):
        self._movs = movs

    def list(self):
        return self._movs

    def add(self, e): ...
    def get(self, _): ...
    def delete(self, _): ...


def test_csv_export(tmp_path):
    movs = [
        Movimiento(
            id=1,
            lote_id=1,
            tipo=TipoMovimiento.ENTRADA,
            cantidad=5,
            motivo="test",
            creado_en=datetime.utcnow(),
        )
    ]
    svc = ReportService(RepoMock(movs))
    path = svc.to_csv(tmp_path / "rep.csv", movs)
    with path.open() as f:
        rows = list(csv.reader(f))
    assert rows[1][0] == "1"  # id en primera fila


def test_pdf_export(tmp_path):
    movs = [
        Movimiento(
            id=1,
            lote_id=1,
            tipo=TipoMovimiento.SALIDA,
            cantidad=2,
            motivo="x",
            creado_en=datetime.utcnow(),
        )
    ]
    svc = ReportService(RepoMock(movs))
    path = svc.to_pdf(tmp_path / "rep.pdf", movs)
    assert path.exists() and os.path.getsize(path) > 0
