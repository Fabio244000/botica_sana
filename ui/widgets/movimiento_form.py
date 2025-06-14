from PySide6 import QtWidgets
from PySide6.QtCore import QDate
from PySide6.QtWidgets import QDateEdit

from core.models.movimiento import TipoMovimiento


class MovimientoForm(QtWidgets.QDialog):
    def __init__(
        self,
        parent=None,
        tipo: TipoMovimiento = TipoMovimiento.ENTRADA,
        necesita_fecha: bool = False,
    ):
        super().__init__(parent)
        self.setWindowTitle("Nuevo movimiento")
        self.setModal(True)

        self.tipo = tipo
        self._necesita_fecha = necesita_fecha  # ←★ GUARDAR EL FLAG

        self.sb_cant = QtWidgets.QSpinBox()
        self.sb_cant.setRange(1, 9999)
        self.le_motivo = QtWidgets.QLineEdit()

        self.dt_venc = QDateEdit()
        self.dt_venc.setCalendarPopup(True)
        self.dt_venc.setDate(QDate.currentDate())

        form = QtWidgets.QFormLayout()
        form.addRow("Cantidad", self.sb_cant)
        if necesita_fecha:  # solo cuando se requiere
            form.addRow("Fecha vencimiento", self.dt_venc)
        form.addRow("Motivo", self.le_motivo)

        btn_ok = QtWidgets.QPushButton("Aceptar")
        btn_cancel = QtWidgets.QPushButton("Cancelar")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        h = QtWidgets.QHBoxLayout()
        h.addStretch()
        h.addWidget(btn_ok)
        h.addWidget(btn_cancel)

        v = QtWidgets.QVBoxLayout(self)
        v.addLayout(form)
        v.addLayout(h)

    def get_data(self):
        data = {
            "cantidad": self.sb_cant.value(),
            "motivo": self.le_motivo.text().strip(),
            "tipo": self.tipo,
        }
        if self._necesita_fecha:
            data["fecha_venc"] = self.dt_venc.date().toPython()
        return data
