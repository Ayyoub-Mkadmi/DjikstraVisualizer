# launcher/main_menu.py
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

from src.gui.main_window import MainWindow
from src.gui2.djikstra_app import DijkstraApp
import networkx as nx
import tkinter as tk

def launch_main_window():
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

def launch_dijkstra_app():
    root = tk.Tk()
    G = nx.DiGraph()
    G.add_weighted_edges_from([(0, 1, 4), (0, 2, 1), (2, 1, 2), (1, 3, 1), (2, 3, 5)])
    app = DijkstraApp([(0, 1, 4), (0, 2, 1), (2, 1, 2), (1, 3, 1), (2, 3, 5)], 0)
    root.mainloop()

class MainMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dijkstra Visualizer - Menu")
        self.setGeometry(200, 200, 600, 400)

        layout = QVBoxLayout()

        title = QLabel("Choose a Mode")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 20))

        draw_button = QPushButton("🎨 Draw Graph")
        draw_button.setFixedHeight(50)
        draw_button.clicked.connect(launch_main_window)

        vis_button = QPushButton("🚀 Visualize Dijkstra")
        vis_button.setFixedHeight(50)
        vis_button.clicked.connect(launch_dijkstra_app)

        layout.addWidget(title)
        layout.addSpacing(30)
        layout.addWidget(draw_button)
        layout.addWidget(vis_button)

        avatar = QLabel()
        pixmap = QPixmap("assets/yassine.png").scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        avatar.setPixmap(pixmap)
        avatar.setAlignment(Qt.AlignCenter)

        layout.addStretch()
        layout.addWidget(avatar)

        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec_())
