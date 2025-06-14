from PySide6 import QtWidgets

from core.services.auth_service import AuthService
from infrastructure.db import SessionLocal
from infrastructure.hash_bcrypt import BcryptHasher
from infrastructure.repos import UsuarioRepo
from ui.screens.main_window import MainWindow
from ui.widgets.login_dialog import LoginDialog


def main():
    app = QtWidgets.QApplication([])

    # servicio auth
    auth = AuthService(UsuarioRepo(SessionLocal()), BcryptHasher())

    # dlg login
    login = LoginDialog(auth)
    if login.exec() != QtWidgets.QDialog.Accepted:
        return  # cierra la aplicación

    main_win = MainWindow()
    main_win.show()

    app.exec()


if __name__ == "__main__":
    main()
