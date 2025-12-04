# Quantum Traffic Light Optimization (QAOA)

This project uses the Quantum Approximate Optimization Algorithm (QAOA) to optimize traffic signal timings in a simulation.

## Features
- **Simulation:** SUMO (Simulation of Urban Mobility).
- **Algorithm:** IBM Qiskit QAOA.
- **Logic:** Optimizes North/South vs East/West flow based on real-time queue lengths.
- **Results:** Generates a performance report (Graph & Table) at the end.

## How to Run
1. Install SUMO: https://eclipse.dev/sumo/
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python main.py`