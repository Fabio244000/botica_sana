from PySide6 import QtWidgets

from ui.widgets.alert_table import AlertTableModel


class AlertCenter(QtWidgets.QDialog):
    def __init__(self, data: dict[str, list]):
        super().__init__()
        self.setWindowTitle("Centro de alertas")
        self.resize(600, 400)

        tabs = QtWidgets.QTabWidget(self)

        tbl_stock = QtWidgets.QTableView()
        tbl_venc = QtWidgets.QTableView()

        tbl_stock.setModel(AlertTableModel(data["stock"]))
        tbl_venc.setModel(AlertTableModel(data["vencimiento"]))

        tabs.addTab(tbl_stock, f'Stock bajo ({len(data["stock"])})')
        tabs.addTab(tbl_venc, f'Por vencer ({len(data["vencimiento"])})')

        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(tabs)
