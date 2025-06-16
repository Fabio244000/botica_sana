# ui/screens/alert_center.py

from datetime import date
from pathlib import Path

from PySide6 import QtGui, QtWidgets

from ui.widgets.alert_table import AlertTableModel


class AlertCenter(QtWidgets.QDialog):
    def __init__(self, data: dict[str, list]):
        super().__init__()
        self.setWindowTitle("Centro de alertas")
        self.resize(700, 450)

        # Icono
        icon_path = Path(__file__).parent.parent / "assets/icons/botica_sana_logo.png"
        self.setWindowIcon(QtGui.QIcon(str(icon_path)))

        # Estilos
        self.setStyleSheet(
            """
            QTabWidget::pane {
                border: 1px solid #ccc;
                border-radius: 6px;
                margin: 6px;
            }
            QTabBar::tab {
                background: #f0f0f0;
                padding: 8px 20px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 14px;
            }
            QTabBar::tab:selected {
                background: #3f51b5;
                color: white;
                font-weight: bold;
            }
            QTableView {
                font-size: 13px;
            }
        """
        )

        # Pestañas
        tabs = QtWidgets.QTabWidget(self)

        # Filtrar stock bajo (<= 5)
        low_stock = [l for l in data.get("stock", []) if l.stock <= 5]

        # Filtrar por vencer (<= 30 días)
        soon_expire = [
            l
            for l in data.get("vencimiento", [])
            if (l.fecha_vencimiento - date.today()).days <= 30
        ]

        # Tabla stock bajo
        tbl_stock = QtWidgets.QTableView()
        stock_model = AlertTableModel(low_stock)
        tbl_stock.setModel(stock_model)
        tbl_stock.resizeColumnsToContents()

        # Tabla por vencer
        tbl_venc = QtWidgets.QTableView()
        venc_model = AlertTableModel(soon_expire)
        tbl_venc.setModel(venc_model)
        tbl_venc.resizeColumnsToContents()

        tabs.addTab(tbl_stock, f"Stock bajo ({len(low_stock)})")
        tabs.addTab(tbl_venc, f"Por vencer ({len(soon_expire)})")

        # Layout
        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(12)
        lay.addWidget(tabs)
