# dijkstra_visualizer.py
import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import patheffects
from dijkstra_algorithm import DijkstraStepByStep

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
        
        # Schéma de couleurs moderne
        self.couleur_fond = '#f5f7fa'
        self.couleur_panneau = '#ffffff'
        self.couleur_principale = '#4e79a7'
        self.couleur_secondaire = '#f28e2b'
        self.couleur_surlignage = '#e15759'
        self.couleur_texte = '#2d3436'
        self.couleur_succes = '#59a14f'
        self.couleur_arete = '#6a8caf'
        
        # Schéma de couleurs pour le graphe
        self.couleur_noeud = '#4e79a7'
        self.couleur_noeud_courant = '#e15759'
        self.couleur_noeud_visite = '#59a14f'
        self.couleur_noeud_non_visite = '#bab0ab'
        self.couleur_arete_surlignee = '#f28e2b'
        
        self.configurer_interface()
        self.configurer_algorithme()
        
    def configurer_interface(self):
        # Configurer les styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Cadre principal
        cadre_principal = tk.Frame(self.racine, bg=self.couleur_fond)
        cadre_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panneau gauche (contrôles et statut)
        panneau_gauche = tk.Frame(cadre_principal, bg=self.couleur_panneau, bd=2, relief=tk.RAISED)
        panneau_gauche.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=5)
        
        # Panneau droit (visualisation)
        panneau_droit = tk.Frame(cadre_principal, bg=self.couleur_fond)
        panneau_droit.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=5)
        
        # Titre
        cadre_titre = tk.Frame(panneau_gauche, bg=self.couleur_panneau)
        cadre_titre.pack(fill=tk.X, pady=(10, 20))
        ttk.Label(
            cadre_titre, 
            text="Algorithme de Dijkstra", 
            font=('Helvetica', 14, 'bold'),
            background=self.couleur_panneau,
            foreground=self.couleur_principale
        ).pack()
        
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
            text="Vitesse (ms):",
            background=self.couleur_panneau
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
            background=self.couleur_panneau
        )
        self.etiquette_vitesse.pack(side=tk.LEFT)
        
        # Boutons
        style_bouton = ttk.Style()
        style_bouton.configure('Primary.TButton', 
                             font=('Helvetica', 10, 'bold'),
                             padding=8,
                             foreground='white',
                             background=self.couleur_principale)
        
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
            font=('Helvetica', 9, 'bold'),
            background=self.couleur_panneau
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.affichage_noeud_courant = tk.Label(
            self.cadre_noeud_courant,
            text="Aucun",
            font=('Helvetica', 9, 'bold'),
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
            font=('Helvetica', 9, 'bold'),
            background=self.couleur_panneau
        ).pack(anchor=tk.W)
        
        self.affichage_noeuds_visites = tk.Text(
            cadre_visites,
            height=4,
            width=25,
            font=('Consolas', 8),
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
            font=('Helvetica', 9, 'bold'),
            background=self.couleur_panneau
        ).pack(anchor=tk.W)
        
        self.affichage_file = tk.Text(
            cadre_file,
            height=4,
            width=25,
            font=('Consolas', 8),
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
        
        # Configurer les styles
        self.style.configure('Panel.TLabelframe', 
                           background=self.couleur_panneau,
                           borderwidth=2,
                           relief=tk.RAISED)
        self.style.configure('Panel.TLabelframe.Label', 
                           background=self.couleur_panneau,
                           foreground=self.couleur_texte,
                           font=('Helvetica', 10, 'bold'))
        
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
        
    def dessiner_graphe(self):
        self.axes.clear()
        
        # Utiliser une disposition qui évite le chevauchement des nœuds
        positions = nx.kamada_kawai_layout(self.graphe_initial)
        
        # Ajuster l'échelle pour une meilleure visibilité
        facteur_echelle = 1.8
        positions = {k: (v[0]*facteur_echelle, v[1]*facteur_echelle) for k, v in positions.items()}
        
        etat = self.algorithme.get_current_state()
        
        # Style des nœuds
        couleurs_noeuds = []
        tailles_noeuds = []
        for noeud in self.graphe_initial.nodes():
            if noeud == etat['current_node']:
                couleurs_noeuds.append(self.couleur_noeud_courant)
                tailles_noeuds.append(1200)
            elif noeud in etat['visited']:
                couleurs_noeuds.append(self.couleur_noeud_visite)
                tailles_noeuds.append(800)
            else:
                couleurs_noeuds.append(self.couleur_noeud_non_visite)
                tailles_noeuds.append(600)
        
        # Dessiner toutes les arêtes d'abord (derrière les nœuds)
        nx.draw_networkx_edges(
            self.graphe_initial, positions, ax=self.axes,
            edge_color=self.couleur_arete,
            width=1.5,
            arrows=True,
            arrowsize=15,
            alpha=0.5,
            connectionstyle='arc3,rad=0'  # Lignes droites
        )
        
        # Dessiner les nœuds
        nx.draw_networkx_nodes(
            self.graphe_initial, positions, ax=self.axes,
            node_color=couleurs_noeuds,
            node_size=tailles_noeuds,
            edgecolors='#333333',
            linewidths=1.5,
            alpha=0.9
        )
        
        # Mettre en évidence les arêtes considérées à l'étape courante
        if etat['current_node'] is not None:
            aretes_courantes = [(etat['current_node'], v) for v, _ in self.algorithme.graph[etat['current_node']]]
            nx.draw_networkx_edges(
                self.graphe_initial, positions, ax=self.axes,
                edgelist=aretes_courantes,
                edge_color=self.couleur_arete_surlignee,
                width=3.0,
                arrows=True,
                arrowsize=20,
                alpha=0.8,
                connectionstyle='arc3,rad=0'  # Lignes droites
            )
        
        # Dessiner l'arbre couvrant minimal (persistant)
        if self.arbre_couvrant_minimal.number_of_edges() > 0:
            nx.draw_networkx_edges(
                self.arbre_couvrant_minimal, positions, ax=self.axes,
                edge_color=self.couleur_succes,
                width=3.5,
                arrows=True,
                arrowsize=20,
                alpha=0.8,
                connectionstyle='arc3,rad=0'  # Lignes droites
            )
        
        # Étiquettes des arêtes avec positionnement approprié
        etiquettes_aretes = {(u, v): f"{d['weight']}" for u, v, d in self.graphe_initial.edges(data=True)}
        nx.draw_networkx_edge_labels(
            self.graphe_initial, positions, edge_labels=etiquettes_aretes,
            ax=self.axes, font_size=9,
            bbox=dict(alpha=0.8, facecolor='white', edgecolor='none')
        )
        
        # Étiquettes des nœuds avec distances
        etiquettes_noeuds = {}
        for noeud in self.graphe_initial.nodes():
            dist = etat['distances'].get(noeud, float('inf'))
            texte_dist = f"{dist:.0f}" if dist < float('inf') else "∞"
            etiquettes_noeuds[noeud] = f"{noeud}\n(d={texte_dist})"
            
        # Dessiner les étiquettes des nœuds avec contour pour une meilleure visibilité
        textes = nx.draw_networkx_labels(
            self.graphe_initial, positions, labels=etiquettes_noeuds,
            ax=self.axes, font_size=10,
            font_color=self.couleur_texte,
            font_weight='bold'
        )
        
        for _, texte in textes.items():
            texte.set_path_effects([
                patheffects.withStroke(linewidth=3, foreground='white')
            ])
        
        # Afficher les informations sur le chemin le plus court
        if etat['current_node'] is not None and etat['current_node'] != self.source_initial:
            chemin = []
            noeud = etat['current_node']
            while noeud is not None:
                chemin.append(noeud)
                noeud = etat['predecessors'].get(noeud)
            chemin.reverse()
            
            if len(chemin) > 1:
                distance_totale = etat['distances'][etat['current_node']]
                self.axes.text(
                    0.5, -0.1,
                    f"Distance jusqu'à {etat['current_node']}: {distance_totale}",
                    transform=self.axes.transAxes,
                    ha='center',
                    fontsize=11,
                    bbox=dict(facecolor=self.couleur_succes, alpha=0.7, edgecolor='none')
                )
        
        # Personnaliser l'apparence du graphe
        self.axes.set_facecolor(self.couleur_fond)
        self.axes.set_title("Visualisation de l'Algorithme de Dijkstra", fontsize=12, pad=20)
        self.axes.margins(0.2)
        self.figure.tight_layout()
        self.canvas.draw()
        
    def fermer(self):
        if self.auto_etape and self.id_auto_etape:
            self.racine.after_cancel(self.id_auto_etape)
        plt.close('all')
        self.racine.destroy()