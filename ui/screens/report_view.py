from pathlib import Path

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QDate

from core.services.report_service import ReportService
from infrastructure.db import SessionLocal
from infrastructure.repos import MovimientoRepo
from ui.widgets.alert_table import AlertTableModel


class ReportView(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.svc = ReportService(MovimientoRepo(SessionLocal()))

        # ─── Estilos ───────────────────────────────
        self.setStyleSheet(
            """
            QPushButton {
                padding: 8px 20px;
                font-size: 14px;
                border-radius: 6px;
                background-color: #e0e0e0;
            }
            QPushButton:hover {
                background-color: #d5d5d5;
            }
            QPushButton:checked {
                background-color: #3f51b5;
                border: 2px solid #303f9f;
                font-weight: bold;
                color: white;
            }

            QTableView {
                background-color: #ffffff;
                alternate-background-color: #f7f7f7;
                selection-color: white;
                selection-background-color: #3f51b5;
                font-size: 13px;
                gridline-color: #dcdcdc;
            }

            QHeaderView::section {
                background-color: #eeeeee;
                font-weight: bold;
                padding: 6px;
                border: 1px solid #d3d3d3;
            }
        """
        )

        # ─── Filtros ────────────────────────────────
        self.dt_desde = QtWidgets.QDateEdit()
        self.dt_hasta = QtWidgets.QDateEdit()
        self.dt_desde.setCalendarPopup(True)
        self.dt_hasta.setCalendarPopup(True)
        self.dt_desde.setDate(QDate.currentDate().addMonths(-1))
        self.dt_hasta.setDate(QDate.currentDate())

        self.cb_tipo = QtWidgets.QComboBox()
        self.cb_tipo.addItems(["todos", "entradas", "salidas"])

        self.btn_filtrar = QtWidgets.QPushButton("Filtrar")
        self.btn_csv = QtWidgets.QPushButton("Exportar CSV")
        self.btn_pdf = QtWidgets.QPushButton("Exportar PDF")

        self.btn_filtrar.setCheckable(True)
        self.btn_csv.setCheckable(True)
        self.btn_pdf.setCheckable(True)

        self.btn_filtrar.clicked.connect(
            lambda: self._handle_action(self.btn_filtrar, self._aplicar_filtros)
        )
        self.btn_csv.clicked.connect(
            lambda: self._handle_action(self.btn_csv, lambda: self._exportar("csv"))
        )
        self.btn_pdf.clicked.connect(
            lambda: self._handle_action(self.btn_pdf, lambda: self._exportar("pdf"))
        )

        # ─── Layout de filtros ──────────────────────
        filtro_layout = QtWidgets.QHBoxLayout()
        filtro_layout.addWidget(QtWidgets.QLabel("Desde"))
        filtro_layout.addWidget(self.dt_desde)
        filtro_layout.addWidget(QtWidgets.QLabel("Hasta"))
        filtro_layout.addWidget(self.dt_hasta)
        filtro_layout.addWidget(QtWidgets.QLabel("Tipo"))
        filtro_layout.addWidget(self.cb_tipo)
        filtro_layout.addWidget(self.btn_filtrar)
        filtro_layout.addStretch()
        filtro_layout.addWidget(self.btn_csv)
        filtro_layout.addWidget(self.btn_pdf)

        # ─── Tabla de resultados ─────────────────────
        self.tbl = QtWidgets.QTableView()
        self.model = AlertTableModel([])
        self.tbl.setModel(self.model)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.horizontalHeader().setStretchLastSection(True)

        # ─── Layout principal ────────────────────────
        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(filtro_layout)
        layout.addWidget(self.tbl)

        self._aplicar_filtros()

    def _handle_action(self, btn, action):
        # Reiniciar estados
        self.btn_filtrar.setChecked(False)
        self.btn_csv.setChecked(False)
        self.btn_pdf.setChecked(False)

        btn.setChecked(True)
        QtCore.QTimer.singleShot(300, lambda: btn.setChecked(False))
        action()

    def _movs_filtrados(self):
        f_desde = self.dt_desde.date().toPython()
        f_hasta = self.dt_hasta.date().toPython()
        tipo = self.cb_tipo.currentText()
        return list(self.svc.movimientos(f_desde, f_hasta, tipo))

    def _aplicar_filtros(self):
        self.model.set_rows(self._movs_filtrados())
        self.tbl.resizeColumnsToContents()

    def _exportar(self, formato: str):
        movs = self._movs_filtrados()
        if not movs:
            QtWidgets.QMessageBox.information(self, "Reportes", "Sin datos.")
            return
        filtro = "CSV (*.csv)" if formato == "csv" else "PDF (*.pdf)"
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Guardar", "", filtro)
        if not path:
            return
        fn = self.svc.to_csv if formato == "csv" else self.svc.to_pdf
        fn(Path(path), movs)
        QtWidgets.QMessageBox.information(self, "Reportes", "Archivo generado.")
