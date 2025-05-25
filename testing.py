import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import heapq
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import patheffects

class DijkstraStepByStep:
    def __init__(self, graph, source):
        self.source = source
        self.graph = {
            u: [(v, d['weight']) for v, d in graph[u].items()]
            for u in graph.nodes()
        }
        self.distances = {node: float('inf') for node in self.graph}
        self.distances[source] = 0
        self.predecessors = {node: None for node in self.graph}
        self.visited = set()
        self.queue = [(0, source)]
        self.current_node = None
        self.finished = False

    def has_next(self):
        return not self.finished

    def step_forward(self):
        if not self.queue:
            self.finished = True
            self.current_node = None
            return

        current_distance, current_node = heapq.heappop(self.queue)

        if current_node in self.visited:
            return

        self.current_node = current_node
        self.visited.add(current_node)

        for neighbor, weight in self.graph[current_node]:
            if neighbor in self.visited:
                continue
            new_distance = current_distance + weight
            if new_distance < self.distances[neighbor]:
                self.distances[neighbor] = new_distance
                self.predecessors[neighbor] = current_node
                heapq.heappush(self.queue, (new_distance, neighbor))

        if not self.queue:
            self.finished = True

    def get_current_state(self):
        return {
            'distances': dict(self.distances),
            'visited': set(self.visited),
            'current_node': self.current_node,
            'predecessors': dict(self.predecessors),
        }

class DijkstraVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Dijkstra's Algorithm Visualizer")
        
        # Set initial window size to 90% of screen size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{int(screen_width*0.9)}x{int(screen_height*0.9)}")
        
        # Modern color scheme
        self.bg_color = '#f5f7fa'
        self.panel_color = '#ffffff'
        self.primary_color = '#4e79a7'
        self.secondary_color = '#f28e2b'
        self.highlight_color = '#e15759'
        self.text_color = '#2d3436'
        self.success_color = '#59a14f'
        self.edge_color = '#6a8caf'
        
        # Graph color scheme
        self.node_color = '#4e79a7'
        self.current_node_color = '#e15759'
        self.visited_node_color = '#59a14f'
        self.unvisited_node_color = '#bab0ab'
        self.edge_highlight_color = '#f28e2b'
        
        self.setup_ui()
        self.initialize_graph()
        self.setup_algorithm()
        
    def setup_ui(self):
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Main frame
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel (controls and status)
        left_panel = tk.Frame(main_frame, bg=self.panel_color, bd=2, relief=tk.RAISED)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=5)
        
        # Right panel (visualization)
        right_panel = tk.Frame(main_frame, bg=self.bg_color)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=5)
        
        # Title
        title_frame = tk.Frame(left_panel, bg=self.panel_color)
        title_frame.pack(fill=tk.X, pady=(10, 20))
        ttk.Label(
            title_frame, 
            text="Dijkstra's Algorithm", 
            font=('Helvetica', 14, 'bold'),
            background=self.panel_color,
            foreground=self.primary_color
        ).pack()
        
        # Control widgets
        control_frame = ttk.LabelFrame(
            left_panel, 
            text="Controls",
            style='Panel.TLabelframe'
        )
        control_frame.pack(fill=tk.X, padx=10, pady=(0, 15))
        
        # Auto-step speed control
        speed_frame = tk.Frame(control_frame, bg=self.panel_color)
        speed_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            speed_frame,
            text="Speed (ms):",
            background=self.panel_color
        ).pack(side=tk.LEFT)
        
        self.speed_var = tk.IntVar(value=500)
        self.speed_slider = ttk.Scale(
            speed_frame,
            from_=100,
            to=2000,
            variable=self.speed_var,
            command=lambda _: self.update_speed_label()
        )
        self.speed_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.speed_label = ttk.Label(
            speed_frame,
            textvariable=self.speed_var,
            width=4,
            background=self.panel_color
        )
        self.speed_label.pack(side=tk.LEFT)
        
        # Buttons
        button_style = ttk.Style()
        button_style.configure('Primary.TButton', 
                             font=('Helvetica', 10, 'bold'),
                             padding=8,
                             foreground='white',
                             background=self.primary_color)
        
        self.step_button = ttk.Button(
            control_frame, 
            text="▶ Next Step", 
            command=self.step_forward,
            style='Primary.TButton'
        )
        self.step_button.pack(fill=tk.X, pady=5)
        
        self.auto_step_button = ttk.Button(
            control_frame,
            text="⏩ Auto Step",
            command=self.toggle_auto_step,
            style='Primary.TButton'
        )
        self.auto_step_button.pack(fill=tk.X, pady=5)
        
        self.reset_button = ttk.Button(
            control_frame,
            text="↻ Reset Algorithm",
            command=self.reset_algorithm,
            style='Primary.TButton'
        )
        self.reset_button.pack(fill=tk.X, pady=5)
        
        # Algorithm status visualization
        status_frame = ttk.LabelFrame(
            left_panel, 
            text="Algorithm Status",
            style='Panel.TLabelframe'
        )
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Current node visualization
        self.current_node_frame = tk.Frame(status_frame, bg=self.panel_color)
        self.current_node_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            self.current_node_frame,
            text="Current Node:",
            font=('Helvetica', 9, 'bold'),
            background=self.panel_color
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.current_node_display = tk.Label(
            self.current_node_frame,
            text="None",
            font=('Helvetica', 9, 'bold'),
            bg=self.panel_color,
            fg=self.highlight_color,
            width=5,
            relief=tk.SOLID,
            bd=1
        )
        self.current_node_display.pack(side=tk.LEFT)
        
        # Visited nodes visualization
        visited_frame = tk.Frame(status_frame, bg=self.panel_color)
        visited_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(
            visited_frame,
            text="Visited Nodes:",
            font=('Helvetica', 9, 'bold'),
            background=self.panel_color
        ).pack(anchor=tk.W)
        
        self.visited_nodes_display = tk.Text(
            visited_frame,
            height=4,
            width=25,
            font=('Consolas', 8),
            bg=self.panel_color,
            fg=self.primary_color,
            relief=tk.FLAT,
            wrap=tk.WORD
        )
        self.visited_nodes_display.pack(fill=tk.X)
        self.visited_nodes_display.config(state=tk.DISABLED)
        
        # Priority queue visualization
        queue_frame = tk.Frame(status_frame, bg=self.panel_color)
        queue_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(
            queue_frame,
            text="Priority Queue:",
            font=('Helvetica', 9, 'bold'),
            background=self.panel_color
        ).pack(anchor=tk.W)
        
        self.queue_display = tk.Text(
            queue_frame,
            height=4,
            width=25,
            font=('Consolas', 8),
            bg=self.panel_color,
            fg=self.secondary_color,
            relief=tk.FLAT,
            wrap=tk.WORD
        )
        self.queue_display.pack(fill=tk.X)
        self.queue_display.config(state=tk.DISABLED)
        
        # Graph visualization
        self.figure = plt.Figure(figsize=(8, 6), facecolor=self.bg_color)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=right_panel)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Configure styles
        self.style.configure('Panel.TLabelframe', 
                           background=self.panel_color,
                           borderwidth=2,
                           relief=tk.RAISED)
        self.style.configure('Panel.TLabelframe.Label', 
                           background=self.panel_color,
                           foreground=self.text_color,
                           font=('Helvetica', 10, 'bold'))
        
    def update_speed_label(self):
        self.speed_label.config(text=str(self.speed_var.get()))
        
    def initialize_graph(self):
        # Create a well-spaced graph
        self.graph = nx.DiGraph()
        self.graph.add_weighted_edges_from([
            (0, 1, 4), (0, 2, 1),
            (1, 3, 1), (1, 4, 3),
            (2, 1, 2), (2, 3, 5),
            (3, 4, 2), (3, 5, 3),
            (4, 5, 3), (2, 4, 2)
        ])
        
    def setup_algorithm(self):
        self.algo = DijkstraStepByStep(self.graph, source=0)
        self.auto_step = False
        self.auto_step_id = None
        self.min_spanning_tree = nx.DiGraph()  # To store the minimum spanning tree
        self.draw_graph()
        
    def step_forward(self):
        if self.algo.has_next():
            self.algo.step_forward()
            
            # Update minimum spanning tree
            state = self.algo.get_current_state()
            current_node = state['current_node']
            predecessor = state['predecessors'].get(current_node)
            
            if predecessor is not None and current_node is not None:
                if not self.min_spanning_tree.has_edge(predecessor, current_node):
                    weight = next(d['weight'] for u, v, d in self.graph.edges(data=True) 
                                if u == predecessor and v == current_node)
                    self.min_spanning_tree.add_edge(predecessor, current_node, weight=weight)
            
            self.update_status()
            self.draw_graph()
            
            if not self.algo.has_next():
                self.step_button.config(state=tk.DISABLED)
                self.auto_step_button.config(state=tk.DISABLED)
        else:
            messagebox.showinfo("Algorithm Complete", "Dijkstra's algorithm has finished running!")
            
    def reset_algorithm(self):
        if self.auto_step:
            self.toggle_auto_step()
            
        self.setup_algorithm()
        self.step_button.config(state=tk.NORMAL)
        self.auto_step_button.config(state=tk.NORMAL)
        self.update_status()
        
    def toggle_auto_step(self):
        self.auto_step = not self.auto_step
        
        if self.auto_step:
            self.auto_step_button.config(text="⏸ Pause Auto Step")
            self.step_button.config(state=tk.DISABLED)
            self.auto_step_loop()
        else:
            self.auto_step_button.config(text=f"⏩ Auto Step ({self.speed_var.get()}ms)")
            self.step_button.config(state=tk.NORMAL)
            if self.auto_step_id:
                self.root.after_cancel(self.auto_step_id)
                
    def auto_step_loop(self):
        if self.auto_step and self.algo.has_next():
            self.step_forward()
            self.auto_step_id = self.root.after(self.speed_var.get(), self.auto_step_loop)
        else:
            self.toggle_auto_step()
            
    def update_status(self):
        state = self.algo.get_current_state()
        
        # Update current node display
        current = state['current_node']
        self.current_node_display.config(
            text=str(current) if current is not None else "None",
            bg='#ffebee' if current is not None else self.panel_color
        )
        
        # Update visited nodes display
        visited = sorted(state['visited'])
        self.visited_nodes_display.config(state=tk.NORMAL)
        self.visited_nodes_display.delete(1.0, tk.END)
        self.visited_nodes_display.insert(tk.END, ', '.join(map(str, visited))) if visited else "None"
        self.visited_nodes_display.config(state=tk.DISABLED)
        
        # Update priority queue display
        queue = [(d, n) for d, n in self.algo.queue]
        self.queue_display.config(state=tk.NORMAL)
        self.queue_display.delete(1.0, tk.END)
        if queue:
            for d, n in sorted(queue):
                self.queue_display.insert(tk.END, f"Node {n}: distance {d}\n")
        else:
            self.queue_display.insert(tk.END, "Empty")
        self.queue_display.config(state=tk.DISABLED)
        
    def draw_graph(self):
        self.ax.clear()
        
        # Use a layout that prevents node overlap
        pos = nx.kamada_kawai_layout(self.graph)
        
        # Scale and adjust positions for better visibility
        scale_factor = 1.8
        pos = {k: (v[0]*scale_factor, v[1]*scale_factor) for k, v in pos.items()}
        
        state = self.algo.get_current_state()
        
        # Node styling
        node_colors = []
        node_sizes = []
        for node in self.graph.nodes():
            if node == state['current_node']:
                node_colors.append(self.current_node_color)
                node_sizes.append(1200)
            elif node in state['visited']:
                node_colors.append(self.visited_node_color)
                node_sizes.append(800)
            else:
                node_colors.append(self.unvisited_node_color)
                node_sizes.append(600)
        
        # Draw all edges first (behind nodes) - now with straight lines
        nx.draw_networkx_edges(
            self.graph, pos, ax=self.ax,
            edge_color=self.edge_color,
            width=1.5,
            arrows=True,
            arrowsize=15,
            alpha=0.5,
            connectionstyle='arc3,rad=0'  # Changed to straight lines
        )
        
        # Draw nodes
        nx.draw_networkx_nodes(
            self.graph, pos, ax=self.ax,
            node_color=node_colors,
            node_size=node_sizes,
            edgecolors='#333333',
            linewidths=1.5,
            alpha=0.9
        )
        
        # Highlight edges being considered in current step
        if state['current_node'] is not None:
            current_edges = [(state['current_node'], v) for v, _ in self.algo.graph[state['current_node']]]
            nx.draw_networkx_edges(
                self.graph, pos, ax=self.ax,
                edgelist=current_edges,
                edge_color=self.edge_highlight_color,
                width=3.0,
                arrows=True,
                arrowsize=20,
                alpha=0.8,
                connectionstyle='arc3,rad=0'  # Changed to straight lines
            )
        
        # Draw the minimum spanning tree (persistent)
        if self.min_spanning_tree.number_of_edges() > 0:
            nx.draw_networkx_edges(
                self.min_spanning_tree, pos, ax=self.ax,
                edge_color=self.success_color,
                width=3.5,
                arrows=True,
                arrowsize=20,
                alpha=0.8,
                connectionstyle='arc3,rad=0'  # Changed to straight lines
            )
        
        # Edge labels with proper positioning
        edge_labels = {(u, v): f"{d['weight']}" for u, v, d in self.graph.edges(data=True)}
        nx.draw_networkx_edge_labels(
            self.graph, pos, edge_labels=edge_labels,
            ax=self.ax, font_size=9,
            bbox=dict(alpha=0.8, facecolor='white', edgecolor='none')
        )
        
        # Node labels with distances
        node_labels = {}
        for node in self.graph.nodes():
            dist = state['distances'].get(node, float('inf'))
            dist_text = f"{dist:.0f}" if dist < float('inf') else "∞"
            node_labels[node] = f"{node}\n(d={dist_text})"
            
        # Draw node labels with outline for better visibility
        text_items = nx.draw_networkx_labels(
            self.graph, pos, labels=node_labels,
            ax=self.ax, font_size=10,
            font_color=self.text_color,
            font_weight='bold'
        )
        
        for _, text_item in text_items.items():
            text_item.set_path_effects([
                patheffects.withStroke(linewidth=3, foreground='white')
            ])
        
        # Display current shortest path information
        if state['current_node'] is not None and state['current_node'] != 0:
            path = []
            node = state['current_node']
            while node is not None:
                path.append(node)
                node = state['predecessors'].get(node)
            path.reverse()
            
            if len(path) > 1:
                total_distance = state['distances'][state['current_node']]
                self.ax.text(
                    0.5, -0.1,
                    f"Distance to {state['current_node']}: {total_distance}",
                    transform=self.ax.transAxes,
                    ha='center',
                    fontsize=11,
                    bbox=dict(facecolor=self.success_color, alpha=0.7, edgecolor='none')
                )
        
        # Customize the plot appearance
        self.ax.set_facecolor(self.bg_color)
        self.ax.set_title("Dijkstra's Algorithm Visualization", fontsize=12, pad=20)
        self.ax.margins(0.2)
        self.figure.tight_layout()
        self.canvas.draw()
        
    def on_close(self):
        if self.auto_step and self.auto_step_id:
            self.root.after_cancel(self.auto_step_id)
        plt.close('all')
        self.root.destroy()

