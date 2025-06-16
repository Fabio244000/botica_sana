from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from core.models.usuario import Usuario

# Mostramos 8 campos: ID, Usuario, Nombre completo, DNI, Email, Celular, Rol, Activo
HEADERS = [
    "ID",
    "Usuario",
    "Nombre completo",
    "DNI",
    "Email",
    "Celular",
    "Rol",
    "Activo",
]


class UserTableModel(QAbstractTableModel):
    def __init__(self, rows: list[Usuario] | None = None):
        super().__init__()
        self._rows: list[Usuario] = rows or []

    def rowCount(self, *_):
        return len(self._rows)

    def columnCount(self, *_):
        return len(HEADERS)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        user = self._rows[index.row()]
        col = index.column()

        if col == 0:
            return user.id
        elif col == 1:
            return user.username
        elif col == 2:
            return user.nombre_completo
        elif col == 3:
            return user.dni
        elif col == 4:
            return user.email
        elif col == 5:
            return user.celular
        elif col == 6:
            return user.rol.value
        elif col == 7:
            # ✔ si está activo, ✖ si está desactivado
            return "✔" if user.activo else "✖"
        return None

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return HEADERS[section]
        return super().headerData(section, orientation, role)

    def set_rows(self, rows: list[Usuario]):
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()

    def user_at(self, row: int) -> Usuario:
        return self._rows[row]
