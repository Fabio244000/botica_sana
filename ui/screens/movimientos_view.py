from datetime import date
from math import ceil

from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem

from core.models.movimiento import TipoMovimiento
from core.services.inventory_service import FIFOSelector, InventoryService
from infrastructure.auth_context import get_current_user
from infrastructure.db import SessionLocal
from infrastructure.repos import (LoteRepo, MedicamentoRepo, MovimientoRepo,
                                  UsuarioRepo)
from ui.widgets.buscar_medicamento_dialog import BuscarMedicamentoDialog
from ui.widgets.movimiento_form import MovimientoForm


class MovimientosView(QtWidgets.QWidget):
    def __init__(self, initial_limit: int = 100):
        super().__init__()
        self._initial_limit = initial_limit

        db = SessionLocal()
        self.mov_repo = MovimientoRepo(db)
        self.user_repo = UsuarioRepo(db)
        self.lote_repo = LoteRepo(db)
        self.medic_repo = MedicamentoRepo(db)
        self.inv = InventoryService(
            self.lote_repo,
            MovimientoRepo(db),
            FIFOSelector(self.lote_repo),
        )

        # Barra superior
        self.search_input = QtWidgets.QLineEdit(
            placeholderText="Buscar por ID o medicamento…"
        )
        self.btn_search = QtWidgets.QPushButton("🔍", clicked=self._buscar_movimientos)

        self.de_desde = QtWidgets.QDateEdit(calendarPopup=True)
        self.de_desde.setDisplayFormat("yyyy-MM-dd")
        self.de_desde.setDate(QtCore.QDate.currentDate().addDays(-30))

        self.de_hasta = QtWidgets.QDateEdit(calendarPopup=True)
        self.de_hasta.setDisplayFormat("yyyy-MM-dd")
        self.de_hasta.setDate(QtCore.QDate.currentDate())

        self.btn_ent = QtWidgets.QPushButton(
            "➕ Entrada",
            clicked=lambda: self._accion(self.btn_ent, TipoMovimiento.ENTRADA),
        )
        self.btn_sal = QtWidgets.QPushButton(
            "📤 Salida",
            clicked=lambda: self._accion(self.btn_sal, TipoMovimiento.SALIDA),
        )
        self.btn_new_lote = QtWidgets.QPushButton(
            "🧾 Nuevo lote",
            clicked=lambda: self._accion(self.btn_new_lote, None),
        )
        for b in (self.btn_ent, self.btn_sal, self.btn_new_lote):
            b.setCheckable(True)

        top = QtWidgets.QHBoxLayout()
        top.addWidget(self.search_input)
        top.addWidget(self.btn_search)
        top.addStretch()
        top.addWidget(QtWidgets.QLabel("Desde:"))
        top.addWidget(self.de_desde)
        top.addWidget(QtWidgets.QLabel("Hasta:"))
        top.addWidget(self.de_hasta)
        top.addStretch()
        top.addWidget(self.btn_ent)
        top.addWidget(self.btn_sal)
        top.addWidget(self.btn_new_lote)

        # Tabla de movimientos
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            [
                "ID",
                "Fecha",
                "Usuario",
                "Tipo",
                "Medicamento",
                "Stock",
                "Cantidad",
                "Motivo",
            ]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self._on_edit_movement)

        # Paginador
        self.btn_prev_page = QtWidgets.QPushButton(
            "◀", clicked=lambda: self._goto(self._page - 1)
        )
        self.btn_next_page = QtWidgets.QPushButton(
            "▶", clicked=lambda: self._goto(self._page + 1)
        )
        for b in (self.btn_prev_page, self.btn_next_page):
            b.setFixedWidth(30)
        self.lbl_page = QtWidgets.QLabel()
        pager = QtWidgets.QHBoxLayout()
        pager.addStretch()
        pager.addWidget(self.btn_prev_page)
        pager.addWidget(self.lbl_page)
        pager.addWidget(self.btn_next_page)
        pager.addStretch()

        # Layout principal
        main = QtWidgets.QVBoxLayout(self)
        main.addLayout(top)
        main.addWidget(self.table)
        main.addLayout(pager)

        self._load_initial()

    def _load_initial(self):
        movs = list(self.mov_repo.list_recent(self._initial_limit))
        self._all_movs = movs
        self._per_page = 20
        self._total_pages = max(1, ceil(len(movs) / self._per_page))
        self._page = 1
        self._show_page()

    def _buscar_movimientos(self):
        txt = self.search_input.text().strip()
        if txt and txt.isdigit():
            mov = self.mov_repo.get(int(txt))
            self._all_movs = [mov] if mov else []
        elif txt:
            key = txt.lower()
            meds = list(self.medic_repo.list())
            med_ids = {
                m.id for m in meds if key in m.nombre.lower() or key in m.codigo.lower()
            }
            recent = list(self.mov_repo.list_recent(self._initial_limit))
            self._all_movs = [
                mov
                for mov in recent
                if (l := self.lote_repo.get(mov.lote_id))
                and l.medicamento_id in med_ids
            ]
        else:
            desde = self.de_desde.date().toPython()
            hasta = self.de_hasta.date().toPython()
            recent = list(self.mov_repo.list_recent(self._initial_limit))
            self._all_movs = [
                mov for mov in recent if desde <= mov.creado_en.date() <= hasta
            ]
        self._reset_paginator()

    def _reset_paginator(self):
        self._total_pages = max(1, ceil(len(self._all_movs) / self._per_page))
        self._page = 1
        self._show_page()

    def _goto(self, page: int):
        self._page = max(1, min(page, self._total_pages))
        self._show_page()

    def _show_page(self):
        start = (self._page - 1) * self._per_page
        end = start + self._per_page
        page_items = self._all_movs[start:end]

        self.table.setRowCount(0)
        for row, mov in enumerate(page_items):
            user = self.user_repo.get(mov.usuario_id)
            username = user.username if user else f"#{mov.usuario_id}"

            lote = self.lote_repo.get(mov.lote_id)
            med_str = ""
            stock = ""
            if lote:
                stock = str(lote.stock)
                if med := self.medic_repo.get(lote.medicamento_id):
                    med_str = f"{med.codigo} – {med.nombre}"

            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(mov.id)))
            self.table.setItem(
                row, 1, QTableWidgetItem(mov.creado_en.strftime("%Y-%m-%d %H:%M"))
            )
            self.table.setItem(row, 2, QTableWidgetItem(username))
            self.table.setItem(row, 3, QTableWidgetItem(mov.tipo.value))
            self.table.setItem(row, 4, QTableWidgetItem(med_str))
            self.table.setItem(row, 5, QTableWidgetItem(stock))
            self.table.setItem(row, 6, QTableWidgetItem(str(mov.cantidad)))
            self.table.setItem(row, 7, QTableWidgetItem(mov.motivo))

        self.lbl_page.setText(f"Página {self._page} / {self._total_pages}")
        self.btn_prev_page.setEnabled(self._page > 1)
        self.btn_next_page.setEnabled(self._page < self._total_pages)

    def _select_lote(self) -> int | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        mov_id = int(self.table.item(row, 0).text())
        mov = self.mov_repo.get(mov_id)
        return mov.lote_id if mov else None

    def _on_edit_movement(self, row: int, column: int):
        mov_id = int(self.table.item(row, 0).text())
        mov = self.mov_repo.get(mov_id)
        if not mov:
            return

        dlg = MovimientoForm(
            self, mov.tipo, necesita_fecha=False, show_med=False, show_lote=True
        )
        lote = self.lote_repo.get(mov.lote_id)
        if dlg.cb_lote.count() == 0:
            dlg.cb_lote.addItem(f"{lote.codigo} (stock: {lote.stock})", lote.id)
        idx = next(
            i
            for i in range(dlg.cb_lote.count())
            if dlg.cb_lote.itemData(i) == mov.lote_id
        )
        dlg.cb_lote.setCurrentIndex(idx)

        dlg.sb_cant.setValue(mov.cantidad)
        dlg.le_motivo.setText(mov.motivo)

        if dlg.exec() != QtWidgets.QDialog.Accepted:
            return

        data = dlg.get_data()
        current = get_current_user()
        user_id = current.id if current else mov.usuario_id

        updated = mov.model_copy(
            update={
                "cantidad": data["cantidad"],
                "motivo": data["motivo"],
                "usuario_id": user_id,
            }
        )
        self.mov_repo.add(updated)
        QMessageBox.information(self, "OK", "Movimiento actualizado")
        self._buscar_movimientos()

    def _accion(self, btn, tipo):
        for b in (self.btn_ent, self.btn_sal, self.btn_new_lote):
            b.setChecked(False)
        btn.setChecked(True)
        QtCore.QTimer.singleShot(300, lambda: btn.setChecked(False))

        if tipo is None:
            self._entrada_nuevo_lote()
        else:
            self._movimiento_existente(tipo)

    def _movimiento_existente(self, tipo: TipoMovimiento):
        lote_id = self._select_lote()
        if lote_id is None:
            QMessageBox.warning(
                self, "Error", "Seleccione primero un lote en la tabla."
            )
            return

        lote = self.lote_repo.get(lote_id)
        if not lote:
            QMessageBox.warning(self, "Error", f"No existe el lote {lote_id}.")
            return

        dlg = MovimientoForm(
            self, tipo, necesita_fecha=False, show_med=False, show_lote=True
        )
        if dlg.cb_lote.count() == 0:
            dlg.cb_lote.addItem(f"{lote.codigo} (stock: {lote.stock})", lote.id)
        idx = next(
            i for i in range(dlg.cb_lote.count()) if dlg.cb_lote.itemData(i) == lote_id
        )
        dlg.cb_lote.setCurrentIndex(idx)

        if dlg.exec() != QtWidgets.QDialog.Accepted:
            return

        data = dlg.get_data()
        current = get_current_user()
        user_id = current.id if current else 1

        try:
            if tipo == TipoMovimiento.ENTRADA:
                self.inv.entrada(lote, data["cantidad"], data["motivo"], user_id)
            else:
                self.inv.salida(
                    lote.medicamento_id, data["cantidad"], data["motivo"], user_id
                )
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        else:
            QMessageBox.information(self, "OK", "Movimiento registrado")
            self._buscar_movimientos()

    def _entrada_nuevo_lote(self):
        dlg_med = BuscarMedicamentoDialog(self.medic_repo, self)
        if dlg_med.exec() != QtWidgets.QDialog.Accepted:
            return
        med_id = dlg_med.selected_id()
        if med_id is None:
            QMessageBox.warning(self, "Error", "Debe seleccionar un medicamento.")
            return

        dlg = MovimientoForm(
            self,
            TipoMovimiento.ENTRADA,
            necesita_fecha=True,
            show_med=False,
            show_lote=False,
        )
        if dlg.exec() != QtWidgets.QDialog.Accepted:
            return
        data = dlg.get_data()

        codigo, ok = QtWidgets.QInputDialog.getText(self, "Nuevo lote", "Código lote:")
        if not ok or not codigo.strip():
            return

        current = get_current_user()
        user_id = current.id if current else 1
        try:
            self.inv.entrada_nueva(
                codigo=codigo.strip(),
                medicamento_id=med_id,
                fecha_venc=data["fecha_venc"],
                cantidad=data["cantidad"],
                motivo=data["motivo"],
                usuario_id=user_id,
            )
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        else:
            QMessageBox.information(self, "OK", "Lote creado")
            self._buscar_movimientos()
