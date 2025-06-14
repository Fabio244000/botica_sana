from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, Mapping


class FileExportPort(ABC):
    """Adapter genérico para exportar datos (CSV, PDF…)."""

    @abstractmethod
    def export_csv(self, rows: Iterable[Mapping], path: Path) -> Path: ...
