from PySide6 import QtWidgets

from core.models.rol import Rol


class UserForm(QtWidgets.QDialog):
    """Alta / edición de usuario."""

    def __init__(self, parent=None, *, edit=False, username="", rol=Rol.CAJERO):
        super().__init__(parent)
        self.setWindowTitle("Editar usuario" if edit else "Nuevo usuario")
        self.setModal(True)

        self.le_user = QtWidgets.QLineEdit(username)
        self.le_pass = QtWidgets.QLineEdit()
        self.le_pass.setEchoMode(QtWidgets.QLineEdit.Password)
        if edit:
            self.le_pass.setPlaceholderText("(dejar vacío para no cambiar)")

        self.cb_rol = QtWidgets.QComboBox()
        self.cb_rol.addItems([r.value for r in Rol])
        self.cb_rol.setCurrentText(rol.value)

        form = QtWidgets.QFormLayout()
        form.addRow("Usuario", self.le_user)
        form.addRow("Password", self.le_pass)
        form.addRow("Rol", self.cb_rol)

        btn_ok = QtWidgets.QPushButton("Aceptar")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QtWidgets.QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)

        h = QtWidgets.QHBoxLayout()
        h.addStretch()
        h.addWidget(btn_ok)
        h.addWidget(btn_cancel)

        v = QtWidgets.QVBoxLayout(self)
        v.addLayout(form)
        v.addLayout(h)

    # datos resultantes -------------------------------------------------
    def data(self):
        return {
            "username": self.le_user.text().strip(),
            "password": self.le_pass.text(),
            "rol": Rol(self.cb_rol.currentText()),
        }
