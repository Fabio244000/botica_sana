import csv
from datetime import date
from pathlib import Path
from typing import Iterable, Literal

from core.models.movimiento import Movimiento, TipoMovimiento
from core.ports.repository_port import RepositoryPort

_Tipo = Literal["entradas", "salidas", "todos"]


class ReportService:
    """Genera listados de movimientos y los exporta a CSV/PDF."""

    def __init__(self, mov_repo: RepositoryPort[Movimiento]) -> None:
        self._repo = mov_repo

    # ─── consultas básicas ────────────────────────────────────
    def movimientos(
        self,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        tipo: _Tipo = "todos",
    ) -> Iterable[Movimiento]:
        for m in self._repo.list():
            if fecha_desde and m.creado_en.date() < fecha_desde:
                continue
            if fecha_hasta and m.creado_en.date() > fecha_hasta:
                continue
            if tipo == "entradas" and m.tipo != TipoMovimiento.ENTRADA:
                continue
            if tipo == "salidas" and m.tipo != TipoMovimiento.SALIDA:
                continue
            yield m

    # ─── exportar CSV ─────────────────────────────────────────
    def to_csv(
        self,
        path: str | Path,
        movimientos: Iterable[Movimiento],
    ) -> Path:
        path = Path(path)
        with path.open("w", newline="", encoding="utf-8") as f:
            wr = csv.writer(f)
            wr.writerow(["ID", "Lote", "Tipo", "Cantidad", "Motivo", "Fecha/hora"])
            for m in movimientos:
                wr.writerow(
                    [
                        m.id,
                        m.lote_id,
                        m.tipo.value,
                        m.cantidad,
                        m.motivo,
                        m.creado_en.isoformat(sep=" ", timespec="seconds"),
                    ]
                )
        return path

    # ─── exportar PDF (ReportLab) ─────────────────────────────
    def to_pdf(
        self,
        path: str | Path,
        movimientos: Iterable[Movimiento],
    ) -> Path:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas

        path = Path(path)
        c = canvas.Canvas(str(path), pagesize=A4)
        w, h = A4
        y = h - 40
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Reporte de movimientos")
        y -= 30
        c.setFont("Helvetica", 9)
        for m in movimientos:
            c.drawString(
                40,
                y,
                f"{m.id:>4}  Lote:{m.lote_id:<4}  "
                f"{m.tipo.value:<7}  Cant:{m.cantidad:<5}  "
                f"{m.motivo:<20}  {m.creado_en:%Y-%m-%d %H:%M}",
            )
            y -= 15
            if y < 40:
                c.showPage()
                y = h - 40
        c.save()
        return path
