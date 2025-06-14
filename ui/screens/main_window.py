from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets

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
        self.resize(1280, 800)
        icon_path = Path(__file__).parent.parent / "assets/icons/botica_sana_logo.png"
        self.setWindowIcon(QtGui.QIcon(str(icon_path)))

        self.setStyleSheet(
            """
            QPushButton {
                padding: 10px 18px;
                font-size: 14px;
                border-radius: 6px;
            }

            /* Botón cerrar sesión */
            QPushButton#btn_logout {
                background-color: #cc4444;
                color: white;
                font-weight: bold;
            }

            /* Botón alerta */
            QPushButton#btn_alert {
                background-color: transparent;
                border: none;
                color: red;
                font-size: 16px;
            }
            QPushButton#btn_alert:hover {
                border: 1px solid red;
                background-color: rgba(255, 0, 0, 0.05);
                border-radius: 6px;
            }

            /* Menú lateral */
            QPushButton#menu_btn {
                background-color: #e0e0e0;
                color: #111;
                font-size: 14px;
                padding: 10px;
                border-radius: 6px;
                border: none;
            }
            QPushButton#menu_btn:checked {
                background-color: #c5cae9;
                font-weight: bold;
                border: 2px solid #3f51b5;
                color: #111;
            }
        """
        )

        # ─── Layout principal ───
        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)
        main_layout = QtWidgets.QVBoxLayout(central)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # ─── Encabezado superior (solo botón de alerta) ───
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.addStretch()

        self.btn_alert = QtWidgets.QPushButton("🔔 0")
        self.btn_alert.setObjectName("btn_alert")
        self.btn_alert.clicked.connect(self._open_alert_center)
        header_layout.addWidget(self.btn_alert)

        main_layout.addLayout(header_layout)

        # ─── Zona central ───
        content_layout = QtWidgets.QHBoxLayout()
        content_layout.setSpacing(12)

        menu = QtWidgets.QVBoxLayout()
        menu.setSpacing(12)

        self.btn_catalogo = QtWidgets.QPushButton("📦 Catálogo")
        self.btn_mov = QtWidgets.QPushButton("📋 Movimientos")
        self.btn_users = QtWidgets.QPushButton("👤 Usuarios")
        self.btn_rep = QtWidgets.QPushButton("📊 Reportes")

        # Botones seleccionables
        self.sidebar_buttons = [
            self.btn_catalogo,
            self.btn_mov,
            self.btn_users,
            self.btn_rep,
        ]
        for btn in self.sidebar_buttons:
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.setObjectName("menu_btn")  # importante para aplicar estilo
            menu.addWidget(btn)

        self.btn_catalogo.setChecked(True)  # vista por defecto activa

        menu.addStretch()

        # ─── Botón "Cerrar sesión" abajo a la izquierda ───
        self.btn_logout = QtWidgets.QPushButton("Cerrar sesión")
        self.btn_logout.setObjectName("btn_logout")
        self.btn_logout.clicked.connect(self._logout)
        menu.addWidget(self.btn_logout)

        # ─── Stacked widget ───
        self.stacked = QtWidgets.QStackedWidget()
        content_layout.addLayout(menu, 1)
        content_layout.addWidget(self.stacked, 5)
        main_layout.addLayout(content_layout)

        # ─── Datos de alerta ───
        self._alert_data = {"stock": [], "vencimiento": []}
        lote_repo = LoteRepo(SessionLocal())
        worker = AlertWorker(AlertService(lote_repo))
        worker.alerts_ready.connect(self._update_alerts)

        # ─── Vistas ───
        self.catalog_view = CatalogView()
        self.mov_view = MovimientosView()
        self.rep_view = ReportView()
        self.user_view = UserAdminView()

        self.stacked.addWidget(self.catalog_view)
        self.stacked.addWidget(self.mov_view)
        self.stacked.addWidget(self.rep_view)
        self.stacked.addWidget(self.user_view)

        # ─── Router con activación visual ───
        self.btn_catalogo.clicked.connect(
            lambda: self._change_view(self.catalog_view, self.btn_catalogo)
        )
        self.btn_mov.clicked.connect(
            lambda: self._change_view(self.mov_view, self.btn_mov)
        )
        self.btn_users.clicked.connect(
            lambda: self._change_view(self.user_view, self.btn_users)
        )
        self.btn_rep.clicked.connect(
            lambda: self._change_view(self.rep_view, self.btn_rep)
        )

    def _change_view(self, widget, active_button):
        self.stacked.setCurrentWidget(widget)
        for btn in self.sidebar_buttons:
            btn.setChecked(btn == active_button)

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
        set_current_user(None)
        QtWidgets.QApplication.quit()
