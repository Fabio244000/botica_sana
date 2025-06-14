from pathlib import Path

from PySide6 import QtWidgets
from PySide6.QtCore import QDate

from core.services.report_service import ReportService
from infrastructure.db import SessionLocal
from infrastructure.repos import MovimientoRepo
from ui.widgets.alert_table import AlertTableModel  # tabla reutilizable


class ReportView(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.svc = ReportService(MovimientoRepo(SessionLocal()))

        # filtros
        self.dt_desde = QtWidgets.QDateEdit()
        self.dt_hasta = QtWidgets.QDateEdit()
        self.dt_desde.setCalendarPopup(True)
        self.dt_hasta.setCalendarPopup(True)
        self.dt_desde.setDate(QDate.currentDate().addMonths(-1))
        self.dt_hasta.setDate(QDate.currentDate())

        self.cb_tipo = QtWidgets.QComboBox()
        self.cb_tipo.addItems(["todos", "entradas", "salidas"])

        btn_filtrar = QtWidgets.QPushButton("Filtrar")
        btn_csv = QtWidgets.QPushButton("Exportar CSV")
        btn_pdf = QtWidgets.QPushButton("Exportar PDF")

        btn_filtrar.clicked.connect(self._aplicar_filtros)
        btn_csv.clicked.connect(lambda: self._exportar("csv"))
        btn_pdf.clicked.connect(lambda: self._exportar("pdf"))

        form = QtWidgets.QHBoxLayout()
        form.addWidget(QtWidgets.QLabel("Desde"))
        form.addWidget(self.dt_desde)
        form.addWidget(QtWidgets.QLabel("Hasta"))
        form.addWidget(self.dt_hasta)
        form.addWidget(QtWidgets.QLabel("Tipo"))
        form.addWidget(self.cb_tipo)
        form.addWidget(btn_filtrar)
        form.addStretch()
        form.addWidget(btn_csv)
        form.addWidget(btn_pdf)

        # tabla
        self.tbl = QtWidgets.QTableView()
        self.model = AlertTableModel([])  # reaprovechamos modelo sencillo
        self.tbl.setModel(self.model)

        v = QtWidgets.QVBoxLayout(self)
        v.addLayout(form)
        v.addWidget(self.tbl)

        self._aplicar_filtros()

    # ----------------------------------------------------------
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
