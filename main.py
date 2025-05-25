# main.py
from dijkstra_visualizer import DijkstraVisualisateur
import tkinter as tk
import networkx as nx

def creer_graphe_exemple():
    """Crée un graphe exemple pour la démonstration"""
    G = nx.DiGraph()
    G.add_weighted_edges_from([
        ('A', 'B', 4),
        ('A', 'C', 2),
        ('B', 'C', 1),
        ('B', 'D', 5),
        ('C', 'D', 8),
        ('C', 'E', 10),
        ('D', 'E', 2),
        ('D', 'F', 6),
        ('E', 'F', 2)
    ])
    return G

if __name__ == "__main__":
    # Créer un graphe personnalisé
    graphe_personnalise = creer_graphe_exemple()
    noeud_source = 'A'  # Définir le nœud de départ
    
    # Démarrer l'application
    racine = tk.Tk()
    app = DijkstraVisualisateur(racine, graphe_personnalise, noeud_source)
    racine.protocol("WM_DELETE_WINDOW", app.fermer)
    racine.mainloop()