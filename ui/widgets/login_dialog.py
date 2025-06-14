from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets

from core.services.auth_service import AuthService
from infrastructure.auth_context import get_current_user


class LoginDialog(QtWidgets.QDialog):
    """Diálogo moderno de inicio de sesión."""

    def __init__(self, auth: AuthService, parent=None):
        super().__init__(parent)
        self._auth = auth
        self.setWindowTitle("Iniciar sesión")
        self.setFixedSize(600, 300)
        self.setModal(True)

        # Ruta absoluta del ícono
        icon_path = Path(__file__).parent.parent / "assets/icons/botica_sana_logo.png"
        self.setWindowIcon(QtGui.QIcon(str(icon_path)))

        self.setStyleSheet(
            """
            QLabel#title_label {
                font-size: 20px;
                font-weight: bold;
                padding-bottom: 10px;
            }
            QLabel {
                font-size: 15px;
            }
            QLineEdit {
                padding: 10px 14px;
                border: 1px solid #555;
                border-radius: 6px;
                font-size: 15px;
            }
            QPushButton {
                min-width: 100px;
                min-height: 38px;
                font-size: 15px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton#btn_ok {
                background-color: #2a82da;
                color: white;
            }
            QPushButton#btn_cancel {
                background-color: #444;
                color: white;
            }
        """
        )

        # Título
        title_label = QtWidgets.QLabel("Sistema de Gestión de Inventario – Botica Sana")
        title_label.setObjectName("title_label")
        title_label.setAlignment(QtCore.Qt.AlignCenter)

        # Entradas
        self.le_user = QtWidgets.QLineEdit()
        self.le_user.setPlaceholderText("Ingrese su usuario")

        self.le_pass = QtWidgets.QLineEdit()
        self.le_pass.setPlaceholderText("Ingrese su contraseña")
        self.le_pass.setEchoMode(QtWidgets.QLineEdit.Password)

        form = QtWidgets.QFormLayout()
        form.setSpacing(18)
        form.addRow("Usuario:", self.le_user)
        form.addRow("Contraseña:", self.le_pass)

        self.btn_ok = QtWidgets.QPushButton("Entrar")
        self.btn_ok.setObjectName("btn_ok")
        self.btn_ok.clicked.connect(self._login)

        self.btn_cancel = QtWidgets.QPushButton("Salir")
        self.btn_cancel.setObjectName("btn_cancel")
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addStretch()

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(50, 25, 50, 25)
        main_layout.addWidget(title_label)
        main_layout.addSpacing(12)
        main_layout.addLayout(form)
        main_layout.addSpacing(20)
        main_layout.addLayout(btn_layout)

        self.le_user.returnPressed.connect(self._login)
        self.le_pass.returnPressed.connect(self._login)

    def _login(self):
        username = self.le_user.text().strip()
        password = self.le_pass.text().strip()

        if not username or not password:
            QtWidgets.QMessageBox.warning(
                self, "Campos requeridos", "Ingrese usuario y contraseña."
            )
            return

        try:
            user = self._auth.login(username, password)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error de autenticación", str(e))
            return

        self.accept()

    def user(self):
        return get_current_user()
