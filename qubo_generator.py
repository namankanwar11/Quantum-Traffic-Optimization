from qiskit_optimization import QuadraticProgram
from traffic_model import TrafficNetwork

class QUBOGenerator:
    # Updated line in qubo_generator.py
    def __init__(self, traffic_network, lambda_1=1.0, lambda_4=200.0):
        self.net = traffic_network
        self.l1 = lambda_1
        self.l4 = lambda_4

    def generate_qubo(self):
        qp = QuadraticProgram()
        
        for i in self.net.intersections:
            for mode in range(1, 7):
                qp.binary_var(f"x_{i}_{mode}")

        linear_terms = {}
        quadratic_terms = {}

        for i in self.net.intersections:
            for mode in range(1, 7):
                c_ij = self.net.get_throughput_potential(i, mode)
                var_name = f"x_{i}_{mode}"
                linear_terms[var_name] = -self.l1 * c_ij

        for i in self.net.intersections:
            for mode in range(1, 7):
                var_name = f"x_{i}_{mode}"
                current_val = linear_terms.get(var_name, 0)
                linear_terms[var_name] = current_val - self.l4
                
            for m1 in range(1, 7):
                for m2 in range(1, 7):
                    if m1 != m2:
                        v1 = f"x_{i}_{m1}"
                        v2 = f"x_{i}_{m2}"
                        quadratic_terms[(v1, v2)] = self.l4

        qp.minimize(linear=linear_terms, quadratic=quadratic_terms)
        return qp