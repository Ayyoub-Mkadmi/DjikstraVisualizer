from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QGroupBox, QFrame, QTextEdit, QSlider, QMessageBox, QInputDialog,QProgressBar,QDialog,QPlainTextEdit,QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib import patheffects

from .dijkstra_algorithm import DijkstraStepByStep

class DijkstraVisualisateur(QWidget):
    def __init__(self, parent=None, graphe=None, source=0):
        """
        Initialise le visualisateur avec un graphe et un nœud source
        
        Args:
            parent: Widget parent Qt
            graphe: Objet NetworkX (DiGraph ou Graph)
            source: Nœud de départ (par défaut: 0)
        """
        super().__init__(parent)
        self.graphe_initial = graphe
        self.source_initial = source
        self.setWindowTitle("Visualisation de l'Algorithme de Dijkstra")
        
        # Schéma de couleurs moderne
        self.couleur_fond = '#f5f5f5'
        self.couleur_panneau = '#ffffff'
        self.couleur_principale = '#4285f4'
        self.couleur_secondaire = '#f1c40f'
        self.couleur_surlignage = '#e15759'
        self.couleur_texte = '#202124'
        self.couleur_succes = '#59a14f'
        self.couleur_arete = '#6a8caf'
        
        # Schéma de couleurs pour le graphe
        self.couleur_noeud = "#C8DCFF"
        self.couleur_noeud_courant = '#e15759'
        self.couleur_noeud_visite = '#59a14f'
        self.couleur_noeud_non_visite = "#89B4FF"
        self.couleur_noeud_source = '#ff69b4'
        self.couleur_arete_surlignee = '#f1c40f'

        self._layout_seed = 42
        self.positions = None
        
        self.setup_ui()
        self.configurer_algorithme()
        self.showMaximized()  # <-- Use this instead of showFullScreen()
        
    def setup_ui(self):
        # Configuration du style
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.couleur_fond};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QGroupBox {{
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: {self.couleur_panneau};
            }}
            QPushButton {{
                background-color: {self.couleur_principale};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: #3367d6;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
            }}
            QLabel {{
                font-size: 14px;
                color: {self.couleur_texte};
            }}
            QTextEdit {{
                background-color: {self.couleur_panneau};
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                font-family: 'Consolas', monospace;
            }}
            QSlider::groove:horizontal {{
                height: 8px;
                background: #e0e0e0;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                width: 16px;
                height: 16px;
                background: {self.couleur_principale};
                border-radius: 8px;
                margin: -4px 0;
            }}
            QProgressBar {{
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background: white;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {self.couleur_principale};
                border-radius: 3px;
            }}
        """)
        
        # Layout principal
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(15)
        
        # Panneau gauche (contrôles et statut)
        left_panel = QVBoxLayout()
        left_panel.setSpacing(12)
        left_panel.setContentsMargins(0, 0, 0, 0)
        
        # Titre
        title_layout = QHBoxLayout()
        title = QLabel("Visualiseur de Dijkstra")
        title.setFont(QFont('Segoe UI', 18, QFont.Bold))
        title.setStyleSheet(f"color: {self.couleur_texte};")
        title_layout.addWidget(title)
        title_layout.addStretch()
        left_panel.addLayout(title_layout)
        
        # Status banner
        self.status_banner = QLabel("Prêt à démarrer")
        self.status_banner.setAlignment(Qt.AlignCenter)
        self.status_banner.setFont(QFont('Segoe UI', 12, QFont.Bold))
        self.status_banner.setStyleSheet(f"""
            background-color: {self.couleur_principale};
            color: white;
            padding: 8px;
            border-radius: 4px;
        """)
        left_panel.addWidget(self.status_banner)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        left_panel.addWidget(self.progress_bar)
        
        # Groupe de contrôle
        control_group = QGroupBox("Contrôles")
        control_layout = QVBoxLayout()
        
        # Contrôle de vitesse
        speed_layout = QHBoxLayout()
        speed_label = QLabel("Latence :")
        speed_layout.addWidget(speed_label)
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(100, 2000)
        self.speed_slider.setValue(500)
        self.speed_slider.valueChanged.connect(self.update_speed_label)
        speed_layout.addWidget(self.speed_slider)
        
        self.speed_label = QLabel("500")
        self.speed_label.setFixedWidth(40)
        speed_layout.addWidget(self.speed_label)
        
        control_layout.addLayout(speed_layout)
        
        # Boutons
        button_layout = QHBoxLayout()
        self.step_button = QPushButton("▶ Étape suivante")
        self.step_button.clicked.connect(self.etape_suivante)
        button_layout.addWidget(self.step_button)
        
        self.auto_button = QPushButton("⏩ Défilement auto")
        self.auto_button.clicked.connect(self.basculer_auto_etape)
        button_layout.addWidget(self.auto_button)
        
        control_layout.addLayout(button_layout)
        
        self.reset_button = QPushButton("↻ Réinitialiser")
        self.reset_button.clicked.connect(self.reinitialiser_algorithme)
        control_layout.addWidget(self.reset_button)
        
        self.change_source_button = QPushButton("🎯 Changer le sommet source")
        self.change_source_button.clicked.connect(self.changer_source)
        control_layout.addWidget(self.change_source_button)
        
        control_group.setLayout(control_layout)
        left_panel.addWidget(control_group)
        
        # Add this with the other buttons in setup_ui()
        self.export_button = QPushButton("💾 Exporter la structure")
        self.export_button.clicked.connect(self.exporter_structure)
        self.export_button.setEnabled(True)  # Can export anytime
        control_layout.addWidget(self.export_button)

        # Groupe de statut
        status_group = QGroupBox("Statut de l'algorithme")
        status_layout = QVBoxLayout()
        
        # Nœud courant
        current_node_layout = QHBoxLayout()
        current_node_label = QLabel("Nœud courant:")
        current_node_label.setFont(QFont('Segoe UI', 13))
        current_node_layout.addWidget(current_node_label)
        
        self.current_node_display = QLabel("Aucun")
        self.current_node_display.setFont(QFont('Segoe UI', 11))
        self.current_node_display.setStyleSheet(f"""
            background-color: {self.couleur_panneau};
            color: {self.couleur_surlignage};
            border: 1px solid #e0e0e0;
            padding: 2px 8px;
            min-width: 50px;
        """)
        current_node_layout.addWidget(self.current_node_display)
        current_node_layout.addStretch()
        
        status_layout.addLayout(current_node_layout)
        
        # Nœuds visités
        visited_label = QLabel("Nœuds visités:")
        visited_label.setFont(QFont('Segoe UI', 11))
        status_layout.addWidget(visited_label)
        
        self.visited_display = QTextEdit()
        self.visited_display.setReadOnly(True)
        self.visited_display.setFont(QFont('Consolas', 12))
        self.visited_display.setStyleSheet(f"color: {self.couleur_principale};")
        status_layout.addWidget(self.visited_display)
        
        # File de priorité
        queue_label = QLabel("File de priorité:")
        queue_label.setFont(QFont('Segoe UI', 11))
        status_layout.addWidget(queue_label)
        
        self.queue_display = QTextEdit()
        self.queue_display.setReadOnly(True)
        self.queue_display.setFont(QFont('Consolas', 12))
        self.queue_display.setStyleSheet(f"color: {self.couleur_secondaire};")
        status_layout.addWidget(self.queue_display)
        
        # --- Nouvelle section : Distances finales ---
        final_dist_group = QGroupBox("Distances finales")
        final_dist_layout = QVBoxLayout()
        self.final_dist_display = QTextEdit()
        self.final_dist_display.setReadOnly(True)
        self.final_dist_display.setFont(QFont('Consolas', 12))
        self.final_dist_display.setStyleSheet(f"color: {self.couleur_principale};")
        final_dist_layout.addWidget(self.final_dist_display)
        final_dist_group.setLayout(final_dist_layout)
        status_layout.addWidget(final_dist_group)
        # --- Fin nouvelle section ---

        status_group.setLayout(status_layout)
        left_panel.addWidget(status_group)
        left_panel.addStretch()
        
        main_layout.addLayout(left_panel, stretch=1)
        
        # Séparateur vertical
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #e0e0e0;")
        main_layout.addWidget(separator)
        
        # Panneau droit (visualisation)
        right_panel = QVBoxLayout()
        
        # Figure matplotlib
        self.figure = Figure(figsize=(8, 6), facecolor=self.couleur_fond)
        self.canvas = FigureCanvas(self.figure)
        self.axes = self.figure.add_subplot(111)
        
        # Ajouter une barre d'outils de navigation
        self.toolbar = NavigationToolbar(self.canvas, self)
        right_panel.addWidget(self.toolbar)
        right_panel.addWidget(self.canvas)
        
        main_layout.addLayout(right_panel, stretch=4)
        
    def update_speed_label(self):
        self.speed_label.setText(str(self.speed_slider.value()))
        
    def configurer_algorithme(self):
        """Initialise l'algorithme avec le graphe et la source fournis"""
        self.algorithme = DijkstraStepByStep(self.graphe_initial, source=self.source_initial)
        self.auto_etape = False
        self.id_auto_etape = None
        self.arbre_couvrant_minimal = nx.DiGraph()  # Pour stocker l'arbre couvrant minimal
        self.dessiner_graphe()
        
    def etape_suivante(self):
        if self.algorithme.has_next():
            self.algorithme.step_forward()
            
            # Update spanning tree
            etat = self.algorithme.get_current_state()
            noeud_courant = etat['current_node']
            predecesseur = etat['predecessors'].get(noeud_courant)
            
            if predecesseur is not None and noeud_courant is not None:
                if not self.arbre_couvrant_minimal.has_edge(predecesseur, noeud_courant):
                    poids = next(d['weight'] for u, v, d in self.graphe_initial.edges(data=True) 
                            if u == predecesseur and v == noeud_courant)
                    self.arbre_couvrant_minimal.add_edge(predecesseur, noeud_courant, weight=poids)
            
            # Update progress
            total_nodes = len(self.graphe_initial.nodes())
            visited_nodes = len(etat['visited'])
            progress = int((visited_nodes / total_nodes) * 100)
            self.progress_bar.setValue(progress)
            
            self.mettre_a_jour_statut()
            self.dessiner_graphe()
            
            if not self.algorithme.has_next():
                self.status_banner.setText("Algorithme terminé !")
                self.status_banner.setStyleSheet("""
                    background-color: #59a14f;
                    color: white;
                    padding: 8px;
                    border-radius: 4px;
                """)
                self.progress_bar.setStyleSheet("""
                    QProgressBar::chunk {
                        background-color: #59a14f;
                    }
                """)
                self.step_button.setText("Terminé")
                self.step_button.setStyleSheet("background-color: #59a14f;")
                self.auto_button.setText("Terminé")
                self.auto_button.setStyleSheet("background-color: #59a14f;")
                self.step_button.setEnabled(False)
                self.auto_button.setEnabled(False)
                self.dessiner_graphe()  # Redraw to highlight all paths
                
    def reinitialiser_algorithme(self):
        # Stop auto-stepping if active
        if self.auto_etape:
            self.basculer_auto_etape()
        
        # Reset the algorithm
        self.configurer_algorithme()
        
        # Reset UI elements to initial state
        self.status_banner.setText("Prêt à démarrer")
        self.status_banner.setStyleSheet(f"""
            background-color: {self.couleur_principale};
            color: white;
            padding: 8px;
            border-radius: 4px;
        """)
        
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color: {self.couleur_principale};
            }}
        """)
        
        self.step_button.setText("▶ Étape suivante")
        self.step_button.setStyleSheet(f"""
            background-color: {self.couleur_principale};
            color: white;
        """)
        self.auto_button.setText("⏩ Défilement auto")
        self.auto_button.setStyleSheet(f"""
            background-color: {self.couleur_principale};
            color: white;
        """)
        
        # Enable buttons
        self.step_button.setEnabled(True)
        self.auto_button.setEnabled(True)
        
        # Update status displays
        self.mettre_a_jour_statut()
        
        # Redraw the graph
        self.dessiner_graphe()
        
    def basculer_auto_etape(self):
        self.auto_etape = not self.auto_etape
        
        if self.auto_etape:
            self.auto_button.setText("⏸ Pause")
            self.step_button.setEnabled(False)
            self.boucle_auto_etape()
        else:
            self.auto_button.setText("⏩ Défilement auto")
            self.step_button.setEnabled(True)
            if self.id_auto_etape:
                self.killTimer(self.id_auto_etape)
                
    def boucle_auto_etape(self):
        if self.auto_etape and self.algorithme.has_next():
            self.etape_suivante()
            self.id_auto_etape = self.startTimer(self.speed_slider.value())
        else:
            self.basculer_auto_etape()
            
    def timerEvent(self, event):
        if event.timerId() == self.id_auto_etape:
            self.boucle_auto_etape()
            
    def mettre_a_jour_statut(self):
        etat = self.algorithme.get_current_state()
        
        # Mettre à jour l'affichage du nœud courant
        courant = etat['current_node']
        self.current_node_display.setText(str(courant) if courant is not None else "Aucun")
        if courant is not None:
            self.current_node_display.setStyleSheet(f"""
                background-color: #ffebee;
                color: {self.couleur_surlignage};
                border: 1px solid #e0e0e0;
                padding: 2px 8px;
            """)
        else:
            self.current_node_display.setStyleSheet(f"""
                background-color: {self.couleur_panneau};
                color: {self.couleur_surlignage};
                border: 1px solid #e0e0e0;
                padding: 2px 8px;
            """)
        
        # Mettre à jour l'affichage des nœuds visités
        visites = sorted(etat['visited'])
        self.visited_display.clear()
        self.visited_display.setPlainText(', '.join(map(str, visites))) if visites else "Aucun"
        
        # Mettre à jour l'affichage de la file de priorité
        file = [(d, n) for d, n in self.algorithme.queue]
        self.queue_display.clear()
        if file:
            for d, n in sorted(file):
                self.queue_display.append(f"Nœud {n}: distance {d}")  # <-- FIXED
        else:
            self.queue_display.setPlainText("Vide")
            
        # --- Nouvelle section : Affichage des distances finales ---
        final_distances = etat['distances']
        lines = []
        for node in sorted(final_distances):
            dist = final_distances[node]
            text_dist = f"{dist:.0f}" if dist < float('inf') else "∞"
            lines.append(f"{node} : {text_dist}")
        self.final_dist_display.setPlainText('\n'.join(lines))
        # --- Fin nouvelle section ---
            
    def dessiner_graphe(self, force_new_layout=False):
        self.axes.clear()

        # Calculer ou réutiliser la disposition des nœuds
        if force_new_layout or self.positions is None:
            self.positions = self.calculate_optimal_layout(force_new_seed=force_new_layout)
        positions = self.positions

        etat = self.algorithme.get_current_state()

        # Style des nœuds
        couleurs_noeuds = []
        tailles_noeuds = []
        for noeud in self.graphe_initial.nodes():
            if noeud == self.source_initial:
                couleurs_noeuds.append(self.couleur_noeud_source)
                tailles_noeuds.append(1300)
            elif noeud == etat['current_node']:
                couleurs_noeuds.append(self.couleur_noeud_courant)
                tailles_noeuds.append(1200)
            elif noeud in etat['visited']:
                couleurs_noeuds.append(self.couleur_noeud_visite)
                tailles_noeuds.append(800)
            else:
                couleurs_noeuds.append(self.couleur_noeud_non_visite)
                tailles_noeuds.append(600)

        # Dessiner les arêtes avec évitement de chevauchement
        self.draw_edges_with_avoidance(positions, etat)

        # Dessiner les nœuds
        nx.draw_networkx_nodes(
            self.graphe_initial, positions, ax=self.axes,
            node_color=couleurs_noeuds,
            node_size=tailles_noeuds,
            edgecolors='#333333',
            linewidths=1.5,
            alpha=0.9
        )

        # Dessiner les étiquettes des arêtes avec placement amélioré
        self.draw_edge_labels(positions)

        # Dessiner les étiquettes des nœuds avec distances
        self.draw_node_labels(positions, etat)

        # Afficher les informations sur le chemin le plus court
        if etat['current_node'] is not None and etat['current_node'] != self.source_initial:
            self.display_path_info(etat)

        # Personnaliser l'apparence du graphe
        self.axes.set_facecolor(self.couleur_fond)
        self.axes.set_title("Visualisation de l'Algorithme de Dijkstra", fontsize=12, pad=20)
        self.axes.axis('off')
        self.figure.tight_layout()
        self.canvas.draw()

    def calculate_optimal_layout(self, force_new_seed=False):
        """Place les nœuds en cercle, si >25 deux cercles, si >40 trois couches pour meilleure lisibilité."""
        import math
        n = self.graphe_initial.number_of_nodes()
        nodes = list(self.graphe_initial.nodes())
        pos = {}

        if n <= 25:
            # Un seul cercle
            radius = 1.0
            angle_offset = 0
            if force_new_seed:
                import random
                angle_offset = random.uniform(0, 2 * math.pi)
            for i, node in enumerate(nodes):
                angle = 2 * math.pi * i / n + angle_offset
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                pos[node] = (x, y)
        elif n <= 40:
            # Deux cercles : extérieur et intérieur
            outer_n = min(25, n)
            inner_n = n - outer_n
            outer_radius = 1.0
            inner_radius = 0.55
            angle_offset_outer = 0
            angle_offset_inner = math.pi / outer_n if inner_n > 0 else 0
            if force_new_seed:
                import random
                angle_offset_outer = random.uniform(0, 2 * math.pi)
                angle_offset_inner = random.uniform(0, 2 * math.pi)
            # Outer circle
            for i in range(outer_n):
                angle = 2 * math.pi * i / outer_n + angle_offset_outer
                x = outer_radius * math.cos(angle)
                y = outer_radius * math.sin(angle)
                pos[nodes[i]] = (x, y)
            # Inner circle (scatter)
            for j in range(inner_n):
                angle = 2 * math.pi * j / inner_n + angle_offset_inner
                x = inner_radius * math.cos(angle)
                y = inner_radius * math.sin(angle)
                pos[nodes[outer_n + j]] = (x, y)
        else:
            # Trois cercles : extérieur, intermédiaire, intérieur
            outer_n = 20
            middle_n = 15
            inner_n = n - outer_n - middle_n
            outer_radius = 1.0
            middle_radius = 0.7
            inner_radius = 0.4
            angle_offset_outer = 0
            angle_offset_middle = math.pi / middle_n if middle_n > 0 else 0
            angle_offset_inner = math.pi / inner_n if inner_n > 0 else 0
            if force_new_seed:
                import random
                angle_offset_outer = random.uniform(0, 2 * math.pi)
                angle_offset_middle = random.uniform(0, 2 * math.pi)
                angle_offset_inner = random.uniform(0, 2 * math.pi)
            # Outer circle
            for i in range(outer_n):
                angle = 2 * math.pi * i / outer_n + angle_offset_outer
                x = outer_radius * math.cos(angle)
                y = outer_radius * math.sin(angle)
                pos[nodes[i]] = (x, y)
            # Middle circle
            for j in range(middle_n):
                angle = 2 * math.pi * j / middle_n + angle_offset_middle
                x = middle_radius * math.cos(angle)
                y = middle_radius * math.sin(angle)
                pos[nodes[outer_n + j]] = (x, y)
            # Inner circle (scatter)
            for k in range(inner_n):
                angle = 2 * math.pi * k / inner_n + angle_offset_inner
                x = inner_radius * math.cos(angle)
                y = inner_radius * math.sin(angle)
                pos[nodes[outer_n + middle_n + k]] = (x, y)
        self.normalize_positions(pos)
        return pos

    def normalize_positions(self, pos):
        if not pos:
            return
        x_values = [p[0] for p in pos.values()]
        y_values = [p[1] for p in pos.values()]
        min_x, max_x = min(x_values), max(x_values)
        min_y, max_y = min(y_values), max(y_values)
        x_range = max_x - min_x if max_x != min_x else 1
        y_range = max_y - min_y if max_y != min_y else 1
        padding = 0.1
        scale = 1 - padding
        for node in pos:
            pos[node] = (
                scale * 2 * (pos[node][0] - min_x) / x_range - scale + padding/2,
                scale * 2 * (pos[node][1] - min_y) / y_range - scale + padding/2
            )

    def draw_edges_with_avoidance(self, pos, state):
        nx.draw_networkx_edges(
            self.graphe_initial, pos, ax=self.axes,
            edge_color=self.couleur_arete,
            width=1.5,
            arrows=True,
            arrowsize=30,
            alpha=1,
            connectionstyle='arc3,rad=0'  # <-- lignes droites
        )
        # Highlight current edges only if the algorithm is not finished
        if state['current_node'] is not None and self.algorithme.has_next():
            current_edges = [(state['current_node'], v) for v, _ in self.algorithme.graph[state['current_node']]]
            nx.draw_networkx_edges(
                self.graphe_initial, pos, ax=self.axes,
                edgelist=current_edges,
                edge_color=self.couleur_arete_surlignee,
                width=3.0,
                arrows=True,
                arrowsize=35,
                alpha=0.8,
                connectionstyle='arc3,rad=0'  # <-- lignes droites
            )
        # Always show the minimum spanning tree in green
        if self.arbre_couvrant_minimal.number_of_edges() > 0:
            nx.draw_networkx_edges(
                self.arbre_couvrant_minimal, pos, ax=self.axes,
                edge_color=self.couleur_succes,
                width=3.5,
                arrows=True,
                arrowsize=35,
                alpha=0.8,
                connectionstyle='arc3,rad=0'  # <-- lignes droites
            )

    def draw_edge_labels(self, pos):
        """Affiche les poids directement sur les arêtes (arcs), bien centrés et superposés à l'arc"""
        edge_labels = {(u, v): f"{d['weight']}" for u, v, d in self.graphe_initial.edges(data=True)}
        for edge, label in edge_labels.items():
            x1, y1 = pos[edge[0]]
            x2, y2 = pos[edge[1]]
            # Position du label : exactement au centre de l'arc
            x = (x1 + x2) / 2
            y = (y1 + y2) / 2
            # Décalage très léger pour éviter de masquer la flèche, mais rester sur l'arc
            dx = x2 - x1
            dy = y2 - y1
            length = (dx**2 + dy**2) ** 0.5
            if length != 0:
                # Décalage minime dans la direction perpendiculaire (pour rester sur l'arc)
                offset_x = -dy / length * 0.02
                offset_y = dx / length * 0.02
                x += offset_x
                y += offset_y
            self.axes.text(
                x, y, label,
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.1'),
                fontsize=10,
                ha='center',
                va='center',
                zorder=10
            )

    def draw_node_labels(self, pos, state):
        node_labels = {}
        for node in self.graphe_initial.nodes():
            dist = state['distances'].get(node, float('inf'))
            text_dist = f"{dist:.0f}" if dist < float('inf') else "∞"
            node_labels[node] = f"{node}\n(d={text_dist})"
        textes = nx.draw_networkx_labels(
            self.graphe_initial, pos, labels=node_labels,
            ax=self.axes, font_size=10,
            font_color=self.couleur_texte,
            font_weight='bold'
        )
        for _, text in textes.items():
            text.set_path_effects([
                patheffects.withStroke(linewidth=3, foreground='white')
            ])

    def display_path_info(self, state):
        path = []
        node = state['current_node']
        while node is not None:
            path.append(node)
            node = state['predecessors'].get(node)
        path.reverse()
        if len(path) > 1:
            total_distance = state['distances'][state['current_node']]
            self.axes.text(
                0.5, -0.1,
                f"Distance jusqu'à {state['current_node']}: {total_distance}",
                transform=self.axes.transAxes,
                ha='center',
                fontsize=11,
                bbox=dict(facecolor=self.couleur_succes, alpha=0.7, edgecolor='none')
            )
            
    def changer_source(self):
        noeuds = list(self.graphe_initial.nodes())
        if not noeuds:
            QMessageBox.warning(self, "Erreur", "Aucun nœud dans le graphe.")
            return
        
        new_source, ok = QInputDialog.getInt(
            self,
            "Changer le sommet source",
            f"Entrez le nouvel identifiant du sommet source (entre {min(noeuds)} et {max(noeuds)}):",
            min=min(noeuds),
            max=max(noeuds)
        )
        
        if ok and new_source in noeuds:
            self.source_initial = new_source
            self.configurer_algorithme()
            self.step_button.setEnabled(True)
            self.auto_button.setEnabled(True)
            self.mettre_a_jour_statut()
        elif ok:
            QMessageBox.critical(self, "Erreur", "Sommet source invalide.")
            
    def closeEvent(self, event):
        if self.auto_etape and self.id_auto_etape:
            self.killTimer(self.id_auto_etape)
        plt.close('all')
        event.accept()

    def exporter_structure(self):
        """Export the shortest path tree structure using self.arbre_couvrant_minimal"""
        if not hasattr(self, 'algorithme'):
            QMessageBox.warning(self, "Erreur", "Aucun algorithme initialisé.")
            return
        
        etat = self.algorithme.get_current_state()
        
        # Get edges from the minimum spanning tree
        edges = [(u, v, d['weight']) for u, v, d in self.arbre_couvrant_minimal.edges(data=True)]
        edges.sort()  # Sort for consistent output
        
        # Format as Python code
        formatted_edges = "Arbre des plus courts chemins depuis la source:\n[\n" + \
                        ",\n".join(f"    ({u}, {v}, {weight})" for u, v, weight in edges) + \
                        "\n]"
        
        # Add distances information
        distances = etat['distances']
        formatted_distances = "\n\nDistances depuis la source:\n" + \
                            "\n".join(f"  {node}: {dist if dist != float('inf') else '∞'}" 
                                    for node, dist in sorted(distances.items()))
        
        complete_output = formatted_edges + formatted_distances
        
        # Create the export dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Arbre des plus courts chemins")
        dialog.setMinimumWidth(500)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        # Title
        title = QLabel("Structure de l'arbre des plus courts chemins:")
        title.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #333333;
                padding: 10px 0;
            }
        """)
        layout.addWidget(title)
        
        # Text area with the edges
        text_edit = QPlainTextEdit()
        text_edit.setPlainText(complete_output)
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Consolas", 10))
        text_edit.setStyleSheet("""
            QPlainTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dddfe2;
                border-radius: 4px;
                padding: 10px;
                color: #24292e;
            }
        """)
        layout.addWidget(text_edit)
        
        # Button box
        button_box = QHBoxLayout()
        
        copy_button = QPushButton("📋 Copier")
        copy_button.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                background-color: #4285f4;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
        """)
        copy_button.clicked.connect(lambda: QApplication.clipboard().setText(complete_output))
        
        close_button = QPushButton("❌ Fermer")
        close_button.setStyleSheet("padding: 8px 16px; font-size: 13px;")
        close_button.clicked.connect(dialog.close)
        
        button_box.addWidget(copy_button)
        button_box.addStretch()
        button_box.addWidget(close_button)
        layout.addLayout(button_box)
        
        dialog.exec_()