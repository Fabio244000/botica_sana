from PySide6 import QtWidgets

from core.services.alert_service import AlertService
from infrastructure.auth_context import set_current_user
from infrastructure.db import SessionLocal
from infrastructure.repos import LoteRepo
from ui.alert_worker import AlertWorker
from ui.screens.alert_center import AlertCenter
from ui.screens.catalog_view import CatalogView
from ui.screens.movimientos_view import MovimientosView
from ui.screens.report_view import ReportView
from ui.screens.user_admin_view import UserAdminView


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Botica Sana")
        self.resize(900, 600)

        self.toolbar = self.addToolBar("Main")
        btn_logout = QtWidgets.QPushButton("Cerrar sesión")
        self.toolbar.addWidget(btn_logout)
        btn_logout.clicked.connect(self._logout)
        self.btn_alert = QtWidgets.QPushButton("🔔 0")
        self.toolbar.addWidget(self.btn_alert)
        self.btn_alert.clicked.connect(self._open_alert_center)

        self._alert_data = {"stock": [], "vencimiento": []}

        lote_repo = LoteRepo(SessionLocal())
        worker = AlertWorker(AlertService(lote_repo))
        worker.alerts_ready.connect(self._update_alerts)

        # layout principal
        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)
        hbox = QtWidgets.QHBoxLayout(central)

        # menú lateral
        menu = QtWidgets.QVBoxLayout()
        self.btn_catalogo = QtWidgets.QPushButton("Catálogo")
        self.btn_mov = QtWidgets.QPushButton("Movimientos")
        self.btn_rep = QtWidgets.QPushButton("Reportes")
        self.btn_users = QtWidgets.QPushButton("Usuarios")
        menu.addWidget(self.btn_catalogo)
        menu.addWidget(self.btn_mov)
        menu.addWidget(self.btn_rep)
        menu.insertWidget(2, self.btn_users)
        menu.addStretch()

        # stacked
        self.stacked = QtWidgets.QStackedWidget()

        hbox.addLayout(menu, 1)
        hbox.addWidget(self.stacked, 4)

        # ─── vistas ─────────────────────────────────────────────
        self.catalog_view = CatalogView()
        self.mov_view = MovimientosView()
        self.rep_view = ReportView()
        self.user_view = UserAdminView()

        self.stacked.addWidget(self.catalog_view)
        self.stacked.addWidget(self.mov_view)
        self.stacked.addWidget(self.rep_view)
        self.stacked.addWidget(self.user_view)

        # ─── señales menú → router ─────────────────────────────
        self.btn_catalogo.clicked.connect(
            lambda: self.stacked.setCurrentWidget(self.catalog_view)
        )
        self.btn_mov.clicked.connect(
            lambda: self.stacked.setCurrentWidget(self.mov_view)
        )
        self.btn_rep.clicked.connect(
            lambda: self.stacked.setCurrentWidget(self.rep_view)
        )
        self.btn_users.clicked.connect(
            lambda: self.stacked.setCurrentWidget(self.user_view)
        )

    def _update_alerts(self, data: dict):
        self._alert_data = data
        total = len(data["stock"]) + len(data["vencimiento"])
        self.btn_alert.setText(f"🔔 {total}")

    def _open_alert_center(self):
        if not any(self._alert_data.values()):
            QtWidgets.QMessageBox.information(self, "Alertas", "Sin alertas.")
            return
        dlg = AlertCenter(self._alert_data)
        dlg.exec()

    def _logout(self):
        if (
            QtWidgets.QMessageBox.question(self, "Salir", "¿Cerrar sesión?")
            != QtWidgets.QMessageBox.Yes
        ):
            return
        set_current_user(None)  # limpia contexto
        QtWidgets.QApplication.quit()
