from qiskit_optimization import QuadraticProgram
from traffic_model import TrafficNetwork
import traci

class QUBOGenerator:
    def __init__(self, traffic_network, current_queues, approaching_traffic, lambda_1=1.0, lambda_4=200.0, bus_weight=2.0, alpha=0.5, is_proactive=True):
        self.net = traffic_network
        self.queues = current_queues 
        self.approaching = approaching_traffic 
        self.l1 = lambda_1
        self.l4 = lambda_4
        self.W_person = bus_weight 
        self.alpha = alpha 
        self.is_proactive = is_proactive
        self.modes = [1, 3] # Simplified to NS straight, EW straight

    def generate_qubo(self):
        qp = QuadraticProgram()
        
        for i in self.net.intersections:
            for mode in range(1, 7):
                qp.binary_var(f"x_{i}_{mode}")

        linear_terms = {}
        quadratic_terms = {}

        for i in self.net.intersections:
            for mode in range(1, 7):
                
                # Identify lanes and corresponding edge IDs
                lane_key = None
                edge_key = None
                if mode in [1, 2, 5]: lane_key, edge_key = "N_1", "n_in" 
                elif mode in [3, 4, 6]: lane_key, edge_key = "E_1", "e_in"
                # Fallback, though modes 1-6 cover all main options

                # 1. Base Queue (Reactive part)
                waiting_q = self.queues.get(lane_key, 0)
                
                # 2. Combined Proactive Throughput
                if self.is_proactive and edge_key in self.approaching:
                    # [PROACTIVE LOGIC] Weighted sum of waiting and approaching traffic
                    approaching_q = self.approaching.get(edge_key, 0)
                    proactive_q = ((1 - self.alpha) * waiting_q) + (self.alpha * approaching_q)
                else:
                    # [REACTIVE LOGIC] Only use current waiting queue
                    proactive_q = waiting_q 
                
                # 3. Apply mode split and person weight
                mode_factor = self.net.straight_fraction if mode in [1, 3] else (1 - self.net.straight_fraction)
                
                weight_factor = self.W_person if mode == 3 else 1.0 # Bus/Person factor for EW
                
                # Final Throughput Potential
                c_ij = proactive_q * mode_factor * weight_factor

                var_name = f"x_{i}_{mode}"
                linear_terms[var_name] = -self.l1 * c_ij

        # --- Constraint Logic (Remains the same) ---
        for i in self.net.intersections:
            P = self.l4
            for mode in range(1, 7):
                name = f"x_{i}_{mode}"
                linear_terms[name] = linear_terms.get(name, 0) - P
            
            for m1 in range(1, 7):
                for m2 in range(1, 7):
                    if m1 != m2:
                        v1 = f"x_{i}_{m1}"
                        v2 = f"x_{i}_{m2}"
                        quadratic_terms[(v1, v2)] = P

        qp.minimize(linear=linear_terms, quadratic=quadratic_terms)
        return qp