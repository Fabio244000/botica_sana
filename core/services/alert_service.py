from datetime import date, timedelta
from typing import Dict, Iterable, List

from core.models.lote import Lote
from core.ports.repository_port import RepositoryPort


class AlertService:
    """Detecta lotes con stock bajo o próximos a vencer."""

    def __init__(self, lote_repo: RepositoryPort[Lote]) -> None:
        self._repo = lote_repo

    # ─── consultas básicas ─────────────────────────────────────
    def stock_minimo(self, umbral: int = 5) -> Iterable[Lote]:
        return (l for l in self._repo.list() if l.stock <= umbral)

    def por_vencer(self, dias: int = 30) -> Iterable[Lote]:
        limite = date.today() + timedelta(days=dias)
        return (l for l in self._repo.list() if l.fecha_vencimiento <= limite)

    # ─── helper público: ambos tipos de alerta ─────────────────
    def alertas(self, umbral: int = 5, dias: int = 30) -> Dict[str, List[Lote]]:
        return {
            "stock": list(self.stock_minimo(umbral)),
            "vencimiento": list(self.por_vencer(dias)),
        }
