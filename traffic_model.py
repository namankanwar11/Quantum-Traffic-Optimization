import networkx as nx

class TrafficNetwork:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.intersections = []
        self.queue_lengths = {}
        self.straight_fraction = 0.7

    def create_intersection(self, intersection_id):
        self.intersections.append(intersection_id)
        lanes = [f"N_{intersection_id}", f"S_{intersection_id}", 
                 f"E_{intersection_id}", f"W_{intersection_id}"]
        for lane in lanes:
            self.graph.add_node(lane, type='lane')
            self.queue_lengths[lane] = 0

    def update_queues(self, new_queues):
        for lane, cars in new_queues.items():
            if lane in self.queue_lengths:
                self.queue_lengths[lane] = cars

    def get_throughput_potential(self, intersection_id, mode):
        N = self.queue_lengths[f"N_{intersection_id}"]
        S = self.queue_lengths[f"S_{intersection_id}"]
        E = self.queue_lengths[f"E_{intersection_id}"]
        W = self.queue_lengths[f"W_{intersection_id}"]
        f = self.straight_fraction

        if mode == 1:
            return (f * N) + (f * S)
        elif mode == 2:
            return ((1-f) * N) + ((1-f) * S)
        elif mode == 3:
            return (f * E) + (f * W)
        elif mode == 4:
            return ((1-f) * E) + ((1-f) * W)
        elif mode == 5:
            return N 
        elif mode == 6:
            return E
        else:
            return 0