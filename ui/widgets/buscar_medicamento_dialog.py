from PySide6 import QtWidgets
from PySide6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QLineEdit,
                               QListWidget, QListWidgetItem, QPushButton,
                               QVBoxLayout)

from infrastructure.repos import MedicamentoRepo


class BuscarMedicamentoDialog(QDialog):
    """Diálogo para buscar y seleccionar un medicamento."""

    def __init__(self, medic_repo: MedicamentoRepo, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Buscar medicamento")
        self.setModal(True)
        self.resize(400, 300)

        # Mapeo label → id
        self._meds = list(medic_repo.list())
        self._map = {f"{m.codigo} – {m.nombre}": m.id for m in self._meds}

        # Widgets
        self.input = QLineEdit(self)
        self.input.setPlaceholderText("Escribe código o nombre…")
        self.list = QListWidget(self)
        for label in self._map:
            self.list.addItem(QListWidgetItem(label))

        # Filtrado en tiempo real
        self.input.textChanged.connect(self._filtrar)

        btn_ok = QPushButton("Aceptar", self)
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Cancelar", self)
        btn_cancel.clicked.connect(self.reject)

        btns = QHBoxLayout()
        btns.addStretch()
        btns.addWidget(btn_ok)
        btns.addWidget(btn_cancel)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Buscar medicamento"))
        layout.addWidget(self.input)
        layout.addWidget(self.list)
        layout.addLayout(btns)

    def _filtrar(self, txt: str):
        txt = txt.lower()
        for i in range(self.list.count()):
            item = self.list.item(i)
            item.setHidden(txt not in item.text().lower())

    def selected_id(self) -> int | None:
        it = self.list.currentItem()
        return self._map.get(it.text()) if it else None
