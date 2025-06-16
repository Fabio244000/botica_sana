from typing import Any, Iterable, List, Mapping, Tuple

from pydantic import PositiveInt

from core.models.medicamento import Medicamento
from core.ports.repository_port import RepositoryPort


class CatalogService:
    """Caso de uso: administrar el catálogo de medicamentos."""

    def __init__(self, repo: RepositoryPort[Medicamento]) -> None:
        self._repo = repo

    # ───────────────────────────── CRUD BÁSICO ──────────────────────────────

    def add(self, med: Medicamento) -> Medicamento:
        """Dar de alta un medicamento en el catálogo."""
        return self._repo.add(med)

    def get(self, med_id: PositiveInt) -> Medicamento | None:
        """Obtener un medicamento por su identificador único."""
        return self._repo.get(med_id)

    def list(self) -> Iterable[Medicamento]:
        """Listar el catálogo completo (⚠ puede ser pesado)."""
        return self._repo.list()

    def update(self, med_id: PositiveInt, data: Mapping[str, Any]) -> Medicamento:
        """Actualizar parcialmente un medicamento."""
        med = self.get(med_id)
        if med is None:
            raise ValueError("Medicamento no existe")

        updated_med = med.model_copy(update=data)
        return self._repo.add(updated_med)  # el repo realiza upsert

    def delete(self, med_id: PositiveInt) -> None:
        """Eliminar un medicamento del catálogo."""
        med = self.get(med_id)
        if med is None:
            raise ValueError("Medicamento no existe")

        self._repo.delete(med_id)

    # ─────────────────────────── PAGINACIÓN & FILTROS ──────────────────────

    def list_paginated(
        self,
        *,
        page: int = 1,
        per_page: int = 20,
        filters: Mapping[str, object] | None = None,
    ) -> Tuple[List[Medicamento], int, int]:
        """
        Devuelve (items, total, total_pages).

        ────────────── Parámetros ──────────────
        • page:         1-based
        • per_page:     tamaño de página (20 por defecto)
        • filters:      puede incluir:
            - nombre_codigo: str  → busca LIKE en nombre o código
            - laboratorio:   str
            - tipo:          str
        """
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 20

        offset = (page - 1) * per_page
        items, total = self._repo.list_paginated(
            limit=per_page, offset=offset, filters=filters
        )
        total_pages = (total + per_page - 1) // per_page
        return items, total, total_pages

    # ─────────────────────── CARGA INICIAL (últimos 100) ────────────────────

    def latest_100(self) -> List[Medicamento]:
        """Devuelve los 100 medicamentos más recientes (creado_en DESC)."""
        items, _ = self._repo.list_paginated(limit=100, offset=0)
        return items
