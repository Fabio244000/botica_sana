from typing import Iterable

from pydantic import PositiveInt

from core.models.medicamento import Medicamento
from core.ports.repository_port import RepositoryPort


class CatalogService:
    """Caso de uso: administrar el catálogo de medicamentos."""

    def __init__(self, repo: RepositoryPort[Medicamento]) -> None:
        self._repo = repo

    def add(self, med: Medicamento) -> Medicamento:
        """Dar de alta un medicamento."""
        return self._repo.add(med)

    def get(self, med_id: PositiveInt) -> Medicamento | None:
        """Obtener un medicamento por id."""
        return self._repo.get(med_id)

    def list(self) -> Iterable[Medicamento]:
        """Listar todo el catálogo."""
        return self._repo.list()

    def update(self, med_id: int, data: dict) -> Medicamento:
        med = self.get(med_id)
        if med is None:
            raise ValueError("Medicamento no existe")
        updated = med.model_copy(update=data)
        return self._repo.add(updated)  # InMemory / SQL repo usa upsert

    def delete(self, med_id: int) -> None:
        med = self.get(med_id)
        if med is None:
            raise ValueError("Medicamento no existe")
        # repo no tenía delete, así que lo añadiremos en infraestructura
        self._repo.delete(med_id)
