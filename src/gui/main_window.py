import ast
import math
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QCheckBox, QLabel, QMessageBox,
    QGroupBox, QFrame , QInputDialog, QDialog,QPlainTextEdit,QApplication,QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from src.gui2.djikstra_app import DijkstraApp
from src.gui.graph_selection_dialog import GraphSelectionDialog
from src.gui.help_dialog import HelpDialog
from .graph_canvas import GraphCanvas


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visualiseur de Dijkstra")
        screen = QApplication.primaryScreen()
        geometry = screen.availableGeometry()
        self.setGeometry(geometry)        
        # Apply modern styling
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
            QCheckBox {
                font-size: 13px;
                padding: 6px 0;
                spacing: 8px;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(15)

        # === Left Side Panel ===
        side_panel = QVBoxLayout()
        side_panel.setSpacing(12)
        side_panel.setContentsMargins(0, 0, 0, 0)

        # Title with help button
        title_layout = QHBoxLayout()
        title = QLabel("Visualiseur de Dijkstra")
        title.setFont(QFont('Segoe UI', 18, QFont.Bold))
        title.setStyleSheet("color: #202124;")
        
        help_btn = QPushButton("?")
        help_btn.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                border-radius: 12px;
                min-width: 24px;
                max-width: 24px;
                min-height: 24px;
                max-height: 24px;
                padding: 0px;
                background-color: #f1c40f;
                color: #2c3e50;
            }
            QPushButton:hover {
                background-color: #f39c12;
            }
        """)
        help_btn.clicked.connect(self.show_help)
        
        title_layout.addWidget(title)
        title_layout.addWidget(help_btn)
        title_layout.addStretch()
        
        side_panel.addLayout(title_layout)
        side_panel.addSpacing(10)

        # Rest of your existing panel code...
        # Graph Import Group
        import_group = QGroupBox("Importer des Graphes")
        import_layout = QVBoxLayout()
        
        # Predefined graphs
        predefined_btn = QPushButton("Charger un Graphe")
        predefined_btn.clicked.connect(self.show_predefined_graphs)
        import_layout.addWidget(predefined_btn)
        
        # Custom graph input
        custom_btn = QPushButton("Graphe Personnalisé")
        custom_btn.clicked.connect(self.import_custom_graph)
        import_layout.addWidget(custom_btn)
        
        import_group.setLayout(import_layout)
        side_panel.addWidget(import_group)

        # Tool Selection Group
        tool_group = QGroupBox("Sélection de l’outil")
        tool_layout = QVBoxLayout()
        
        self.eraser_cb = QCheckBox("Mode Gomme")
        tool_layout.addWidget(self.eraser_cb)
        tool_group.setLayout(tool_layout)
        side_panel.addWidget(tool_group)

        # Graph Options Group
        options_group = QGroupBox("Options du graphe")
        options_layout = QVBoxLayout()
        
        self.allow_loops_cb = QCheckBox("Autoriser les boucles")
        self.allow_duplicates_cb = QCheckBox("Autoriser les arcs en double")
        
        self.allow_loops_cb.setChecked(True)
        self.allow_duplicates_cb.setChecked(True)
        
        options_layout.addWidget(self.allow_loops_cb)
        options_layout.addWidget(self.allow_duplicates_cb)
        options_group.setLayout(options_layout)
        side_panel.addWidget(options_group)

        # Export Button
        export_btn = QPushButton("Exporter le graphe")
        export_btn.clicked.connect(self.export_graph)
        export_btn.setStyleSheet("margin-top: 15px;")
        side_panel.addWidget(export_btn)

        # Start Button
        start_btn = QPushButton("Demarrer Djikstra")
        start_btn.clicked.connect(self.start_dijkstra)
        start_btn.setStyleSheet("margin-top: 15px;")
        side_panel.addWidget(start_btn)

        side_panel.addStretch()
        layout.addLayout(side_panel, stretch=1)

        # Add a vertical separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #e0e0e0;")
        layout.addWidget(separator)

        # === Graph Canvas ===
        self.canvas = GraphCanvas()
        layout.addWidget(self.canvas, stretch=4)

        # Connect signals
        self.eraser_cb.stateChanged.connect(self.update_canvas_config)
        self.allow_loops_cb.stateChanged.connect(self.update_canvas_config)
        self.allow_duplicates_cb.stateChanged.connect(self.update_canvas_config)

        self.update_canvas_config()

    def update_canvas_config(self):
        self.canvas.set_config(
            eraser_mode=self.eraser_cb.isChecked(),
            allow_loops=self.allow_loops_cb.isChecked(),
            allow_duplicate_edges=self.allow_duplicates_cb.isChecked()
        )

    def export_graph(self):
        """Export the current graph and display it in a copyable dialog."""
        edges = self.canvas.export_graph()
        formatted_text = str(edges)

        dialog = QDialog(self)
        dialog.setWindowTitle("Exporter le graphe")
        dialog.setMinimumWidth(500)

        layout = QVBoxLayout(dialog)

        title = QLabel("Voici la structure actuelle du graphe :")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        text_edit = QPlainTextEdit()
        text_edit.setPlainText(formatted_text)
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Courier New", 10))
        text_edit.setStyleSheet("background-color: #f8f8f8; padding: 10px; border: 1px solid #ccc;")
        layout.addWidget(text_edit)

        button_box = QHBoxLayout()

        copy_button = QPushButton("📋 Copier")
        copy_button.setStyleSheet("padding: 6px 12px; font-weight: bold;")
        copy_button.clicked.connect(lambda: QApplication.clipboard().setText(formatted_text))

        close_button = QPushButton("❌ Fermer")
        close_button.setStyleSheet("padding: 6px 12px;")
        close_button.clicked.connect(dialog.close)

        button_box.addWidget(copy_button)
        button_box.addStretch()
        button_box.addWidget(close_button)

        layout.addLayout(button_box)

        dialog.exec_()


    def start_dijkstra(self):
        edges = self.canvas.export_graph()
        if not edges:
            QMessageBox.warning(self, "Erreur", "Le graphe est vide.")
            return

        # Get all unique node indices from edges
        node_set = set()
        for u, v, _ in edges:
            node_set.add(u)
            node_set.add(v)
        node_list = sorted(node_set)

        formatted_text = str(edges)

        dialog = QDialog(self)
        dialog.setWindowTitle("Démarrer l'algorithme de Dijkstra")
        dialog.setMinimumWidth(550)
        dialog.setWindowFlag(Qt.WindowStaysOnTopHint, True)

        layout = QVBoxLayout(dialog)

        title = QLabel("Structure actuelle du graphe :")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)

        text_edit = QPlainTextEdit()
        text_edit.setPlainText(formatted_text)
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Courier New", 11))
        text_edit.setStyleSheet("background-color: #f8f8f8; padding: 10px; border: 1px solid #ccc; font-size: 13px;")
        layout.addWidget(text_edit)

        # Source selection
        source_label = QLabel("Choisissez le sommet source :")
        source_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(source_label)

        from PyQt5.QtWidgets import QComboBox
        source_combo = QComboBox()
        source_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                font-size: 14px;
                min-width: 150px;
            }
        """)
        for node in node_list:
            source_combo.addItem(str(node))

        # Add combo box with spacing above and below
        combo_layout = QHBoxLayout()
        combo_layout.addStretch()
        combo_layout.addWidget(source_combo)
        combo_layout.addStretch()
        layout.addLayout(combo_layout)

        # Buttons
        button_box = QHBoxLayout()

        close_button = QPushButton("❌ Fermer")
        close_button.setStyleSheet("padding: 8px 16px; font-size: 13px;")
        close_button.clicked.connect(dialog.close)

        start_button = QPushButton("🚀 Lancer Dijkstra")
        start_button.setStyleSheet("padding: 8px 16px; font-size: 13px; font-weight: bold;")
        
        def on_start():
            try:
                source = int(source_combo.currentText())
                print(f"Dialog result: ok=True, source={source}")  # Debug
                self.dijkstra_app = DijkstraApp(edges, source, parent=None)
                self.dijkstra_app.run()
                if hasattr(self.dijkstra_app, "visualizer"):
                    vis = self.dijkstra_app.visualizer
                    vis.setWindowFlag(Qt.WindowStaysOnTopHint, True)
                    vis.show()
                    vis.raise_()
                    vis.activateWindow()
                dialog.close()
            except Exception as e:
                print(f"Exception: {e}")
                QMessageBox.critical(dialog, "Erreur", f"Une erreur est survenue:\n{str(e)}")

        start_button.clicked.connect(on_start)

        # Button positions: cancel left, launch right
        button_box.addWidget(close_button)
        button_box.addStretch()
        button_box.addWidget(start_button)

        layout.addSpacing(10)
        layout.addLayout(button_box)

        dialog.exec_()

    def show_predefined_graphs(self):
        # Define some sample graphs
        predefined_graphs = {
            # Simple connected graph
            "Linéaire à 3 nœuds": [
                (0, 1, 4),
                (1, 2, 5)
            ],

            # Small graph with multiple shortest paths
            "4 nœuds avec chemins multiples": [
                (0, 1, 1),
                (1, 3, 2),
                (0, 2, 1),
                (2, 3, 2)
            ],

            # Star topology
            "Étoile à 5 nœuds": [
                (0, 1, 2),
                (0, 2, 2),
                (0, 3, 2),
                (0, 4, 2)
            ],

            # Fully connected small graph (dense)
            "Complet à 6 nœuds": [
                (0, 1, 1),
                (0, 2, 5),
                (0, 3, 3),
                (0, 4, 2),
                (0, 5, 4),
                (1, 2, 2),
                (1, 3, 4),
                (1, 4, 3),
                (1, 5, 2),
                (2, 3, 1),
                (2, 4, 2),
                (2, 5, 3),
                (3, 4, 2),
                (3, 5, 1),
                (4, 5, 2)
            ],

            # Graph with cycles
            "Cycle à 6 nœuds": [
                (0, 1, 1),
                (1, 2, 1),
                (2, 3, 1),
                (3, 4, 1),
                (4, 5, 1),
                (5, 0, 1)
            ],

            

            # Graph with zero-weight edges
            "Arêtes de poids zéro": [
                (0, 1, 0),
                (1, 2, 0),
                (2, 3, 1),
                (3, 4, 2)
            ],

            # Dead-end path
            "Chemin sans issue": [
                (0, 1, 1),
                (1, 2, 1),
                (2, 3, 1),
                (1, 4, 5),
                # Node 4 is a dead-end with no outgoing edges
            ],

            # Long path vs short heavy path
            "Court lourd vs long léger": [
                (0, 1, 10),
                (0, 2, 1),
                (2, 3, 1),
                (3, 4, 1),
                (4, 1, 1)
            ],

            # Graph with multiple disconnected components
            "Composants déconnectés": [
                (0, 1, 3),
                (1, 2, 4),
                (3, 4, 2),
                (4, 5, 1)
            ],

            # Larger sparse graph (performance edge case)
            "Sparce à 10 nœuds": [
                (0, 1, 7),
                (1, 2, 9),
                (2, 3, 10),
                (3, 4, 11),
                (4, 5, 6),
                (5, 6, 9),
                (6, 7, 2),
                (7, 8, 1),
                (8, 9, 7)
            ],
            "Poids négatif (non supporté)": [
    (0, 1, 2),
    (1, 2, -5),
    (2, 3, 1),
    (3, 4, 2),
    (4, 5, 3),
    (5, 6, 1),
    (6, 7, 2),
    (7, 8, 1),
    (8, 9, 2)
],
"Arêtes parallèles": [
    (0, 1, 2),
    (0, 1, 5),
    (1, 2, 1),
    (2, 3, 2),
    (2, 3, 4),
    (3, 4, 3),
    (4, 5, 2),
    (5, 6, 6),
    (6, 7, 1),
    (7, 8, 2),
    (8, 9, 3),
    (9, 0, 4)
],
"Boucles sur sommets": [
    (0, 0, 3),
    (1, 1, 2),
    (2, 2, 1),
    (3, 3, 4),
    (4, 4, 2),
    (5, 5, 1),
    (0, 1, 2),
    (1, 2, 1),
    (2, 3, 2),
    (3, 4, 2),
    (4, 5, 1),
    (5, 6, 2),
    (6, 7, 3),
    (7, 8, 2),
    (8, 9, 1)
],
"Arêtes bidirectionnelles": [
    (0, 1, 2), (1, 0, 5),
    (1, 2, 1), (2, 1, 3),
    (2, 3, 2), (3, 2, 2),
    (3, 4, 1), (4, 3, 4),
    (4, 5, 2), (5, 4, 2),
    (5, 6, 3), (6, 5, 1),
    (6, 7, 2), (7, 6, 2),
    (7, 8, 1), (8, 7, 3),
    (8, 9, 2), (9, 8, 2)
],
            # Graphe non complet d'ordre 50 
            "Non complet à 50 nœuds": [
                (i, (i + 1) % 50, 1 + (i % 7)) for i in range(50)
            ] + [
                (i, (i + 5) % 50, 2 + (i % 5)) for i in range(0, 50, 4)
            ] + [
                (i, (i + 13) % 50, 3 + (i % 3)) for i in range(0, 50, 10)
            ],
            # Graphe avec cycle absorbant (cycle de poids total nul ou négatif)
"Graphe avec cycle absorbant(non fiable)": [
    (0, 1, 2),
    (1, 2, -3),
    (2, 3, 1),
    (3, 1, -2),  
    (3, 4, 2),
    (4, 5, 1)
],

# Graphe avec poids négatif qui pose problème à Dijkstra (chemin optimal passe par négatif)
"Graphe négatif (non fiable)": [
    (0, 1, 2),
    (1, 2, -5),
    (2, 0, 1),  # Ce cycle 0→1→2→0 a un poids total négatif (-2)
],
        }

        # Show custom selection dialog
        dialog = GraphSelectionDialog(list(predefined_graphs.keys()), self)
        if dialog.exec_() == QDialog.Accepted:
            graph_name = dialog.get_selected_graph()
            if graph_name:
                self.import_graph_data(predefined_graphs[graph_name])


    def import_custom_graph(self):
        text, ok = QInputDialog.getMultiLineText(
            self, "Importer un graphe", 
            "Entrez les arêtes du graphe au format :\n[(src, dst, poids), ...] ", 
            "[(0, 1, 2),\n(0, 2, 4),\n(1, 2, 1),\n(1, 3, 7),\n(2, 3, 3)]"
        )
        
        if ok and text:
            try:
                # Safely evaluate the input
                edges = ast.literal_eval(text.strip())
                if isinstance(edges, list):
                    self.import_graph_data(edges)
                else:
                    QMessageBox.warning(self, "Format invalide", "L'entrée doit être une liste d'arêtes")
            except (SyntaxError, ValueError) as e:
                QMessageBox.warning(self, "Format invalide", f"Impossible d'analyser l'entrée : {str(e)}")

    def import_graph_data(self, edges):
        """Import graph data and automatically position nodes in concentric circles (adaptive to screen size)"""
        import math
        from PyQt5.QtWidgets import QMessageBox

        try:
            # Clear existing graph
            self.canvas.nodes = []
            self.canvas.edges = []

            # Find all unique nodes
            nodes = set()
            for src, dst, _ in edges:
                nodes.add(src)
                nodes.add(dst)
            num_nodes = len(nodes)

            if num_nodes == 0:
                return

            center_x = self.canvas.width() / 2
            center_y = self.canvas.height() / 2
            max_radius = min(center_x, center_y) * 0.9

            # Estimate the number of rings needed
            ring_counts = []  # how many nodes per ring
            remaining = num_nodes
            ring = 1
            while remaining > 0:
                capacity = 6 * ring  # number of nodes this ring can hold
                use = min(remaining, capacity)
                ring_counts.append(use)
                remaining -= use
                ring += 1

            num_rings = len(ring_counts)
            if num_rings == 0:
                return

            # Dynamically calculate ring gap to use full space
            ring_gap = max_radius / num_rings

            # Place nodes in rings
            positions = []
            node_index = 0
            for r, count in enumerate(ring_counts):
                radius = ring_gap * (r + 1)
                for i in range(count):
                    angle = 2 * math.pi * i / count
                    x = center_x + radius * math.cos(angle)
                    y = center_y + radius * math.sin(angle)
                    positions.append((x, y))
                    node_index += 1

            self.canvas.nodes = positions

            # Add edges
            for src, dst, weight in edges:
                if src < num_nodes and dst < num_nodes:
                    self.canvas.edges.append((src, dst, weight))
                else:
                    QMessageBox.warning(self, "Arc invalide",
                                        f"Arc ({src}, {dst}) Référence à un nœud inexistant")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

            
            self.canvas.update()
            
        except (ValueError, TypeError) as e:
            QMessageBox.warning(self, "Données invalides", f"Erreur lors du traitement des données du graphe : {str(e)}")
    def show_help(self):
        help_dialog = HelpDialog(self)
        help_dialog.exec_()