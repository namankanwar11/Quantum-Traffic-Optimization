# Quantum Traffic Light Optimization (QAOA) 🚦⚛️

. This project uses the **Quantum Approximate Optimization Algorithm (QAOA)** to dynamically optimize traffic signal timings in a SUMO simulation, minimizing congestion and balancing lane queues compared to traditional fixed-time control.


## 🌟 Key Features

* **Quantum Optimization:** Uses IBM's Qiskit to implement QAOA for real-time traffic phase decision-making.
* **Dual-Phase Simulation:**
    * **Phase 1 (Baseline):** Runs a standard fixed-time traffic signal model in the background (invisible) to establish a benchmark.
    * **Phase 2 (QAOA):** Runs the Quantum-optimized model with a live GUI visualization.
* **Real-Time Analytics:**
    * **Congestion Reduction:** Visualizes the drop in total vehicles over time.
    * **Signal Balancing:** Tracks "Queue Variance" to prove that the quantum algorithm balances traffic evenly across all lanes.
* **Performance Comparison:** Generates a final "Before vs. After" report showing the exact percentage improvement in traffic flow.
* **Detailed Dashboard:** Provides per-lane statistics (Average Queue, Max Queue, Wait Time) and congestion profiles.

## 🛠️ Tech Stack

* **Simulation Environment:** [SUMO (Simulation of Urban MObility)](https://eclipse.dev/sumo/)
* **Quantum SDK:** [Qiskit](https://www.ibm.com/quantum/qiskit)
* **Interfacing:** TraCI (Traffic Control Interface)
* **Visualization:** Matplotlib, NumPy, Pandas

## 📂 Project Structure

```bash
├── main.py               # Entry point: Runs Baseline & QAOA phases + Visualization
├── solver.py             # Quantum Solver: Sets up QAOA using Qiskit primitives
├── qubo_generator.py     # Math Layer: Converts Traffic Queues -> QUBO/Ising Hamiltonian
├── traffic_model.py      # Network Graph: Manages intersection state & history
├── visualization.py      # Analytics: Generates comparison graphs & dashboards
├── config.sumocfg        # SUMO Configuration file
├── traffic.rou.xml       # Traffic Demand/Route definitions
└── intersection.net.xml  # Network Geometry definitions