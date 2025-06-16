from datetime import date, timedelta
from typing import Dict, Iterable, List

from core.models.lote import Lote
from core.ports.repository_port import RepositoryPort


class AlertService:
    """
    Detecta lotes con:

    • stock bajo (≤ umbral)
    • fecha de vencimiento dentro de los próximos `dias`
    """

    def __init__(self, lote_repo: RepositoryPort[Lote]) -> None:
        self._repo = lote_repo

    # ────────────────────────── CONSULTAS ──────────────────────────

    def stock_minimo(self, umbral: int = 5) -> Iterable[Lote]:
        """Lotes cuyo stock es igual o inferior al umbral."""
        return (l for l in self._repo.list() if l.stock <= umbral)

    def por_vencer(self, dias: int = 30) -> Iterable[Lote]:
        """Lotes que vencerán en los próximos `dias` días (inclusive)."""
        limite = date.today() + timedelta(days=dias)
        return (l for l in self._repo.list() if l.fecha_vencimiento <= limite)

    # ────────────────────────── AGREGADOR ──────────────────────────

    def alertas(self, umbral: int = 5, dias: int = 30) -> Dict[str, List[Lote]]:
        """
        Devuelve un dict con las dos listas de alertas:

        ```python
        {
            "stock":       [Lote, ...],
            "vencimiento": [Lote, ...],
        }
        ```
        """
        return {
            "stock": list(self.stock_minimo(umbral)),
            "vencimiento": list(self.por_vencer(dias)),
        }
