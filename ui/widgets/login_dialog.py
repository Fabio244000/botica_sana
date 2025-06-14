from PySide6 import QtWidgets

from core.services.auth_service import AuthService
from infrastructure.auth_context import get_current_user


class LoginDialog(QtWidgets.QDialog):
    """Diálogo modal de acceso."""

    def __init__(self, auth: AuthService, parent=None):
        super().__init__(parent)
        self._auth = auth
        self.setWindowTitle("Iniciar sesión")
        self.setModal(True)

        self.le_user = QtWidgets.QLineEdit()
        self.le_pass = QtWidgets.QLineEdit()
        self.le_pass.setEchoMode(QtWidgets.QLineEdit.Password)

        form = QtWidgets.QFormLayout()
        form.addRow("Usuario", self.le_user)
        form.addRow("Contraseña", self.le_pass)

        btn_ok = QtWidgets.QPushButton("Entrar")
        btn_ok.clicked.connect(self._login)
        btn_cancel = QtWidgets.QPushButton("Salir")
        btn_cancel.clicked.connect(self.reject)

        h = QtWidgets.QHBoxLayout()
        h.addStretch()
        h.addWidget(btn_ok)
        h.addWidget(btn_cancel)

        v = QtWidgets.QVBoxLayout(self)
        v.addLayout(form)
        v.addLayout(h)

    # ----------------------------------------------------------
    def _login(self):
        if self._auth.login(self.le_user.text(), self.le_pass.text()):
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(self, "Acceso", "Credenciales inválidas")

    # helper para obtener al usuario conectado
    def user(self):
        return get_current_user()
