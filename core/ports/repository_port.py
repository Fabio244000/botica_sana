from abc import ABC, abstractmethod
from typing import Generic, Iterable, TypeVar

T = TypeVar("T")


class RepositoryPort(ABC, Generic[T]):
    """Operaciones CRUD mínimas para cualquier entidad."""

    @abstractmethod
    def add(self, entity: T) -> T: ...

    @abstractmethod
    def get(self, entity_id: int) -> T | None: ...

    @abstractmethod
    def list(self) -> Iterable[T]: ...

    @abstractmethod
    def delete(self, entity_id: int) -> None: ...
