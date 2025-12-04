from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit.primitives import StatevectorSampler
from qiskit_optimization.algorithms import MinimumEigenOptimizer
import numpy as np

class QAOATrafficSolver:
    def __init__(self):
        """
        Sets up the Quantum Approximate Optimization Algorithm (QAOA).
        """
        # 1. Choose a Classical Optimizer
        # COBYLA is standard for QAOA as it handles noisy landscapes well
        self.optimizer = COBYLA(maxiter=50)

        # 2. Choose a Quantum Primitive (Simulator)
        # StatevectorSampler calculates the exact outcome probabilities (perfect for testing)
        self.sampler = StatevectorSampler()

        # 3. Initialize QAOA
        # reps=1 means depth p=1 (shallow circuit, faster but less accurate)
        # You can increase reps=2 or 3 for better results at the cost of speed
        self.qaoa = QAOA(sampler=self.sampler, optimizer=self.optimizer, reps=1)

        # 4. Wrap it in the Optimizer Class
        # This helper class handles the conversion from QUBO -> Ising Hamiltonian -> QAOA
        self.eigen_optimizer = MinimumEigenOptimizer(self.qaoa)

    def solve(self, qubo_problem):
        """
        Runs the QAOA loop to find the optimal traffic signal configuration.
        
        Args:
            qubo_problem (QuadraticProgram): The output from QUBOGenerator
            
        Returns:
            dict: {intersection_id: active_mode}
        """
        # Execute the optimization
        result = self.eigen_optimizer.solve(qubo_problem)
        
        # Extract the best bitstring (solution)
        # result.x gives us an array like [0, 1, 0, 0, 0, 0] corresponding to variables
        return self._interpret_solution(result, qubo_problem)

    def _interpret_solution(self, result, qubo_problem):
        """
        Decodes the binary result back into traffic modes.
        """
        solution_dict = {}
        variable_names = [var.name for var in qubo_problem.variables]
        binary_values = result.x
        
        print(f"\n--- QAOA Raw Result Status: {result.status} ---")
        
        for name, value in zip(variable_names, binary_values):
            # We are looking for variables like "x_1_2" set to 1.0
            if value > 0.9:  # Threshold for binary 1
                # Parse name "x_{intersection}_{mode}"
                parts = name.split('_')
                intersection_id = int(parts[1])
                mode = int(parts[2])
                solution_dict[intersection_id] = mode
                print(f"Intersection {intersection_id} -> Activating Mode {mode}")
        
        return solution_dict

# --- Quick Test ---
if __name__ == "__main__":
    from traffic_model import TrafficNetwork
    from qubo_generator import QUBOGenerator

    # 1. Setup a dummy intersection
    net = TrafficNetwork()
    net.create_intersection(1)
    # Heavy traffic on North-South (should trigger Mode 1)
    net.update_queues({"N_1": 100, "S_1": 100, "E_1": 5, "W_1": 5})

    # 2. Generate QUBO
    print("Generating QUBO...")
    qubo_gen = QUBOGenerator(net)
    qubo = qubo_gen.generate_qubo()

    # 3. Solve with QAOA
    print("Solving with QAOA...")
    solver = QAOATrafficSolver()
    solution = solver.solve(qubo)
    
    print("\nFinal Recommended Signal Plan:", solution)