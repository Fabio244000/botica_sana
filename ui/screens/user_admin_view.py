from PySide6 import QtCore, QtWidgets

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

        # Tabla de usuarios
        self.model = UserTableModel([])
        self.tbl = QtWidgets.QTableView()
        self.tbl.setModel(self.model)
        self.tbl.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tbl.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tbl.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        # Botones
        self.btn_new = QtWidgets.QPushButton("➕ Nuevo")
        self.btn_edit = QtWidgets.QPushButton("✏️ Editar")
        self.btn_del = QtWidgets.QPushButton("🗑️ Eliminar")
        self.btn_toggle = QtWidgets.QPushButton("🔄 Activar / Desactivar")

        for btn in (self.btn_new, self.btn_edit, self.btn_toggle):
            btn.setCheckable(True)
        self.btn_del.setObjectName("btn_danger")

        # Conexiones
        self.btn_new.clicked.connect(
            lambda: self._handle_action(self.btn_new, self._nuevo)
        )
        self.btn_edit.clicked.connect(
            lambda: self._handle_action(self.btn_edit, self._editar)
        )
        self.btn_del.clicked.connect(self._eliminar)
        self.btn_toggle.clicked.connect(
            lambda: self._handle_action(self.btn_toggle, self._toggle_activo)
        )

        # Estilos (igual que antes)
        self.setStyleSheet(
            """
            /* ... tu CSS ... */
        """
        )

        # Layouts
        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addStretch()
        top_layout.addWidget(self.btn_new)
        top_layout.addWidget(self.btn_edit)
        top_layout.addWidget(self.btn_del)
        top_layout.addWidget(self.btn_toggle)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.tbl)

        self._refresh()

    def _refresh(self):
        self.model.set_rows(self.svc.list_users())
        self.tbl.resizeColumnsToContents()

    def _selected_user(self):
        idx = self.tbl.selectionModel().currentIndex()
        if not idx.isValid():
            QtWidgets.QMessageBox.information(
                self, "Usuarios", "Seleccione un usuario."
            )
            return None
        return self.model.user_at(idx.row())

    def _handle_action(self, btn, action_func):
        # reset checks
        for b in (self.btn_new, self.btn_edit, self.btn_toggle):
            b.setChecked(False)
        btn.setChecked(True)
        QtCore.QTimer.singleShot(300, lambda: btn.setChecked(False))
        action_func()

    def _nuevo(self):
        dlg = UserForm(self, edit=False)
        if dlg.exec() != QtWidgets.QDialog.Accepted:
            return
        data = dlg.data()
        # Ahora pasamos todos los campos de una vez:
        self.svc.create_user(
            username=data["username"],
            password=data["password"],
            nombre_completo=data["nombre_completo"],
            dni=data["dni"],
            email=data["email"],
            celular=data["celular"],
            direccion=data["direccion"],
            rol=data["rol"],
            activo=data["activo"],
        )
        self._refresh()

    def _editar(self):
        u = self._selected_user()
        if not u:
            return
        dlg = UserForm(
            self,
            edit=True,
            username=u.username,
            email=u.email,
            celular=u.celular,
            direccion=u.direccion,
            nombre_completo=u.nombre_completo,
            dni=u.dni,
            rol=u.rol,
            activo=u.activo,
        )
        if dlg.exec() != QtWidgets.QDialog.Accepted:
            return
        data = dlg.data()
        # Cambiamos sólo lo que corresponda:
        if data["password"]:
            self.svc.change_password(u.id, data["password"])
        # Actualizamos los demás campos:
        u.username = data["username"]
        u.email = data["email"]
        u.celular = data["celular"]
        u.direccion = data["direccion"]
        u.nombre_completo = data["nombre_completo"]
        u.dni = data["dni"]
        u.rol = data["rol"]
        u.activo = data["activo"]
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
