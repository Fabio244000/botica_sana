from PySide6 import QtCore, QtGui, QtWidgets


class Toast(QtWidgets.QLabel):
    """
    Pequeña notificación flotante que se desvanece sola.

    Uso:
        Toast.show_("Medicamento creado", parent=self)
    """

    def __init__(self, text: str, parent: QtWidgets.QWidget | None = None):
        # ➊ Llamada correcta: primero parent, luego flags (sin keyword argument)
        super().__init__(parent, QtCore.Qt.ToolTip)
        self.setText(text)

        # ➋ Estilos
        self.setStyleSheet(
            """
            QLabel {
                background: rgba(60, 60, 60, 200);
                color: white;
                padding: 8px 14px;
                border-radius: 8px;
                font-size: 13px;
            }
            """
        )
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.adjustSize()  # calcula tamaño tras setText

        # ➌ Posición: centrado horizontal, 40 px arriba del borde inferior
        if parent:
            geo = parent.geometry()
        else:
            geo = QtGui.QGuiApplication.primaryScreen().geometry()

        x = geo.center().x() - self.width() // 2
        y = geo.bottom() - self.height() - 40
        self.move(x, y)

        # ➍ Se destruye solo tras 2,5 s
        QtCore.QTimer.singleShot(2500, self.close)

    # Helper estático
    @staticmethod
    def show_(text: str, parent: QtWidgets.QWidget | None = None):
        Toast(text, parent).show()
