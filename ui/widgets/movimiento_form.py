from datetime import date
from typing import Dict, List, Optional

from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import (QComboBox, QDateEdit, QFormLayout, QHBoxLayout,
                               QLineEdit, QMessageBox, QPushButton, QSpinBox,
                               QVBoxLayout)

from core.models.movimiento import TipoMovimiento
from infrastructure.db import SessionLocal
from infrastructure.repos import LoteRepo, MedicamentoRepo


class MovimientoForm(QtWidgets.QDialog):
    def __init__(
        self,
        parent=None,
        tipo: TipoMovimiento = TipoMovimiento.ENTRADA,
        necesita_fecha: bool = False,
        show_med: bool = True,
        show_lote: bool = True,
        movimiento: Optional[any] = None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Editar movimiento" if movimiento else "Nuevo movimiento")
        self.setModal(True)
        self.tipo = tipo
        self._necesita_fecha = necesita_fecha

        # Repositorios y datos
        db = SessionLocal()
        self._med_repo = MedicamentoRepo(db)
        self._lote_repo = LoteRepo(db)

        self._meds = list(self._med_repo.list())
        self._lotes_by_med: Dict[int, List] = {
            m.id: [l for l in self._lote_repo.list() if l.medicamento_id == m.id]
            for m in self._meds
        }

        # Controles
        if show_med:
            self.cb_med = QComboBox()
            for m in self._meds:
                self.cb_med.addItem(f"{m.codigo} – {m.nombre}", m.id)
            self.cb_med.currentIndexChanged.connect(self._on_med_changed)
        else:
            self.cb_med = None

        if show_lote:
            self.cb_lote = QComboBox()
        else:
            self.cb_lote = None

        if show_med and self.cb_med:
            self._on_med_changed(0)

        self.sb_cant = QSpinBox()
        self.sb_cant.setRange(1, 9999)

        self.dt_venc = QDateEdit(calendarPopup=True)
        self.dt_venc.setDate(QtCore.QDate.currentDate())

        self.le_motivo = QLineEdit()

        # Layout
        form = QFormLayout()
        if self.cb_med:
            form.addRow("Medicamento", self.cb_med)
        if self.cb_lote:
            form.addRow("Lote (stock)", self.cb_lote)
        form.addRow("Cantidad", self.sb_cant)
        if self._necesita_fecha:
            form.addRow("Fecha vencimiento", self.dt_venc)
        form.addRow("Motivo", self.le_motivo)

        btn_ok = QPushButton("Aceptar")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)

        main = QVBoxLayout(self)
        main.addLayout(form)
        main.addLayout(btn_layout)

    def _on_med_changed(self, index: int):
        if not self.cb_lote:
            return
        med_id = self.cb_med.itemData(index)
        lotes = self._lotes_by_med.get(med_id, [])
        self.cb_lote.clear()
        for lote in lotes:
            self.cb_lote.addItem(f"{lote.codigo} (stock: {lote.stock})", lote.id)

    def get_data(self) -> dict:
        data = {}
        if self.cb_lote:
            idx = self.cb_lote.currentIndex()
            if idx < 0:
                QMessageBox.warning(self, "Error", "Debe seleccionar un lote válido.")
                return {}
            lote_id = self.cb_lote.itemData(idx)
            stock = int(self.cb_lote.currentText().split("stock: ")[1].rstrip(")"))
            if self.tipo == TipoMovimiento.SALIDA and self.sb_cant.value() > stock:
                QMessageBox.warning(
                    self,
                    "Stock insuficiente",
                    f"No puede retirar {self.sb_cant.value()}; sólo hay {stock}.",
                )
                return {}
            data["lote_id"] = lote_id

        data["cantidad"] = self.sb_cant.value()
        data["motivo"] = self.le_motivo.text().strip()
        data["tipo"] = self.tipo
        if self._necesita_fecha:
            data["fecha_venc"] = self.dt_venc.date().toPython()
        return data

    def accept(self) -> None:
        if not self.get_data():
            return
        super().accept()
