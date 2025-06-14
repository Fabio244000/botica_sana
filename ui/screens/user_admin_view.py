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

        for btn in [self.btn_new, self.btn_edit, self.btn_toggle]:
            btn.setCheckable(True)
        self.btn_del.setObjectName("btn_danger")

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

        # ─── Estilos ─────────────────────────────
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

        self.tbl.setAlternatingRowColors(True)
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.horizontalHeader().setStretchLastSection(True)

        # ─── Layout superior ─────────────────────
        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addStretch()
        top_layout.addWidget(self.btn_new)
        top_layout.addWidget(self.btn_edit)
        top_layout.addWidget(self.btn_del)
        top_layout.addWidget(self.btn_toggle)

        # ─── Layout principal ─────────────────────
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.tbl)

        self._refresh()

    # ─────────────────────────────────────────────
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
        self.btn_new.setChecked(False)
        self.btn_edit.setChecked(False)
        self.btn_toggle.setChecked(False)

        btn.setChecked(True)
        QtCore.QTimer.singleShot(300, lambda: btn.setChecked(False))
        action_func()

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
