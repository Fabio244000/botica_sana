from PySide6 import QtWidgets

from core.services.auth_service import AuthService
from infrastructure.db import SessionLocal
from infrastructure.hash_bcrypt import BcryptHasher
from infrastructure.repos import UsuarioRepo
from ui.widgets.user_form import UserForm
from ui.widgets.user_table import UserTableModel


class UserAdminView(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.svc = AuthService(UsuarioRepo(SessionLocal()), BcryptHasher())

        self.model = UserTableModel([])
        self.tbl = QtWidgets.QTableView()
        self.tbl.setModel(self.model)
        self.tbl.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tbl.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tbl.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        btn_new = QtWidgets.QPushButton("Nuevo")
        btn_edit = QtWidgets.QPushButton("Editar")
        btn_del = QtWidgets.QPushButton("Eliminar")
        btn_toggle = QtWidgets.QPushButton("Activar / Desactivar")

        btn_new.clicked.connect(self._nuevo)
        btn_edit.clicked.connect(self._editar)
        btn_del.clicked.connect(self._eliminar)
        btn_toggle.clicked.connect(self._toggle_activo)

        h = QtWidgets.QHBoxLayout()
        h.addWidget(btn_new)
        h.addWidget(btn_edit)
        h.addWidget(btn_del)
        h.addWidget(btn_toggle)
        h.addStretch()

        v = QtWidgets.QVBoxLayout(self)
        v.addLayout(h)
        v.addWidget(self.tbl)

        self._refresh()

    # --------------------------------------------------------------
    def _refresh(self):
        self.model.set_rows(self.svc.list_users())
        self.tbl.resizeColumnsToContents()

    def _selected_user(self):
        # usa el modelo de selección en lugar de currentIndex()
        idx = self.tbl.selectionModel().currentIndex()
        if not idx.isValid():
            QtWidgets.QMessageBox.information(
                self, "Usuarios", "Seleccione un usuario."
            )
            return None
        return self.model.user_at(idx.row())

    # botones ------------------------------------------------------
    def _nuevo(self):
        dlg = UserForm(self)
        if dlg.exec() != QtWidgets.QDialog.Accepted:
            return
        d = dlg.data()
        self.svc.create_user(d["username"], d["password"], d["rol"])
        self._refresh()

    def _editar(self):
        u = self._selected_user()
        if not u:
            return
        dlg = UserForm(self, edit=True, username=u.username, rol=u.rol)
        if dlg.exec() != QtWidgets.QDialog.Accepted:
            return
        d = dlg.data()
        if d["password"]:
            self.svc.change_password(u.id, d["password"])
        if d["rol"] != u.rol:
            u.rol = d["rol"]
            self.svc._repo.add(u)
        self._refresh()

    def _eliminar(self):
        u = self._selected_user()
        if not u:
            return
        if (
            QtWidgets.QMessageBox.question(
                self, "Eliminar", f"¿Borrar al usuario {u.username}?"
            )
            != QtWidgets.QMessageBox.Yes
        ):
            return
        self.svc.delete_user(u.id)
        self._refresh()

    def _toggle_activo(self):
        u = self._selected_user()
        if not u:
            return
        self.svc.set_active(u.id, not u.activo)
        self._refresh()
