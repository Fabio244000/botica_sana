from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

import pydantic
from PySide6 import QtCore, QtGui, QtWidgets

from core.models.enums import Presentacion
from core.models.medicamento import Medicamento

# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

_ASSETS_DIR = Path(__file__).parent.parent / "assets" / "img"
_NO_PHOTO = _ASSETS_DIR / "no-photo.png"


def _load_pixmap(path: str | Path) -> QtGui.QPixmap:
    """
    Devuelve un QPixmap siempre válido:
    - Si la ruta existe → la imagen
    - Si no → rectángulo gris para evitar warnings
    """
    pix = QtGui.QPixmap(str(path))
    if pix.isNull():
        pix = QtGui.QPixmap(160, 160)
        pix.fill(QtCore.Qt.lightGray)
    return pix


# ---------------------------------------------------------------------------
# Diálogo Medicamento
# ---------------------------------------------------------------------------


class MedicamentoForm(QtWidgets.QDialog):
    """Alta / edición de medicamento – campos completos + imagen + stock."""

    def __init__(self, parent=None, med: Optional[Medicamento] = None):
        super().__init__(parent)
        self.setWindowTitle("Medicamento")
        self.setModal(True)
        self.resize(640, 400)

        # ---------- controles de datos básicos ----------
        self.le_id = QtWidgets.QLineEdit(readOnly=True)
        self.le_creado = QtWidgets.QLineEdit(readOnly=True)

        self.le_nombre = QtWidgets.QLineEdit()
        self.le_codigo = QtWidgets.QLineEdit()
        self.le_tipo = QtWidgets.QLineEdit()
        self.le_pactivo = QtWidgets.QLineEdit()
        self.le_lab = QtWidgets.QLineEdit()

        self.cb_present = QtWidgets.QComboBox()
        for p in Presentacion:
            self.cb_present.addItem(p.value, p)

        self.le_concentracion = QtWidgets.QLineEdit()
        self.le_forma = QtWidgets.QLineEdit()
        self.le_via = QtWidgets.QLineEdit()

        self.te_indic = QtWidgets.QPlainTextEdit()
        self.te_contra = QtWidgets.QPlainTextEdit()
        self.te_cond = QtWidgets.QPlainTextEdit()

        self.sb_precio = QtWidgets.QDoubleSpinBox()
        self.sb_precio.setRange(0.01, 9999)
        self.sb_precio.setDecimals(2)

        self.sb_stock = QtWidgets.QSpinBox()
        self.sb_stock.setRange(0, 10_000)

        # ---------- imagen ----------
        self.lbl_img = QtWidgets.QLabel(alignment=QtCore.Qt.AlignCenter)
        self.lbl_img.setFixedSize(160, 160)
        self.lbl_img.setFrameShape(QtWidgets.QFrame.Box)
        self.lbl_img.setPixmap(
            _load_pixmap(_NO_PHOTO).scaled(
                160, 160, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
            )
        )
        self.btn_img = QtWidgets.QPushButton(
            "Seleccionar imagen", clicked=self._choose_img
        )
        self._img_path: str | None = None

        # ---------- botones ----------
        btn_ok = QtWidgets.QPushButton("Guardar", clicked=self.accept)
        btn_cancel = QtWidgets.QPushButton("Cancelar", clicked=self.reject)

        # ---------- layouts ----------
        form_left = QtWidgets.QFormLayout()
        form_left.addRow("ID", self.le_id)
        form_left.addRow("Creado en", self.le_creado)
        form_left.addRow("Nombre*", self.le_nombre)
        form_left.addRow("Código*", self.le_codigo)
        form_left.addRow("Tipo*", self.le_tipo)
        form_left.addRow("Principio activo*", self.le_pactivo)
        form_left.addRow("Laboratorio", self.le_lab)
        form_left.addRow("Presentación*", self.cb_present)
        form_left.addRow("Concentración", self.le_concentracion)
        form_left.addRow("Forma farmacéutica", self.le_forma)
        form_left.addRow("Vía administración", self.le_via)
        form_left.addRow("Precio venta*", self.sb_precio)
        form_left.addRow("Stock inicial", self.sb_stock)
        form_left.addRow("Indicaciones", self.te_indic)
        form_left.addRow("Contraindicaciones", self.te_contra)
        form_left.addRow("Cond. almacenamiento", self.te_cond)

        img_col = QtWidgets.QVBoxLayout()
        img_col.addWidget(self.lbl_img)
        img_col.addWidget(self.btn_img)
        img_col.addStretch()

        top = QtWidgets.QHBoxLayout()
        top.addLayout(form_left, 3)
        top.addLayout(img_col, 1)

        btns = QtWidgets.QHBoxLayout()
        btns.addStretch()
        btns.addWidget(btn_ok)
        btns.addWidget(btn_cancel)

        v = QtWidgets.QVBoxLayout(self)
        v.addLayout(top)
        v.addLayout(btns)

        # ---------- estado inicial ----------
        self._result: Medicamento | None = None
        if med:
            self._populate(med)

    # ───────────────────────── helpers ─────────────────────────

    def _choose_img(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Seleccionar imagen", "", "Images (*.png *.jpg *.jpeg)"
        )
        if path:
            self._img_path = path
            self.lbl_img.setPixmap(
                _load_pixmap(path).scaled(
                    160, 160, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
                )
            )

    def _populate(self, med: Medicamento):
        self.setWindowTitle(f"Editar: {med.nombre}")
        self.le_id.setText(str(med.id))
        self.le_creado.setText(med.creado_en.strftime("%Y-%m-%d %H:%M"))
        self.le_nombre.setText(med.nombre)
        self.le_codigo.setText(med.codigo)
        self.le_tipo.setText(med.tipo)
        self.le_pactivo.setText(med.principio_activo)
        self.le_lab.setText(med.laboratorio or "")
        self.le_concentracion.setText(med.concentracion or "")
        self.le_forma.setText(med.forma_farmaceutica or "")
        self.le_via.setText(med.via_administracion or "")
        self.te_indic.setPlainText(med.indicaciones or "")
        self.te_contra.setPlainText(med.contraindicaciones or "")
        self.te_cond.setPlainText(med.condiciones_almacenamiento or "")

        if med.imagen_url:
            self._img_path = med.imagen_url
            self.lbl_img.setPixmap(
                _load_pixmap(med.imagen_url).scaled(
                    160, 160, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
                )
            )

        idx = self.cb_present.findData(med.presentacion)
        self.cb_present.setCurrentIndex(idx)
        self.sb_precio.setValue(med.precio_venta)

        # En edición, no permitimos cambiar el stock inicial
        self.sb_stock.setEnabled(False)
        self._result = med

    # ───────────────────────── API pública ─────────────────────────

    def get_data(self) -> Medicamento:
        return self._result  # se setea en accept()

    def get_stock_inicial(self) -> int:
        return int(self.sb_stock.value())

    # ───────────────────────── validación & accept ─────────────────────────
    def accept(self) -> None:
        try:
            payload = {
                "nombre": self.le_nombre.text(),
                "codigo": self.le_codigo.text(),
                "tipo": self.le_tipo.text(),
                "principio_activo": self.le_pactivo.text(),
                "laboratorio": self.le_lab.text() or None,
                "presentacion": self.cb_present.currentData(),
                "concentracion": self.le_concentracion.text() or None,
                "forma_farmaceutica": self.le_forma.text() or None,
                "via_administracion": self.le_via.text() or None,
                "indicaciones": self.te_indic.toPlainText() or None,
                "contraindicaciones": self.te_contra.toPlainText() or None,
                "condiciones_almacenamiento": self.te_cond.toPlainText() or None,
                "imagen_url": self._img_path,
                "precio_venta": float(self.sb_precio.value()),
                "creado_en": datetime.utcnow(),
            }

            if self._result:  # edición
                self._result = self._result.model_copy(update=payload)
            else:  # nuevo
                self._result = Medicamento(**payload)

        except pydantic.ValidationError as e:
            QtWidgets.QMessageBox.warning(self, "Error", str(e))
            return

        super().accept()
