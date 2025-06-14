from PySide6 import QtCore, QtWidgets


class LoginWindow(QtWidgets.QMainWindow):
    """
    Ventana de inicio de sesión muy simple.
    Emite la señal `logged_in` cuando el usuario pulsa “Entrar”.
    """

    logged_in = QtCore.Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Botica Sana – Login")
        self.setFixedSize(300, 160)

        # ----- UI mínima en código -----
        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)
        lay = QtWidgets.QVBoxLayout(central)

        self.le_user = QtWidgets.QLineEdit(placeholderText="Usuario")
        self.le_pass = QtWidgets.QLineEdit(placeholderText="Contraseña")
        self.le_pass.setEchoMode(QtWidgets.QLineEdit.Password)

        self.btn_login = QtWidgets.QPushButton("Entrar")
        self.btn_login.clicked.connect(self._handle_login)

        lay.addStretch()
        lay.addWidget(self.le_user)
        lay.addWidget(self.le_pass)
        lay.addWidget(self.btn_login)
        lay.addStretch()

    # ──────────────────────────────────────────────────────────────
    def _handle_login(self) -> None:
        """
        Aquí integrarás AuthService.
        Por ahora siempre pasa.
        """
        # TODO: validar contra AuthService
        self.logged_in.emit()
