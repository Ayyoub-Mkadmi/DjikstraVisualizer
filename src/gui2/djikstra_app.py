import tkinter as tk
import networkx as nx

from .dijkstra_visualizer import DijkstraVisualisateur


class DijkstraApp:
    def __init__(self, edge_list, source):
        """
        edge_list: list of (u, v, weight)
        source: node label (int or str)
        """
        self.graph = nx.DiGraph()
        for u, v, w in edge_list:
            self.graph.add_edge(u, v, weight=w)
        self.source = source

    def run(self):
        root = tk.Tk()
        app = DijkstraVisualisateur(root, self.graph, self.source)
        root.protocol("WM_DELETE_WINDOW", app.fermer)
        root.mainloop()



# if __name__ == "__main__":
#     # Example usage
#     edges = [
#         (0, 1, 2),
#         (0, 2, 4),
#         (1, 2, 1),
#         (1, 3, 7),
#         (2, 3, 3)
#     ]
#     source = 0
#     app = DijkstraApp(edges, source)
#     app.run()