class DijkstraStepByStep:
    def __init__(self, graph, source):
        self.source = source
        self.graph = {
            u: [(v, d['weight']) for v, d in graph[u].items()]
            for u in graph.nodes()
        }
        self.distances = {node: float('inf') for node in self.graph}
        self.distances[source] = 0
        self.predecessors = {node: None for node in self.graph}
        self.visited = set()
        self.queue = [(0, source)]
        self.current_node = None
        self.finished = False

    def has_next(self):
        return not self.finished

    def step_forward(self):
        if not self.queue:
            self.finished = True
            self.current_node = None
            return

        current_distance, current_node = heapq.heappop(self.queue)

        if current_node in self.visited:
            return

        self.current_node = current_node
        self.visited.add(current_node)

        for neighbor, weight in self.graph[current_node]:
            if neighbor in self.visited:
                continue
            new_distance = current_distance + weight
            if new_distance < self.distances[neighbor]:
                self.distances[neighbor] = new_distance
                self.predecessors[neighbor] = current_node
                heapq.heappush(self.queue, (new_distance, neighbor))

        if not self.queue:
            self.finished = True

    def get_current_state(self):
        return {
            'distances': dict(self.distances),
            'visited': set(self.visited),
            'current_node': self.current_node,
            'predecessors': dict(self.predecessors),
        }

if __name__ == "__main__":
    root = tk.Tk()
    app = DijkstraVisualizer(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()