from datetime import date
from typing import List

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from core.models.movimiento import Movimiento
from infrastructure.db import SessionLocal
from infrastructure.repos import LoteRepo, MedicamentoRepo, UsuarioRepo


class ReportTableModel(QAbstractTableModel):
    """
    Modelo de tabla para reportes de movimientos, mostrando columnas:
    Fecha/hora, Tipo, Usuario, Medicamento, Lote, Cantidad, Días para vencer
    """

    HEADERS = [
        "Fecha/hora",
        "Tipo",
        "Usuario",
        "Medicamento",
        "Lote",
        "Cantidad",
        "Días para vencer",
    ]

    def __init__(self, movimientos: List[Movimiento], parent=None):
        super().__init__(parent)
        self._movs = movimientos
        db = SessionLocal()
        self._user_repo = UsuarioRepo(db)
        self._lote_repo = LoteRepo(db)
        self._med_repo = MedicamentoRepo(db)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._movs)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.HEADERS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        mov = self._movs[index.row()]
        col = index.column()

        lote = self._lote_repo.get(mov.lote_id)
        med = self._med_repo.get(lote.medicamento_id) if lote else None
        user = self._user_repo.get(mov.usuario_id)

        if col == 0:
            return mov.creado_en.strftime("%Y-%m-%d %H:%M")
        elif col == 1:
            return mov.tipo.value
        elif col == 2:
            return user.username if user else ""
        elif col == 3:
            return f"{med.codigo} – {med.nombre}" if med else ""
        elif col == 4:
            return lote.codigo if lote else ""
        elif col == 5:
            return str(mov.cantidad)
        elif col == 6:
            return str((lote.fecha_vencimiento - date.today()).days) if lote else ""
        return None

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole
    ):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal and 0 <= section < len(self.HEADERS):
            return self.HEADERS[section]
        return super().headerData(section, orientation, role)
