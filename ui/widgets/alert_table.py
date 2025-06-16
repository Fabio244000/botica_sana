# ui/widgets/alert_table.py

from datetime import date
from typing import List

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

HEADERS = ["Código", "Medicamento", "Stock", "Vence en (días)"]


class AlertTableModel(QAbstractTableModel):
    """
    Modelo para alertas de lote:
      • Código
      • Medicamento (ID por ahora; luego puedes resolver nombre)
      • Stock
      • Días para vencer
    """

    def __init__(self, rows: List, parent=None):
        super().__init__(parent)
        self._rows = rows

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._rows)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(HEADERS)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        lote = self._rows[index.row()]
        dias = (lote.fecha_vencimiento - date.today()).days
        return [
            lote.codigo,
            lote.medicamento_id,
            lote.stock,
            dias,
        ][index.column()]

    def headerData(
        self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole
    ):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return HEADERS[section]
        return super().headerData(section, orientation, role)

    def set_rows(self, rows: List):
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()
