import networkx as nx
import numpy as np

class TrafficNetwork:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.intersections = []
        self.queue_lengths = {}
        self.straight_fraction = 0.7
        # [NEW FEATURE] History tracking
        self.history = {
            'step': [],
            'total_congestion': [],
            'queue_variance': [] # To measure "Balanced Timings"
        }
        self.step_count = 0

    def create_intersection(self, intersection_id):
        self.intersections.append(intersection_id)
        lanes = [f"N_{intersection_id}", f"S_{intersection_id}", 
                 f"E_{intersection_id}", f"W_{intersection_id}"]
        for lane in lanes:
            self.graph.add_node(lane, type='lane')
            self.queue_lengths[lane] = 0

    def update_queues(self, new_queues):
        # Update current state
        for lane, cars in new_queues.items():
            if lane in self.queue_lengths:
                self.queue_lengths[lane] = cars
        
        # [NEW FEATURE] Record Statistics for Visualization
        self.step_count += 1
        current_queues = list(self.queue_lengths.values())
        total_cars = sum(current_queues)
        variance = np.var(current_queues) if current_queues else 0
        
        self.history['step'].append(self.step_count)
        self.history['total_congestion'].append(total_cars)
        self.history['queue_variance'].append(variance)

    def get_throughput_potential(self, intersection_id, mode):
        N = self.queue_lengths.get(f"N_{intersection_id}", 0)
        S = self.queue_lengths.get(f"S_{intersection_id}", 0)
        E = self.queue_lengths.get(f"E_{intersection_id}", 0)
        W = self.queue_lengths.get(f"W_{intersection_id}", 0)
        f = self.straight_fraction

        if mode == 1:   return (f * N) + (f * S)
        elif mode == 2: return ((1-f) * N) + ((1-f) * S)
        elif mode == 3: return (f * E) + (f * W)
        elif mode == 4: return ((1-f) * E) + ((1-f) * W)
        elif mode == 5: return N 
        elif mode == 6: return E
        else:           return 0
        
    def get_history(self):
        return self.history