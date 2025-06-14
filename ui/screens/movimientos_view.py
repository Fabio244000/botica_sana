from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QInputDialog, QTableWidget, QTableWidgetItem

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

        self.setStyleSheet(
            """
            QPushButton {
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 13px;
                background-color: #e0e0e0;
            }
            QPushButton:hover {
                background-color: #d5d5d5;
            }
            QPushButton:checked {
                background-color: #3f51b5;
                color: white;
                font-weight: bold;
                border: 2px solid #303f9f;
            }
        """
        )

        # Campo de búsqueda
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("Buscar movimiento...")

        # Botones
        self.btn_search = QtWidgets.QPushButton("🔍")
        self.btn_ent = QtWidgets.QPushButton("➕ Entrada")
        self.btn_sal = QtWidgets.QPushButton("📤 Salida")
        self.btn_new_lote = QtWidgets.QPushButton("🧾 Entrada nuevo lote")

        for btn in [self.btn_ent, self.btn_sal, self.btn_new_lote]:
            btn.setCheckable(True)

        self.btn_search.clicked.connect(self._buscar_movimientos)
        self.btn_ent.clicked.connect(
            lambda: self._accion(self.btn_ent, TipoMovimiento.ENTRADA)
        )
        self.btn_sal.clicked.connect(
            lambda: self._accion(self.btn_sal, TipoMovimiento.SALIDA)
        )
        self.btn_new_lote.clicked.connect(lambda: self._accion(self.btn_new_lote, None))

        # Encabezado
        top = QtWidgets.QHBoxLayout()
        top.addWidget(self.search_input)
        top.addWidget(self.btn_search)
        top.addStretch()
        top.addWidget(self.btn_ent)
        top.addWidget(self.btn_sal)
        top.addWidget(self.btn_new_lote)

        # Tabla de movimientos
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Fecha", "Tipo", "Medicamento", "Cantidad", "Motivo"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.lbl_info = QtWidgets.QLabel("Seleccione un lote y haga la operación.")

        v = QtWidgets.QVBoxLayout(self)
        v.addLayout(top)
        v.addWidget(self.table)
        v.addWidget(self.lbl_info)

    def _accion(self, btn, tipo):
        self.btn_ent.setChecked(False)
        self.btn_sal.setChecked(False)
        self.btn_new_lote.setChecked(False)

        btn.setChecked(True)
        QtCore.QTimer.singleShot(300, lambda: btn.setChecked(False))

        if tipo:
            self._nuevo_movimiento(tipo)
        else:
            self._entrada_nuevo_lote()

    def _nuevo_movimiento(self, tipo: TipoMovimiento):
        dlg = MovimientoForm(self, tipo)
        if dlg.exec() != QtWidgets.QDialog.Accepted:
            return

        data = dlg.get_data()
        try:
            if tipo == TipoMovimiento.ENTRADA:
                self.inv.entrada_nueva(
                    "codigo-temporal",
                    1,
                    QtCore.QDate.currentDate(),
                    data["cantidad"],
                    data["motivo"],
                )
            else:
                self.inv.salida(1, data["cantidad"], data["motivo"])
        except ValueError as e:
            QtWidgets.QMessageBox.warning(self, "Error", str(e))
        else:
            QtWidgets.QMessageBox.information(self, "OK", "Movimiento registrado")

    def _entrada_nuevo_lote(self):
        dlg = MovimientoForm(self, TipoMovimiento.ENTRADA, necesita_fecha=True)
        if dlg.exec() != QtWidgets.QDialog.Accepted:
            return

        data = dlg.get_data()
        codigo, ok = QInputDialog.getText(self, "Nuevo lote", "Código lote:")
        if not ok or not codigo:
            return

        try:
            self.inv.entrada_nueva(
                codigo=codigo,
                medicamento_id=1,  # FIXME
                fecha_venc=data["fecha_venc"],
                cantidad=data["cantidad"],
                motivo=data["motivo"],
            )
        except ValueError as e:
            QtWidgets.QMessageBox.warning(self, "Error", str(e))
        else:
            QtWidgets.QMessageBox.information(self, "OK", "Lote creado")

    def _buscar_movimientos(self):
        texto = self.search_input.text().strip()
        if not texto:
            return
        QtWidgets.QMessageBox.information(self, "Buscar", f"Búsqueda: {texto}")
