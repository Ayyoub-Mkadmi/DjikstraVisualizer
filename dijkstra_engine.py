import heapq

class DijkstraStepByStep:
    def __init__(self, graph, source):
        """
        graph: Dict[int, List[Tuple[int, float]]] - adjacency list
        source: int - starting node
        """
        self.graph = graph
        self.source = source
        self.distances = {node: float('inf') for node in graph}
        self.distances[source] = 0
        self.predecessors = {node: None for node in graph}
        self.visited = set()

        # Priority queue: (distance, node)
        self.pq = [(0, source)]

        # For step-by-step
        self.steps = []
        self.current_step = -1

        # Store snapshots of state
        self.state_snapshots = []

        self._initialize_step()

    def _initialize_step(self):
        self._snapshot("Initialized Dijkstra with source {}".format(self.source))

    def _snapshot(self, action_description):
        snapshot = {
            "step": len(self.steps),
            "action": action_description,
            "distances": self.distances.copy(),
            "predecessors": self.predecessors.copy(),
            "visited": self.visited.copy(),
            "pq": list(self.pq)
        }
        self.steps.append(snapshot)
        self.state_snapshots.append(snapshot)

    def has_next(self):
        return bool(self.pq)

    def step_forward(self):
        if not self.pq:
            self._snapshot("Algorithm complete")
            return None  # Done

        current_distance, current_node = heapq.heappop(self.pq)

        if current_node in self.visited:
            self._snapshot(f"Skipped already visited node {current_node}")
            return current_node

        self.visited.add(current_node)
        self._snapshot(f"Visiting node {current_node} with distance {current_distance}")

        for neighbor, weight in self.graph.get(current_node, []):
            new_distance = current_distance + weight
            if new_distance < self.distances[neighbor]:
                self.distances[neighbor] = new_distance
                self.predecessors[neighbor] = current_node
                heapq.heappush(self.pq, (new_distance, neighbor))
                self._snapshot(f"Updated distance of node {neighbor} to {new_distance} via {current_node}")

        self.current_step += 1
        return current_node

    def get_current_state(self):
        if 0 <= self.current_step < len(self.state_snapshots):
            return self.state_snapshots[self.current_step]
        return None

    def get_all_steps(self):
        return self.state_snapshots

    def get_final_distances(self):
        return self.distances

    def get_predecessors(self):
        return self.predecessors

graph = {
    0: [(1, 2), (2, 4)],
    1: [(2, 1), (3, 7)],
    2: [(3, 3)],
    3: []
}

algo = DijkstraStepByStep(graph, source=0)

while algo.has_next():
    algo.step_forward()
    print(algo.get_current_state()) 