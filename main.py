# main.py
from dijkstra_visualizer import DijkstraVisualisateur
import tkinter as tk
import networkx as nx
import random

def creer_graphe_exemple():
    """Crée un graphe orienté à 10 nœuds, bien réparti, sans doublons d'arcs"""
    G = nx.DiGraph()
    nodes = [f"N{i}" for i in range(1, 11)]
    G.add_nodes_from(nodes)
    # Créer un cycle
    for i in range(10):
        G.add_edge(nodes[i], nodes[(i+1)%10], weight=random.randint(1, 10))
    # Ajouter quelques arcs aléatoires pour la densité
    added = set((nodes[i], nodes[(i+1)%10]) for i in range(10))
    while len(added) < 22:  # 12 arcs supplémentaires
        u, v = random.sample(nodes, 2)
        if (u, v) not in added:
            G.add_edge(u, v, weight=random.randint(1, 10))
            added.add((u, v))
    return G

if __name__ == "__main__":
    # Créer un graphe personnalisé
    graphe_personnalise = creer_graphe_exemple()
    noeud_source = 'N1'  # Définir le nœud de départ
    
    # Démarrer l'application
    racine = tk.Tk()
    app = DijkstraVisualisateur(racine, graphe_personnalise, noeud_source)
    racine.protocol("WM_DELETE_WINDOW", app.fermer)
    racine.mainloop()