from pathlib import Path

from PySide6.QtWidgets import QApplication


def apply_theme(app: QApplication, dark: bool = True) -> None:
    """
    Aplica estilo Fusion y carga un QSS.
    Si el archivo no existe, solo cambia el estilo.
    """
    QApplication.setStyle("Fusion")
    qss_file = Path("ui/style_dark.qss" if dark else "ui/style_light.qss")
    if qss_file.exists():
        app.setStyleSheet(qss_file.read_text(encoding="utf-8"))
