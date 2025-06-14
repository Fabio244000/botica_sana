from datetime import date

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from core.models.lote import Lote

HEADERS = ["Código", "Medicamento", "Stock", "Vence en (días)"]


class AlertTableModel(QAbstractTableModel):
    def __init__(self, rows=None):
        super().__init__()
        self._rows: list[Lote] = rows or []

    def rowCount(self, *_):
        return len(self._rows)

    def columnCount(self, *_):
        return len(HEADERS)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        l = self._rows[index.row()]
        col = index.column()
        return [
            l.codigo,
            l.medicamento_id,  # luego se mapea a nombre
            l.stock,
            (l.fecha_vencimiento - date.today()).days,
        ][col]

    def headerData(self, sec, orient, role):
        if orient == Qt.Horizontal and role == Qt.DisplayRole:
            return HEADERS[sec]
        return super().headerData(sec, orient, role)

    def set_rows(self, rows):
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()
