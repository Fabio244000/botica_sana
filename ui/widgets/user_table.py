from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from core.models.usuario import Usuario

HEADERS = ["ID", "Usuario", "Rol", "Activo"]


class UserTableModel(QAbstractTableModel):
    def __init__(self, rows=None):
        super().__init__()
        self._rows: list[Usuario] = rows or []

    def rowCount(self, *_):
        return len(self._rows)

    def columnCount(self, *_):
        return len(HEADERS)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        u = self._rows[index.row()]
        return [u.id, u.username, u.rol.value, "✔" if u.activo else "✖"][index.column()]

    def headerData(self, sec, orient, role):
        if orient == Qt.Horizontal and role == Qt.DisplayRole:
            return HEADERS[sec]
        return super().headerData(sec, orient, role)

    def set_rows(self, rows):
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()

    def user_at(self, row: int) -> Usuario:
        return self._rows[row]
