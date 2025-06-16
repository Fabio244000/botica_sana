from pathlib import Path

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QDate

from core.services.report_service import ReportService
from infrastructure.db import SessionLocal
from infrastructure.repos import MovimientoRepo
from ui.widgets.report_table_model import ReportTableModel


class ReportView(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.svc = ReportService(MovimientoRepo(SessionLocal()))

        # ─── Estilos ───────────────────────────────
        self.setStyleSheet(
            """
            QPushButton { padding: 6px 12px; font-size: 13px; border-radius: 4px; background-color: #e0e0e0; }
            QPushButton:hover { background-color: #d5d5d5; }
            QPushButton:checked { background-color: #3f51b5; color: white; }
            QTableView { font-size: 13px; }
            QHeaderView::section { font-weight: bold; padding: 4px; }
        """
        )

        # ─── Filtros ────────────────────────────────
        self.dt_desde = QtWidgets.QDateEdit(calendarPopup=True)
        self.dt_hasta = QtWidgets.QDateEdit(calendarPopup=True)
        self.dt_desde.setDate(QDate.currentDate().addMonths(-1))
        self.dt_hasta.setDate(QDate.currentDate())

        self.cb_tipo = QtWidgets.QComboBox()
        self.cb_tipo.addItems(["todos", "entradas", "salidas"])

        # rangos rápidos
        self.btn_dia = QtWidgets.QPushButton("Último día")
        self.btn_semana = QtWidgets.QPushButton("Última semana")
        self.btn_mes = QtWidgets.QPushButton("Último mes")

        # acciones
        self.btn_filtrar = QtWidgets.QPushButton("Filtrar")
        self.btn_export_csv = QtWidgets.QPushButton("Exportar CSV")
        self.btn_export_pdf = QtWidgets.QPushButton("Exportar PDF")

        # paginación
        self.btn_prev = QtWidgets.QPushButton("◀")
        self.btn_next = QtWidgets.QPushButton("▶")
        self.lbl_page = QtWidgets.QLabel()

        for btn in (
            self.btn_dia,
            self.btn_semana,
            self.btn_mes,
            self.btn_filtrar,
            self.btn_export_csv,
            self.btn_export_pdf,
            self.btn_prev,
            self.btn_next,
        ):
            btn.setCheckable(True)
        self.btn_prev.setCheckable(False)
        self.btn_next.setCheckable(False)
        self.btn_prev.setFixedWidth(30)
        self.btn_next.setFixedWidth(30)

        # conexiones
        self.btn_dia.clicked.connect(lambda: self._range_and_refresh("dia"))
        self.btn_semana.clicked.connect(lambda: self._range_and_refresh("semana"))
        self.btn_mes.clicked.connect(lambda: self._range_and_refresh("mes"))
        self.btn_filtrar.clicked.connect(self._aplicar_filtros)
        self.btn_export_csv.clicked.connect(lambda: self._exportar("csv"))
        self.btn_export_pdf.clicked.connect(lambda: self._exportar("pdf"))
        self.btn_prev.clicked.connect(lambda: self._change_page(-1))
        self.btn_next.clicked.connect(lambda: self._change_page(1))

        # ─── Layout filtros ────────────────────────
        top = QtWidgets.QHBoxLayout()
        top.addWidget(self.btn_dia)
        top.addWidget(self.btn_semana)
        top.addWidget(self.btn_mes)
        top.addSpacing(20)
        top.addWidget(QtWidgets.QLabel("Desde"))
        top.addWidget(self.dt_desde)
        top.addWidget(QtWidgets.QLabel("Hasta"))
        top.addWidget(self.dt_hasta)
        top.addWidget(QtWidgets.QLabel("Tipo"))
        top.addWidget(self.cb_tipo)
        top.addWidget(self.btn_filtrar)
        top.addStretch()
        top.addWidget(self.btn_export_csv)
        top.addWidget(self.btn_export_pdf)

        # ─── Tabla de resultados ────────────────────
        self.tbl = QtWidgets.QTableView()
        # self.tbl.setAlternatingRowColors(True)
        self.tbl.verticalHeader().setVisible(False)

        header = self.tbl.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)  # Fecha/hora
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)  # Medicamento
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QtWidgets.QHeaderView.Stretch)

        # ─── Layout paginador ──────────────────────
        pager = QtWidgets.QHBoxLayout()
        pager.addStretch()
        pager.addWidget(self.btn_prev)
        pager.addWidget(self.lbl_page)
        pager.addWidget(self.btn_next)
        pager.addStretch()

        # ─── Layout principal ───────────────────────
        v = QtWidgets.QVBoxLayout(self)
        v.addLayout(top)
        v.addWidget(self.tbl)
        v.addLayout(pager)

        # inicializar paginación
        self._per_page = 20
        self._page = 1
        self._total = 0

        self._apply_and_paginate()

    def _range_and_refresh(self, period: str):
        hoy = QDate.currentDate()
        if period == "dia":
            self.dt_desde.setDate(hoy.addDays(-1))
        elif period == "semana":
            self.dt_desde.setDate(hoy.addDays(-7))
        else:
            self.dt_desde.setDate(hoy.addMonths(-1))
        self.dt_hasta.setDate(hoy)
        self._apply_and_paginate()

    def _aplicar_filtros(self):
        # validación de fechas
        if self.dt_desde.date() > self.dt_hasta.date():
            QtWidgets.QMessageBox.warning(
                self, "Error", "Desde no puede ser mayor que Hasta."
            )
            return
        self._page = 1
        self._apply_and_paginate()

    def _apply_and_paginate(self):
        movimientos = self.svc.movimientos(
            self.dt_desde.date().toPython(),
            self.dt_hasta.date().toPython(),
            self.cb_tipo.currentText(),
        )
        movs = list(movimientos)
        self._total = len(movs)
        self._total_pages = max(1, (self._total + self._per_page - 1) // self._per_page)

        start = (self._page - 1) * self._per_page
        end = start + self._per_page
        page_slice = movs[start:end]

        # actualizar modelo
        self.model = ReportTableModel(page_slice)
        self.tbl.setModel(self.model)

        # actualizar paginador
        self.lbl_page.setText(f"Página {self._page} / {self._total_pages}")
        self.btn_prev.setEnabled(self._page > 1)
        self.btn_next.setEnabled(self._page < self._total_pages)

    def _change_page(self, delta: int):
        self._page = min(max(1, self._page + delta), self._total_pages)
        self._apply_and_paginate()

    def _exportar(self, fmt: str):
        movs = list(
            self.svc.movimientos(
                self.dt_desde.date().toPython(),
                self.dt_hasta.date().toPython(),
                self.cb_tipo.currentText(),
            )
        )
        if not movs:
            QtWidgets.QMessageBox.information(self, "Reportes", "Sin datos.")
            return
        filtro = "CSV (*.csv)" if fmt == "csv" else "PDF (*.pdf)"
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Guardar", "", filtro)
        if not path:
            return
        fn = self.svc.to_csv if fmt == "csv" else self.svc.to_pdf
        fn(Path(path), movs)
        QtWidgets.QMessageBox.information(self, "Reportes", "Archivo generado.")
