from PySide6 import QtCore, QtWidgets

from core.services.catalog_service import CatalogService
from infrastructure.db import SessionLocal
from infrastructure.repos import MedicamentoRepo
from ui.widgets.medicamento_form import MedicamentoForm
from ui.widgets.medicamento_table import MedicamentoTableModel


class CatalogView(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.svc = CatalogService(MedicamentoRepo(SessionLocal()))

        # ─── Tabla ──────────────────────────────────────────────
        self.table = QtWidgets.QTableView()
        self.model = MedicamentoTableModel()
        self.table.setModel(self.model)
        self.table.doubleClicked.connect(self._edit_current)

        # Mejora visual
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("QTableView::item:focus { outline: none; }")
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )

        # ─── Botones ─────────────────────────────────────────────
        self.btn_new = QtWidgets.QPushButton("➕ Nuevo")
        self.btn_edit = QtWidgets.QPushButton("✏️ Editar")
        self.btn_del = QtWidgets.QPushButton("🗑️ Eliminar")

        self.btn_new.setCheckable(True)
        self.btn_edit.setCheckable(True)
        self.btn_del.setObjectName("btn_danger")

        # Lógica de acción con resaltado
        self.btn_new.clicked.connect(
            lambda: self._handle_action(self.btn_new, self._add)
        )
        self.btn_edit.clicked.connect(
            lambda: self._handle_action(self.btn_edit, self._edit_current)
        )
        self.btn_del.clicked.connect(self._delete_current)

        # ─── Layout superior ─────────────────────────────────────
        top = QtWidgets.QHBoxLayout()
        top.addStretch()
        top.addWidget(self.btn_new)
        top.addWidget(self.btn_edit)
        top.addWidget(self.btn_del)

        # ─── Layout principal ────────────────────────────────────
        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.table)

        # ─── Estilos ─────────────────────────────────────────────
        self.setStyleSheet(
            """
            QPushButton {
                padding: 8px 24px;
                min-width: 90px;
                border-radius: 6px;
                font-size: 14px;
                background-color: #e0e0e0;
            }

            QPushButton:hover {
                background-color: #d5d5d5;
            }

            QPushButton:pressed {
                background-color: #c0c0c0;
            }

            QPushButton:checked {
                background-color: #3f51b5;
                border: 2px solid #303f9f;
                font-weight: bold;
                color: white;
                min-width: 90px;
            }

            QPushButton#btn_danger {
                background-color: #e53935;
                color: white;
            }

            QPushButton#btn_danger:hover {
                background-color: #c62828;
            }

            QPushButton#btn_danger:pressed {
                background-color: #b71c1c;
            }

            QHeaderView::section {
                background-color: #f5f5f5;
                color: #333;
                padding: 6px;
                font-weight: bold;
                border-bottom: 1px solid #ccc;
            }

            QTableView {
                gridline-color: #eee;
                selection-background-color: #c5cae9;
                selection-color: #000;
                alternate-background-color: #fafafa;
            }

            QTableView::item {
                padding: 6px;
            }

            QTableView::item:selected {
                background-color: #c5cae9;
                color: black;
            }
        """
        )

        self._refresh()

    # ─────────────────────────────────────────────────────────────
    def _refresh(self):
        self.model.set_rows(list(self.svc.list()))
        self.table.resizeColumnsToContents()

    def _current_med(self):
        idx = self.table.currentIndex()
        if not idx.isValid():
            return None
        return self.model.item(idx.row())

    # ─── CRUD actions ─────────────────────────────────────────────
    def _add(self):
        dlg = MedicamentoForm(self)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            self.svc.add(dlg.get_data())
            self._refresh()

    def _edit_current(self):
        med = self._current_med()
        if not med:
            return
        dlg = MedicamentoForm(self, med)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            self.svc.update(med.id, dlg.get_data().model_dump(exclude={"id"}))
            self._refresh()

    def _delete_current(self):
        med = self._current_med()
        if not med:
            return
        if (
            QtWidgets.QMessageBox.question(
                self,
                "Eliminar",
                f"¿Eliminar {med.nombre}?",
            )
            == QtWidgets.QMessageBox.Yes
        ):
            self.svc.delete(med.id)
            self._refresh()

    # ─── Manejo visual de botones activos ─────────────────────────
    def _handle_action(self, button, action_func):
        self.btn_new.setChecked(False)
        self.btn_edit.setChecked(False)
        button.setChecked(True)
        action_func()
        button.setChecked(False)
