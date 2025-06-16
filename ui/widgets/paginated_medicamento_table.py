from __future__ import annotations

from typing import List, Sequence

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt

from core.models.medicamento import Medicamento
from infrastructure.db import SessionLocal
from infrastructure.repos import LoteRepo

# Columnas: cabecera y clave de modelo
_COLUMNS = [
    ("Id", "id"),
    ("Nombre", "nombre"),
    ("Código", "codigo"),
    ("Laboratorio", "laboratorio"),
    ("Precio venta", "precio_venta"),
    ("Disponible", "disponible"),  # muestra ✔/✖ según stock real
]


class PaginatedMedicamentoTableModel(QtCore.QAbstractTableModel):
    """Modelo con columna "Disponible" que muestra ✔ en verde o ✖ en rojo."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self._rows: List[Medicamento] = []
        # repositorio de lotes para calcular stock real
        self._lote_repo = LoteRepo(SessionLocal())

    def set_rows(self, meds: Sequence[Medicamento]) -> None:
        """Reemplaza las filas actuales por la lista dada de Medicamento."""
        self.beginResetModel()
        self._rows = list(meds)
        self.endResetModel()

    def item(self, row: int) -> Medicamento:
        """Devuelve la instancia Medicamento en la fila dada."""
        return self._rows[row]

    def rowCount(self, parent=QtCore.QModelIndex()) -> int:
        return len(self._rows)

    def columnCount(self, parent=QtCore.QModelIndex()) -> int:
        return len(_COLUMNS)

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return _COLUMNS[section][0]
        return super().headerData(section, orientation, role)

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        col_key = _COLUMNS[index.column()][1]
        med = self._rows[index.row()]

        # columna disponible: calcular stock sumando lotes
        if col_key == "disponible":
            lotes = list(self._lote_repo.list())
            total = sum(l.stock for l in lotes if l.medicamento_id == med.id)
            if role == QtCore.Qt.DisplayRole:
                return "✔" if total > 0 else "✖"
            if role == QtCore.Qt.TextAlignmentRole:
                return QtCore.Qt.AlignCenter
            if role == QtCore.Qt.ForegroundRole:
                color = QtGui.QColor("green") if total > 0 else QtGui.QColor("red")
                return QtGui.QBrush(color)
            return None

        # para las otras columnas, mostrar su atributo
        val = getattr(med, col_key)
        if role in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole):
            # formatear precio con 2 decimales
            if col_key == "precio_venta":
                return f"{val:.2f}"
            return val
        return None
