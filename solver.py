from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit.primitives import StatevectorSampler
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit.circuit.library import QAOAAnsatz
import matplotlib.pyplot as plt
import os

class QAOATrafficSolver:
    def __init__(self):
        """
        Sets up the Quantum Approximate Optimization Algorithm (QAOA).
        """
        self.optimizer = COBYLA(maxiter=50)
        self.sampler = StatevectorSampler()
        self.reps = 1
        self.qaoa = QAOA(sampler=self.sampler, optimizer=self.optimizer, reps=self.reps)
        self.eigen_optimizer = MinimumEigenOptimizer(self.qaoa)

    def solve(self, qubo_problem):
        result = self.eigen_optimizer.solve(qubo_problem)
        return self._interpret_solution(result, qubo_problem)

    def _interpret_solution(self, result, qubo_problem):
        solution_dict = {}
        variable_names = [var.name for var in qubo_problem.variables]
        binary_values = result.x
        
        for name, value in zip(variable_names, binary_values):
            if value > 0.9: 
                parts = name.split('_')
                if len(parts) >= 3:
                    intersection_id = int(parts[1])
                    mode = int(parts[2])
                    solution_dict[intersection_id] = mode
        
        return solution_dict

    def save_circuit_diagram(self, qubo_problem, filename="results/quantum_circuit.png"):
        """
        Generates and saves the Quantum Circuit Diagram using a robust saving method.
        """
        if not os.path.exists("results"):
            os.makedirs("results")
            
        print("\n   -> Generating Quantum Circuit Diagram...")
        
        try:
            # 1. Convert QUBO to Operator
            op, offset = qubo_problem.to_ising()
            
            # 2. Create the QAOA Circuit (Ansatz)
            ansatz = QAOAAnsatz(op, reps=self.reps)
            
            # 3. Decompose it into readable gates (H, CX, RZ)
            # We decompose twice to break down high-level QAOA blocks into raw gates
            decomposed_circuit = ansatz.decompose().decompose()
            
            # 4. Draw using Matplotlib (MPL)
            # We DO NOT pass 'filename' here. We get the figure object instead.
            fig = decomposed_circuit.draw(output='mpl', style='clifford')
            
            # 5. Force Save
            if fig:
                fig.savefig(filename, dpi=300, bbox_inches='tight')
                print(f"   -> ✅ SUCCESS: Circuit diagram saved to {filename}")
                
                # Close memory to prevent lag
                plt.close(fig)
            else:
                print("   -> ⚠️ Warning: Qiskit returned no figure to save.")

        except Exception as e:
            print(f"   -> ❌ ERROR generating image: {e}")
            print("   -> Attempting text-based fallback...")
            try:
                # Fallback: Print ASCII circuit to terminal if image fails
                print(decomposed_circuit.draw(output='text'))
            except:
                pass