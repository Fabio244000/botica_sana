from PySide6 import QtWidgets
from PySide6.QtWidgets import QInputDialog

from core.models.lote import Lote
from core.models.movimiento import TipoMovimiento
from core.services.inventory_service import FIFOSelector, InventoryService
from infrastructure.db import SessionLocal
from infrastructure.repos import LoteRepo, MovimientoRepo
from ui.widgets.movimiento_form import MovimientoForm


class MovimientosView(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        db = SessionLocal()
        self.inv = InventoryService(
            LoteRepo(db), MovimientoRepo(db), FIFOSelector(LoteRepo(db))
        )

        # combo con lotes
        self.cmb_lote = QtWidgets.QComboBox()
        self._cargar_lotes()

        # botones
        btn_ent = QtWidgets.QPushButton("Entrada")
        btn_sal = QtWidgets.QPushButton("Salida")
        btn_new_lote = QtWidgets.QPushButton("Entrada nuevo lote")  # ← NUEVO

        btn_ent.clicked.connect(lambda: self._nuevo_movimiento(TipoMovimiento.ENTRADA))
        btn_sal.clicked.connect(lambda: self._nuevo_movimiento(TipoMovimiento.SALIDA))
        btn_new_lote.clicked.connect(self._entrada_nuevo_lote)

        h = QtWidgets.QHBoxLayout()
        h.addWidget(self.cmb_lote)
        h.addWidget(btn_ent)
        h.addWidget(btn_sal)
        h.addWidget(btn_new_lote)
        h.addStretch()

        self.lbl_info = QtWidgets.QLabel("Seleccione un lote y haga la operación.")

        v = QtWidgets.QVBoxLayout(self)
        v.addLayout(h)
        v.addWidget(self.lbl_info)

    # ────────────────────────────────────────────────────────────
    def _cargar_lotes(self):
        self.cmb_lote.clear()
        for lote in LoteRepo(SessionLocal()).list():
            self.cmb_lote.addItem(f"{lote.codigo} (stock {lote.stock})", lote)

    def _nuevo_movimiento(self, tipo: TipoMovimiento):
        lote: Lote = self.cmb_lote.currentData()
        if lote is None:
            return

        dlg = MovimientoForm(self, tipo)
        if dlg.exec() != QtWidgets.QDialog.Accepted:
            return

        data = dlg.get_data()
        try:
            if tipo is TipoMovimiento.ENTRADA:
                self.inv.entrada(lote, data["cantidad"], data["motivo"])
            else:
                self.inv.salida(lote.medicamento_id, data["cantidad"], data["motivo"])
        except ValueError as e:
            QtWidgets.QMessageBox.warning(self, "Error", str(e))
        else:
            QtWidgets.QMessageBox.information(self, "OK", "Movimiento registrado")
        self._cargar_lotes()

    # -------- Entrada de lote NUEVO ---------------------------------
    def _entrada_nuevo_lote(self):
        dlg = MovimientoForm(self, TipoMovimiento.ENTRADA, necesita_fecha=True)
        if dlg.exec() != QtWidgets.QDialog.Accepted:
            return

        data = dlg.get_data()
        codigo, ok = QInputDialog.getText(self, "Nuevo lote", "Código lote:")
        if not ok or not codigo:
            return

        try:
            # TODO: seleccionar medicamento desde la interfaz; por ahora id=1
            self.inv.entrada_nueva(
                codigo=codigo,
                medicamento_id=1,
                fecha_venc=data["fecha_venc"],
                cantidad=data["cantidad"],
                motivo=data["motivo"],
            )
        except ValueError as e:
            QtWidgets.QMessageBox.warning(self, "Error", str(e))
        else:
            QtWidgets.QMessageBox.information(self, "OK", "Lote creado")
        self._cargar_lotes()
