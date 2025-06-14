from PySide6 import QtWidgets

from core.services.catalog_service import CatalogService
from infrastructure.db import SessionLocal
from infrastructure.repos import MedicamentoRepo
from ui.widgets.medicamento_form import MedicamentoForm
from ui.widgets.medicamento_table import MedicamentoTableModel


class CatalogView(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.svc = CatalogService(MedicamentoRepo(SessionLocal()))

        # ─── tabla ──────────────────────────────────────────────
        self.table = QtWidgets.QTableView()
        self.model = MedicamentoTableModel()
        self.table.setModel(self.model)
        self.table.doubleClicked.connect(self._edit_current)

        # ─── botones ────────────────────────────────────────────
        btn_new = QtWidgets.QPushButton("Nuevo")
        btn_edit = QtWidgets.QPushButton("Editar")
        btn_del = QtWidgets.QPushButton("Eliminar")

        btn_new.clicked.connect(self._add)
        btn_edit.clicked.connect(self._edit_current)
        btn_del.clicked.connect(self._delete_current)

        h = QtWidgets.QHBoxLayout()
        h.addWidget(btn_new)
        h.addWidget(btn_edit)
        h.addWidget(btn_del)
        h.addStretch()

        v = QtWidgets.QVBoxLayout(self)
        v.addLayout(h)
        v.addWidget(self.table)

        self._refresh()

    # ─────────────────────────────────────────────────────────
    def _refresh(self):
        self.model.set_rows(list(self.svc.list()))
        self.table.resizeColumnsToContents()

    def _current_med(self):
        idx = self.table.currentIndex()
        if not idx.isValid():
            return None
        return self.model.item(idx.row())

    # CRUD actions
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
