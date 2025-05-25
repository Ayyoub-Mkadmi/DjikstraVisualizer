from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class GraphSelectionDialog(QDialog):
    def __init__(self, graph_names, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sélectionner un graphe prédéfini")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        label = QLabel("Choisissez un graphe prédéfini :")
        label.setFont(QFont("Arial", 12))
        layout.addWidget(label)

        self.list_widget = QListWidget()
        self.list_widget.setFont(QFont("Arial", 11))
        self.list_widget.addItems(graph_names)
        self.list_widget.setSpacing(6)
        layout.addWidget(self.list_widget)

        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Annuler")
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

    def get_selected_graph(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            return selected_items[0].text()
        return None
