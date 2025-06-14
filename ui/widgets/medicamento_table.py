from typing import Any, List

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from core.models.medicamento import Medicamento

HEADERS = ["ID", "Nombre", "Principio activo", "Presentación", "Precio"]


class MedicamentoTableModel(QAbstractTableModel):
    def __init__(self, datos: List[Medicamento] | None = None):
        super().__init__()
        self._rows: List[Medicamento] = datos or []

    # ─── Qt overrides ────────────────────────────────────────────
    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._rows)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(HEADERS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        med = self._rows[index.row()]
        col = index.column()
        return [
            med.id,
            med.nombre,
            med.principio_activo,
            med.presentacion.value,
            f"{med.precio_venta:.2f}",
        ][col]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return HEADERS[section]
        return super().headerData(section, orientation, role)

    # ─── API pública ─────────────────────────────────────────────
    def set_rows(self, rows: List[Medicamento]) -> None:
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()

    def item(self, row: int) -> Medicamento:
        return self._rows[row]
