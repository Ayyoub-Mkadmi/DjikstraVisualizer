# dijkstra_visualizer.py
import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import patheffects
from .dijkstra_algorithm import DijkstraStepByStep

class DijkstraVisualisateur:
    def __init__(self, racine, graphe, source=0):
        """
        Initialise le visualisateur avec un graphe et un nœud source
        
        Args:
            racine: Fenêtre Tkinter parente
            graphe: Objet NetworkX (DiGraph ou Graph)
            source: Nœud de départ (par défaut: 0)
        """
        self.racine = racine
        self.graphe_initial = graphe
        self.source_initial = source
        self.racine.title("Visualisation de l'Algorithme de Dijkstra")
        
        # Configuration initiale de la fenêtre
        largeur_ecran = self.racine.winfo_screenwidth()
        hauteur_ecran = self.racine.winfo_screenheight()
        self.racine.geometry(f"{int(largeur_ecran*0.9)}x{int(hauteur_ecran*0.9)}")
        
        # Schéma de couleurs moderne (aligned with PyQt5 version)
        self.couleur_fond = '#f5f5f5'
        self.couleur_panneau = '#ffffff'
        self.couleur_principale = '#4285f4'
        self.couleur_secondaire = '#f1c40f'
        self.couleur_surlignage = '#e15759'
        self.couleur_texte = '#202124'
        self.couleur_succes = '#59a14f'
        self.couleur_arete = '#6a8caf'
        
        # Schéma de couleurs pour le graphe
        self.couleur_noeud = "#C8DCFF"  # Light blue
        self.couleur_noeud_courant = '#e15759'
        self.couleur_noeud_visite = '#59a14f'
        self.couleur_noeud_non_visite = "#89B4FF"   # Light blue
        self.couleur_arete_surlignee = '#f1c40f'
        
        self.couleur_noeud_source = '#ff69b4'  # Pink for the source node

        self._layout_seed = 42  # Ajout d'une seed fixe pour la topologie initiale
        self.positions = None   # Stocke la disposition courante
        self.configurer_interface()
        self.configurer_algorithme()
        
    def configurer_interface(self):
        # Configurer les styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure custom styles to match PyQt5 version
        self.style.configure('TFrame', background=self.couleur_fond)
        self.style.configure('Panel.TLabelframe', 
                           background=self.couleur_panneau,
                           borderwidth=0,
                           relief=tk.RAISED,
                           bordercolor='#e0e0e0')
        self.style.configure('Panel.TLabelframe.Label', 
                           background=self.couleur_panneau,
                           foreground=self.couleur_texte,
                           font=('Segoe UI', 11, 'bold'))
        self.style.configure('Primary.TButton', 
                           font=('Segoe UI', 13),
                           padding=8,
                           foreground='white',
                           background=self.couleur_principale,
                           borderwidth=0,
                           focusthickness=0,
                           focuscolor='none')
        self.style.map('Primary.TButton',
                      background=[('active', '#3367d6'), ('pressed', '#2a56c6')])
        
        # Cadre principal
        cadre_principal = tk.Frame(self.racine, bg=self.couleur_fond)
        cadre_principal.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        # Panneau gauche (contrôles et statut)
        panneau_gauche = ttk.LabelFrame(cadre_principal, style='Panel.TLabelframe', width=350)
        panneau_gauche.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15), pady=5)
        panneau_gauche.pack_propagate(False)
        
        # Panneau droit (visualisation)
        panneau_droit = tk.Frame(cadre_principal, bg=self.couleur_fond)
        panneau_droit.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(15, 0), pady=5)
        
        # Titre
        cadre_titre = tk.Frame(panneau_gauche, bg=self.couleur_panneau)
        cadre_titre.pack(fill=tk.X, pady=(10, 20))
        ttk.Label(
            cadre_titre, 
            text="Visualiseur de Dijkstra", 
            font=('Segoe UI', 16, 'bold'),
            background=self.couleur_panneau,
            foreground=self.couleur_texte
        ).pack(side=tk.LEFT)
        
        
        
        # Widgets de contrôle
        cadre_controle = ttk.LabelFrame(
            panneau_gauche, 
            text="Contrôles",
            style='Panel.TLabelframe'
        )
        cadre_controle.pack(fill=tk.X, padx=10, pady=(0, 15))
        
        # Contrôle de vitesse
        cadre_vitesse = tk.Frame(cadre_controle, bg=self.couleur_panneau)
        cadre_vitesse.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            cadre_vitesse,
            text="Latence : ",
            background=self.couleur_panneau,
            font=('Segoe UI', 10)
        ).pack(side=tk.LEFT)
        
        self.variable_vitesse = tk.IntVar(value=500)
        self.curseur_vitesse = ttk.Scale(
            cadre_vitesse,
            from_=100,
            to=2000,
            variable=self.variable_vitesse,
            command=lambda _: self.mettre_a_jour_etiquette_vitesse()
        )
        self.curseur_vitesse.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.etiquette_vitesse = ttk.Label(
            cadre_vitesse,
            textvariable=self.variable_vitesse,
            width=4,
            background=self.couleur_panneau,
            font=('Segoe UI', 9)
        )
        self.etiquette_vitesse.pack(side=tk.LEFT)
        
        # Boutons
        self.bouton_etape = ttk.Button(
            cadre_controle, 
            text="▶ Étape suivante", 
            command=self.etape_suivante,
            style='Primary.TButton'
        )
        self.bouton_etape.pack(fill=tk.X, pady=5)
        
        self.bouton_auto = ttk.Button(
            cadre_controle,
            text="⏩ Défilement auto",
            command=self.basculer_auto_etape,
            style='Primary.TButton'
        )
        self.bouton_auto.pack(fill=tk.X, pady=5)
        
        self.bouton_reinitialiser = ttk.Button(
            cadre_controle,
            text="↻ Réinitialiser",
            command=self.reinitialiser_algorithme,
            style='Primary.TButton'
        )
        self.bouton_reinitialiser.pack(fill=tk.X, pady=5)

        # Nouveau bouton pour redessiner la topologie
        self.bouton_redessiner = ttk.Button(
            cadre_controle,
            text="🔄 Nouvelle topologie",
            command=self.redessiner_topologie,
            style='Primary.TButton'
        )
        self.bouton_redessiner.pack(fill=tk.X, pady=5)

        # Visualisation du statut de l'algorithme
        cadre_statut = ttk.LabelFrame(
            panneau_gauche, 
            text="Statut de l'algorithme",
            style='Panel.TLabelframe'
        )
        cadre_statut.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Visualisation du nœud courant
        self.cadre_noeud_courant = tk.Frame(cadre_statut, bg=self.couleur_panneau)
        self.cadre_noeud_courant.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            self.cadre_noeud_courant,
            text="Nœud courant:",
            font=('Segoe UI', 13),
            background=self.couleur_panneau
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.affichage_noeud_courant = tk.Label(
            self.cadre_noeud_courant,
            text="Aucun",
            font=('Segoe UI',11),
            bg=self.couleur_panneau,
            fg=self.couleur_surlignage,
            width=5,
            relief=tk.SOLID,
            bd=1
        )
        self.affichage_noeud_courant.pack(side=tk.LEFT)
        
        # Visualisation des nœuds visités
        cadre_visites = tk.Frame(cadre_statut, bg=self.couleur_panneau)
        cadre_visites.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(
            cadre_visites,
            text="Nœuds visités:",
            font=('Segoe UI', 11),
            background=self.couleur_panneau
        ).pack(anchor=tk.W)
        
        self.affichage_noeuds_visites = tk.Text(
            cadre_visites,
            height=4,
            width=25,
            font=('Consolas', 12),
            bg=self.couleur_panneau,
            fg=self.couleur_principale,
            relief=tk.FLAT,
            wrap=tk.WORD
        )
        self.affichage_noeuds_visites.pack(fill=tk.X)
        self.affichage_noeuds_visites.config(state=tk.DISABLED)
        
        # Visualisation de la file de priorité
        cadre_file = tk.Frame(cadre_statut, bg=self.couleur_panneau)
        cadre_file.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(
            cadre_file,
            text="File de priorité:",
            font=('Segoe UI', 11),
            background=self.couleur_panneau
        ).pack(anchor=tk.W)
        
        self.affichage_file = tk.Text(
            cadre_file,
            height=4,
            width=25,
            font=('Consolas', 12),
            bg=self.couleur_panneau,
            fg=self.couleur_secondaire,
            relief=tk.FLAT,
            wrap=tk.WORD
        )
        self.affichage_file.pack(fill=tk.X)
        self.affichage_file.config(state=tk.DISABLED)
        
        # Visualisation du graphe
        self.figure = plt.Figure(figsize=(8, 6), facecolor=self.couleur_fond)
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=panneau_droit)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    
        
    def mettre_a_jour_etiquette_vitesse(self):
        self.etiquette_vitesse.config(text=str(self.variable_vitesse.get()))
        
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
            
            # Mettre à jour l'arbre couvrant minimal
            etat = self.algorithme.get_current_state()
            noeud_courant = etat['current_node']
            predecesseur = etat['predecessors'].get(noeud_courant)
            
            if predecesseur is not None and noeud_courant is not None:
                if not self.arbre_couvrant_minimal.has_edge(predecesseur, noeud_courant):
                    poids = next(d['weight'] for u, v, d in self.graphe_initial.edges(data=True) 
                               if u == predecesseur and v == noeud_courant)
                    self.arbre_couvrant_minimal.add_edge(predecesseur, noeud_courant, weight=poids)
            
            self.mettre_a_jour_statut()
            self.dessiner_graphe()
            
            if not self.algorithme.has_next():
                self.bouton_etape.config(state=tk.DISABLED)
                self.bouton_auto.config(state=tk.DISABLED)
        else:
            messagebox.showinfo("Algorithme terminé", "L'algorithme de Dijkstra a terminé son exécution!")
            
    def reinitialiser_algorithme(self):
        if self.auto_etape:
            self.basculer_auto_etape()
            
        self.configurer_algorithme()
        self.bouton_etape.config(state=tk.NORMAL)
        self.bouton_auto.config(state=tk.NORMAL)
        self.mettre_a_jour_statut()
        
    def basculer_auto_etape(self):
        self.auto_etape = not self.auto_etape
        
        if self.auto_etape:
            self.bouton_auto.config(text="⏸ Pause")
            self.bouton_etape.config(state=tk.DISABLED)
            self.boucle_auto_etape()
        else:
            self.bouton_auto.config(text=f"⏩ Défilement auto ({self.variable_vitesse.get()}ms)")
            self.bouton_etape.config(state=tk.NORMAL)
            if self.id_auto_etape:
                self.racine.after_cancel(self.id_auto_etape)
                
    def boucle_auto_etape(self):
        if self.auto_etape and self.algorithme.has_next():
            self.etape_suivante()
            self.id_auto_etape = self.racine.after(self.variable_vitesse.get(), self.boucle_auto_etape)
        else:
            self.basculer_auto_etape()
            
    def mettre_a_jour_statut(self):
        etat = self.algorithme.get_current_state()
        
        # Mettre à jour l'affichage du nœud courant
        courant = etat['current_node']
        self.affichage_noeud_courant.config(
            text=str(courant) if courant is not None else "Aucun",
            bg='#ffebee' if courant is not None else self.couleur_panneau
        )
        
        # Mettre à jour l'affichage des nœuds visités
        visites = sorted(etat['visited'])
        self.affichage_noeuds_visites.config(state=tk.NORMAL)
        self.affichage_noeuds_visites.delete(1.0, tk.END)
        self.affichage_noeuds_visites.insert(tk.END, ', '.join(map(str, visites))) if visites else "Aucun"
        self.affichage_noeuds_visites.config(state=tk.DISABLED)
        
        # Mettre à jour l'affichage de la file de priorité
        file = [(d, n) for d, n in self.algorithme.queue]
        self.affichage_file.config(state=tk.NORMAL)
        self.affichage_file.delete(1.0, tk.END)
        if file:
            for d, n in sorted(file):
                self.affichage_file.insert(tk.END, f"Nœud {n}: distance {d}\n")
        else:
            self.affichage_file.insert(tk.END, "Vide")
        self.affichage_file.config(state=tk.DISABLED)
        
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

    def redessiner_topologie(self):
        """Force le recalcul et le redessin du graphe avec une nouvelle disposition."""
        import random
        self._layout_seed = random.randint(0, 1000000)
        self.positions = self.calculate_optimal_layout(force_new_seed=True)
        self.dessiner_graphe()

    def calculate_optimal_layout(self, force_new_seed=False):
        """
        Place les nœuds en cercle, façon 'steering wheel', pour une répartition parfaite.
        """
        import math
        n = self.graphe_initial.number_of_nodes()
        nodes = list(self.graphe_initial.nodes())
        radius = 1.0  # rayon du cercle
        angle_offset = 0  # pour faire tourner le cercle à chaque redessin si souhaité

        # Optionnel: randomiser la rotation du cercle à chaque redessin
        if force_new_seed:
            import random
            angle_offset = random.uniform(0, 2 * math.pi)

        pos = {}
        for i, node in enumerate(nodes):
            angle = 2 * math.pi * i / n + angle_offset
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            pos[node] = (x, y)
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
            arrowsize=15,
            alpha=0.5,
            connectionstyle='arc3,rad=0'  # <-- lignes droites
        )
        if state['current_node'] is not None:
            current_edges = [(state['current_node'], v) for v, _ in self.algorithme.graph[state['current_node']]]
            nx.draw_networkx_edges(
                self.graphe_initial, pos, ax=self.axes,
                edgelist=current_edges,
                edge_color=self.couleur_arete_surlignee,
                width=3.0,
                arrows=True,
                arrowsize=20,
                alpha=0.8,
                connectionstyle='arc3,rad=0'  # <-- lignes droites
            )
        if self.arbre_couvrant_minimal.number_of_edges() > 0:
            nx.draw_networkx_edges(
                self.arbre_couvrant_minimal, pos, ax=self.axes,
                edge_color=self.couleur_succes,
                width=3.5,
                arrows=True,
                arrowsize=20,
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
        
    def fermer(self):
        if self.auto_etape and self.id_auto_etape:
            self.racine.after_cancel(self.id_auto_etape)
        plt.close('all')
        self.racine.destroy()