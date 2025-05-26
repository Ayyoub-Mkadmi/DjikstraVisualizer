import heapq

class DijkstraStepByStep:
    def __init__(self, graph, source):
        self.source = source
  
        self.graph = {}
        for u in graph.nodes():
            self.graph[u] = [(v, d['weight']) for v, d in graph[u].items()]
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