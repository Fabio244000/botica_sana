from abc import ABC, abstractmethod
from typing import Generic, Iterable, List, Mapping, Tuple, TypeVar

T = TypeVar("T")


class RepositoryPort(ABC, Generic[T]):
    """Operaciones CRUD mínimas + paginación opcional."""

    # --- CRUD mínimo ---
    @abstractmethod
    def add(self, entity: T) -> T: ...
    @abstractmethod
    def get(self, entity_id: int) -> T | None: ...
    @abstractmethod
    def list(self) -> Iterable[T]: ...
    @abstractmethod
    def delete(self, entity_id: int) -> None: ...

    # --- Paginación: implementación por defecto ----------
    def list_paginated(
        self,
        limit: int,
        offset: int = 0,
        filters: Mapping[str, object] | None = None,
    ) -> Tuple[List[T], int]:
        """
        Implementación básica: usa list() + slice.
        Repositorios que necesiten queries eficientes deben sobreescribirla.
        """
        items = list(self.list())
        total = len(items)
        return items[offset : offset + limit], total
