from __future__ import annotations

import uuid
from datetime import date
from typing import Mapping

from PySide6 import QtWidgets
from PySide6.QtCore import Qt

from core.services.catalog_service import CatalogService
from core.services.inventory_service import FIFOSelector, InventoryService
from infrastructure.auth_context import get_current_user
from infrastructure.db import SessionLocal
from infrastructure.repos import LoteRepo, MedicamentoRepo, MovimientoRepo
from ui.widgets.medicamento_form import MedicamentoForm
from ui.widgets.paginated_medicamento_table import \
    PaginatedMedicamentoTableModel
from ui.widgets.toast import Toast

_PER_PAGE = 20


class CatalogView(QtWidgets.QWidget):
    """Vista Catálogo con paginación + filtros."""

    def __init__(self):
        super().__init__()
        self.svc = CatalogService(MedicamentoRepo(SessionLocal()))

        # ─── Estado ────────────────────────────────────────────
        self._page = 1
        self._total_pages = 1
        self._filters: Mapping[str, object] | None = None

        # ─── Tabla ─────────────────────────────────────────────
        self.table = QtWidgets.QTableView()
        self.model = PaginatedMedicamentoTableModel(self)
        self.table.setModel(self.model)
        self.table.doubleClicked.connect(self._edit_current)

        # Ajustes de columnas
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # Selección transparente
        self.table.setStyleSheet(
            """
            QTableView::item:selected {
                background: transparent;
                color: black;
            }
        """
        )

        # ─── Controles de filtro ─────────────────────────────────
        self.le_search = QtWidgets.QLineEdit(placeholderText="Nombre o código…")
        self.le_search.returnPressed.connect(self._apply_filters)

        self.cb_lab = QtWidgets.QComboBox()
        self.cb_lab.addItem("Laboratorio (todos)")

        self.cb_tipo = QtWidgets.QComboBox()
        self.cb_tipo.addItem("Tipo (todos)")

        self.btn_search = QtWidgets.QPushButton("🔍", clicked=self._apply_filters)

        # ─── Paginador ─────────────────────────────────────────
        self.btn_first = QtWidgets.QPushButton("⏮", clicked=lambda: self._goto(1))
        self.btn_prev = QtWidgets.QPushButton(
            "◀", clicked=lambda: self._goto(self._page - 1)
        )
        self.btn_next = QtWidgets.QPushButton(
            "▶", clicked=lambda: self._goto(self._page + 1)
        )
        self.btn_last = QtWidgets.QPushButton(
            "⏭", clicked=lambda: self._goto(self._total_pages)
        )
        for btn in (self.btn_first, self.btn_prev, self.btn_next, self.btn_last):
            btn.setFixedWidth(40)
        self.lbl_page = QtWidgets.QLabel()

        # ─── Botones CRUD ───────────────────────────────────────
        self.btn_new = QtWidgets.QPushButton("➕ Nuevo", clicked=self._add)
        self.btn_edit = QtWidgets.QPushButton("✏️ Editar", clicked=self._edit_current)
        self.btn_del = QtWidgets.QPushButton("🗑️ Eliminar", clicked=self._delete_current)
        self.btn_del.setObjectName("btn_danger")

        # ─── Estilos de botón Eliminar ─────────────────────────
        self.setStyleSheet(
            """
            QPushButton#btn_danger {
                background-color: #e53935;
                color: white;
                font-weight: bold;
            }
            QPushButton#btn_danger:hover {
                background-color: #c62828;
            }
            QPushButton#btn_danger:pressed {
                background-color: #b71c1c;
            }
        """
        )

        # ─── Layouts ───────────────────────────────────────────
        top_bar = QtWidgets.QHBoxLayout()
        top_bar.addWidget(self.le_search)
        top_bar.addWidget(self.cb_lab)
        top_bar.addWidget(self.cb_tipo)
        top_bar.addWidget(self.btn_search)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_new)
        top_bar.addWidget(self.btn_edit)
        top_bar.addWidget(self.btn_del)

        pager = QtWidgets.QHBoxLayout()
        pager.addWidget(self.btn_first)
        pager.addWidget(self.btn_prev)
        pager.addWidget(self.lbl_page)
        pager.addWidget(self.btn_next)
        pager.addWidget(self.btn_last)
        pager.addStretch()

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(top_bar)
        layout.addWidget(self.table)
        layout.addLayout(pager)

        # ─── Inicializar datos ─────────────────────────────────
        self._load_combo_data()
        self._load_initial()

    def _load_initial(self):
        meds = self.svc.latest_100()
        self._total_pages = (len(meds) + _PER_PAGE - 1) // _PER_PAGE or 1
        self._page = 1
        self.model.set_rows(meds[:_PER_PAGE])
        self._update_page_label()

    def _apply_filters(self):
        filters: dict[str, object] = {}
        txt = self.le_search.text().strip()
        if txt:
            filters["nombre_codigo"] = txt

        lab = self.cb_lab.currentText()
        if lab != "Laboratorio (todos)":
            filters["laboratorio"] = lab

        typ = self.cb_tipo.currentText()
        if typ != "Tipo (todos)":
            filters["tipo"] = typ

        self._filters = filters or None
        self._goto(1)

    def _goto(self, page: int):
        if page < 1:
            page = 1
        items, _, total_pages = self.svc.list_paginated(
            page=page, per_page=_PER_PAGE, filters=self._filters
        )
        self._page = page
        self._total_pages = max(total_pages, 1)
        self.model.set_rows(items)
        self._update_page_label()

    def _update_page_label(self):
        self.lbl_page.setText(f"Página {self._page} / {self._total_pages}")
        self.btn_first.setEnabled(self._page > 1)
        self.btn_prev.setEnabled(self._page > 1)
        self.btn_next.setEnabled(self._page < self._total_pages)
        self.btn_last.setEnabled(self._page < self._total_pages)

    def _load_combo_data(self):
        latest = self.svc.latest_100()
        labs = sorted({m.laboratorio for m in latest if m.laboratorio})
        tipos = sorted({m.tipo for m in latest if m.tipo})
        self.cb_lab.addItems(labs)
        self.cb_tipo.addItems(tipos)

    def _current_med(self):
        idx = self.table.currentIndex()
        return self.model.item(idx.row()) if idx.isValid() else None

    def _add(self):
        dlg = MedicamentoForm(self)
        if dlg.exec() != QtWidgets.QDialog.Accepted:
            return

        med = dlg.get_data()
        med_saved = self.svc.add(med)

        stock_ini = dlg.get_stock_inicial()
        if stock_ini > 0:
            lote_repo = LoteRepo(SessionLocal())
            mov_repo = MovimientoRepo(SessionLocal())
            inv = InventoryService(lote_repo, mov_repo, FIFOSelector(lote_repo))
            current = get_current_user()
            usuario_id = current.id if current else 1
            inv.entrada_nueva(
                codigo=str(uuid.uuid4())[:8],
                medicamento_id=med_saved.id,
                fecha_venc=date.today().replace(year=date.today().year + 2),
                cantidad=stock_ini,
                motivo="Ingreso inicial",
                usuario_id=usuario_id,
            )

        self._apply_filters()
        Toast.show_("Medicamento creado", self)

    def _edit_current(self):
        med = self._current_med()
        if not med:
            return
        dlg = MedicamentoForm(self, med)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            data = dlg.get_data().model_dump(exclude={"id"}, mode="python")
            self.svc.update(med.id, data)
            self._apply_filters()
            Toast.show_("Medicamento actualizado", self)

    def _delete_current(self):
        med = self._current_med()
        if not med:
            return
        if (
            QtWidgets.QMessageBox.question(self, "Eliminar", f"¿Eliminar {med.nombre}?")
            == QtWidgets.QMessageBox.Yes
        ):
            self.svc.delete(med.id)
            self._apply_filters()
            Toast.show_("Medicamento eliminado", self)
