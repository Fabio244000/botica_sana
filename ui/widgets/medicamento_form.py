import pydantic
from PySide6 import QtWidgets

from core.models.enums import Presentacion
from core.models.medicamento import Medicamento


class MedicamentoForm(QtWidgets.QDialog):
    def __init__(self, parent=None, med: Medicamento | None = None):
        super().__init__(parent)
        self.setWindowTitle("Medicamento")
        self.setModal(True)

        # campos
        self.le_nombre = QtWidgets.QLineEdit()
        self.le_pactivo = QtWidgets.QLineEdit()
        self.cb_present = QtWidgets.QComboBox()
        self.sb_precio = QtWidgets.QDoubleSpinBox()
        self.sb_precio.setRange(0.01, 9999)
        self.sb_precio.setDecimals(2)

        for p in Presentacion:
            self.cb_present.addItem(p.value, p)

        # botones
        btn_ok = QtWidgets.QPushButton("Guardar")
        btn_cancel = QtWidgets.QPushButton("Cancelar")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        # layout
        form = QtWidgets.QFormLayout()
        form.addRow("Nombre", self.le_nombre)
        form.addRow("Principio activo", self.le_pactivo)
        form.addRow("Presentación", self.cb_present)
        form.addRow("Precio venta", self.sb_precio)

        h = QtWidgets.QHBoxLayout()
        h.addStretch()
        h.addWidget(btn_ok)
        h.addWidget(btn_cancel)

        v = QtWidgets.QVBoxLayout(self)
        v.addLayout(form)
        v.addLayout(h)

        self._result: Medicamento | None = None
        if med:
            self._populate(med)

    # ─────────────────────────────────────────────────────────────
    def _populate(self, med: Medicamento) -> None:
        self.setWindowTitle(f"Editar: {med.nombre}")
        self.le_nombre.setText(med.nombre)
        self.le_pactivo.setText(med.principio_activo)
        idx = self.cb_present.findData(med.presentacion)
        self.cb_present.setCurrentIndex(idx)
        self.sb_precio.setValue(med.precio_venta)
        self._result = med

    def get_data(self) -> Medicamento | None:
        return self._result

    # aceptamos y validamos con Pydantic
    def accept(self) -> None:
        try:
            data = {
                "nombre": self.le_nombre.text(),
                "principio_activo": self.le_pactivo.text(),
                "presentacion": self.cb_present.currentData(),
                "precio_venta": float(self.sb_precio.value()),
            }
            if self._result:  # edición
                self._result = self._result.model_copy(update=data)
            else:
                self._result = Medicamento(**data)
        except pydantic.ValidationError as e:
            QtWidgets.QMessageBox.warning(self, "Error", str(e))
            return
        super().accept()
