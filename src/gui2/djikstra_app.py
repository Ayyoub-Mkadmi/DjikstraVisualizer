# djikstra_app.py
import networkx as nx
from .dijkstra_visualizer import DijkstraVisualisateur

class DijkstraApp:
    def __init__(self, edge_list, source, parent=None):
        """
        Initialize without creating QApplication

        Args:
            edge_list: list of (u, v, weight) tuples
            source: node label (int or str)
            parent: Parent QWidget
        """
        # Keep only the minimum weight for each (u, v)
        min_edges = {}
        for u, v, w in edge_list:
            if (u, v) not in min_edges or w < min_edges[(u, v)]:
                min_edges[(u, v)] = w

        self.graph = nx.DiGraph()
        for (u, v), w in min_edges.items():
            self.graph.add_edge(u, v, weight=w)
        self.source = source
        self.parent = parent

    def run(self):
        """Run the visualizer as a child window"""
        self.visualizer = DijkstraVisualisateur(
            graphe=self.graph, 
            source=self.source,
            parent=self.parent  # Pass the parent
        )
        self.visualizer.show()