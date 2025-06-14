from datetime import date
from typing import Iterable

from pydantic import PositiveInt

from core.models.lote import Lote
from core.models.movimiento import Movimiento, TipoMovimiento
from core.ports.repository_port import RepositoryPort


class FIFOSelector:
    """Selector FIFO basado en fecha de vencimiento + id."""

    def __init__(self, lote_repo: RepositoryPort[Lote]) -> None:
        self._repo = lote_repo

    def next_lote(self, medicamento_id: int) -> Lote | None:
        lotes = [
            l
            for l in self._repo.list()
            if l.medicamento_id == medicamento_id and l.stock > 0
        ]
        lotes.sort(key=lambda l: (l.fecha_vencimiento, l.id))
        return lotes[0] if lotes else None

    def lotes_con_stock(self, medicamento_id: int) -> Iterable[Lote]:
        return (
            l
            for l in self._repo.list()
            if l.medicamento_id == medicamento_id and l.stock > 0
        )


class InventoryService:
    def __init__(
        self,
        lote_repo: RepositoryPort[Lote],
        mov_repo: RepositoryPort[Movimiento],
        fifo_selector: FIFOSelector,
    ) -> None:
        self._lote_repo = lote_repo
        self._mov_repo = mov_repo
        self._fifo = fifo_selector

    # Entradas
    def entrada(self, lote: Lote, cantidad: PositiveInt, motivo: str) -> Movimiento:
        lote.stock += cantidad
        self._lote_repo.add(lote)
        return self._mov_repo.add(
            Movimiento(
                lote_id=lote.id,
                tipo=TipoMovimiento.ENTRADA,
                cantidad=cantidad,
                motivo=motivo,
            )
        )

    def entrada_nueva(
        self,
        codigo: str,
        medicamento_id: int,
        fecha_venc: date,
        cantidad: PositiveInt,
        motivo: str,
    ) -> Movimiento:
        # lote nace con la cantidad real
        lote = Lote(
            codigo=codigo,
            medicamento_id=medicamento_id,
            fecha_vencimiento=fecha_venc,
            stock=cantidad,
        )
        lote = self._lote_repo.add(lote)  # INSERT

        # registramos el movimiento de entrada
        return self._mov_repo.add(
            Movimiento(
                lote_id=lote.id,
                tipo=TipoMovimiento.ENTRADA,
                cantidad=cantidad,
                motivo=motivo,
            )
        )

    # Salidas con FIFO
    def salida(
        self, medicamento_id: int, cantidad: PositiveInt, motivo: str
    ) -> list[Movimiento]:
        movimientos: list[Movimiento] = []
        restante = cantidad

        while restante > 0:
            lote = self._fifo.next_lote(medicamento_id)
            if lote is None or lote.stock == 0:
                raise ValueError("Stock insuficiente")

            salida_qty = min(lote.stock, restante)
            lote.stock -= salida_qty
            self._lote_repo.add(lote)  # persiste cambio

            movimientos.append(
                self._mov_repo.add(
                    Movimiento(
                        lote_id=lote.id,
                        tipo=TipoMovimiento.SALIDA,
                        cantidad=salida_qty,
                        motivo=motivo,
                    )
                )
            )
            restante -= salida_qty

        return movimientos

    def lotes_con_stock(self, medicamento_id: int) -> Iterable[Lote]:
        return self._fifo.lotes_con_stock(medicamento_id)

    def dias_para_vencer(lote: Lote) -> int:
        return (lote.fecha_vencimiento - date.today()).days
