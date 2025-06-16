from pydantic import SecretStr
from PySide6 import QtWidgets
from PySide6.QtCore import QRegularExpression, Qt
from PySide6.QtGui import QRegularExpressionValidator

from core.models.rol import Rol
from core.models.usuario import Usuario


class UserForm(QtWidgets.QDialog):
    """Alta / edición de usuario con validación en el formulario."""

    def __init__(
        self,
        parent=None,
        *,
        edit: bool = False,
        username: str = "",
        email: str = "",
        celular: str = "",
        direccion: str = "",
        nombre_completo: str = "",
        dni: str = "",
        rol: Rol = Rol.CAJERO,
        activo: bool = True,
    ):
        super().__init__(parent)
        self.setWindowTitle("Editar usuario" if edit else "Nuevo usuario")
        self.setModal(True)
        self._edit = edit

        # Campos básicos
        self.le_user = QtWidgets.QLineEdit(username)
        self.le_pass = QtWidgets.QLineEdit()
        self.le_pass.setEchoMode(QtWidgets.QLineEdit.Password)
        if edit:
            self.le_pass.setPlaceholderText("(dejar vacío para no cambiar)")

        # Nuevos campos
        self.le_nombre = QtWidgets.QLineEdit(nombre_completo)
        self.le_dni = QtWidgets.QLineEdit(dni)
        # Validador: alfanumérico, hasta 12 caracteres
        regex = QRegularExpression(r"^[A-Za-z0-9]{0,12}$")
        self.le_dni.setValidator(QRegularExpressionValidator(regex, self))

        self.le_email = QtWidgets.QLineEdit(email)
        self.le_celular = QtWidgets.QLineEdit(celular)
        self.le_direccion = QtWidgets.QLineEdit(direccion)

        self.cb_rol = QtWidgets.QComboBox()
        self.cb_rol.addItems([r.value for r in Rol])
        self.cb_rol.setCurrentText(rol.value)

        self.chk_activo = QtWidgets.QCheckBox("Activo")
        self.chk_activo.setChecked(activo)

        # Layout
        form = QtWidgets.QFormLayout()
        form.addRow("Usuario*", self.le_user)
        form.addRow("Password", self.le_pass)
        form.addRow("Nombre completo*", self.le_nombre)
        form.addRow("DNI", self.le_dni)
        form.addRow("Email*", self.le_email)
        form.addRow("Celular*", self.le_celular)
        form.addRow("Dirección*", self.le_direccion)
        form.addRow("Rol", self.cb_rol)
        form.addRow("", self.chk_activo)

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

    def accept(self) -> None:
        # Campos obligatorios
        if not self.le_user.text().strip():
            QtWidgets.QMessageBox.warning(
                self, "Error", "El nombre de usuario es obligatorio."
            )
            return
        if not self.le_nombre.text().strip():
            QtWidgets.QMessageBox.warning(
                self, "Error", "El nombre completo es obligatorio."
            )
            return
        if not self.le_email.text().strip():
            QtWidgets.QMessageBox.warning(self, "Error", "El email es obligatorio.")
            return
        if not self.le_celular.text().strip():
            QtWidgets.QMessageBox.warning(self, "Error", "El celular es obligatorio.")
            return
        if not self.le_direccion.text().strip():
            QtWidgets.QMessageBox.warning(self, "Error", "La dirección es obligatoria.")
            return

        pwd = self.le_pass.text().strip()
        # Si es creación o si se ingresó nueva contraseña al editar:
        if not self._edit or pwd:
            try:
                # Validar con Pydantic: disparará ValueError si no cumple
                Usuario(
                    username=self.le_user.text().strip(),
                    password=SecretStr(pwd),
                    email=self.le_email.text().strip(),
                    celular=self.le_celular.text().strip(),
                    direccion=self.le_direccion.text().strip(),
                    nombre_completo=self.le_nombre.text().strip(),
                    dni=self.le_dni.text().strip() or None,
                    rol=Rol(self.cb_rol.currentText()),
                    activo=self.chk_activo.isChecked(),
                )
            except ValueError as e:
                QtWidgets.QMessageBox.warning(self, "Error de validación", str(e))
                return

        super().accept()

    def data(self) -> dict:
        return {
            "username": self.le_user.text().strip(),
            "password": self.le_pass.text(),
            "nombre_completo": self.le_nombre.text().strip(),
            "dni": self.le_dni.text().strip() or None,
            "email": self.le_email.text().strip(),
            "celular": self.le_celular.text().strip(),
            "direccion": self.le_direccion.text().strip(),
            "rol": Rol(self.cb_rol.currentText()),
            "activo": self.chk_activo.isChecked(),
        }
