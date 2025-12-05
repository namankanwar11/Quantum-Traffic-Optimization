# Quantum Traffic Light Optimization (QAOA) 🚦⚛️

A Bachelor Thesis Project (BTP) exploring the application of Quantum Computing to smart city traffic management. This project uses the **Quantum Approximate Optimization Algorithm (QAOA)** to dynamically control traffic signals in SUMO, integrating real-world constraints like emergency vehicles, weather conditions, and environmental impact.


## 🌟 Key Features

### 1. Quantum Optimization (QAOA)
Uses IBM's Qiskit to solve the Maximum Independent Set (MIS) problem on the traffic graph, finding the optimal phase configuration to maximize throughput in real-time.

### 2. Emergency Vehicle Priority (EVP) 🚑
* **Safety First:** Automatically detects ambulances approaching the intersection.
* **Instant Override:** Overrides the quantum logic to grant an immediate Green Light to the emergency vehicle, minimizing response time.

### 3. Adaptive Green Timing ⏱️
* **Dynamic Duration:** Instead of fixed intervals, the system calculates the exact green time needed (e.g., 10s for light traffic vs. 35s for heavy queues).
* **Smart Extension:** Extends the current green phase if the lane is still clearing, reducing unnecessary switching penalties.

### 4. Environmental Impact Analysis 🌿
* **CO2 Tracking:** Real-time monitoring of carbon emissions from idling cars.
* **Sustainability:** Demonstrates how better traffic flow leads to a measurable reduction in urban pollution.

### 5. Weather Simulation (Rain Mode) 🌧️
* **Realism:** Simulates wet road conditions by reducing tire friction and increasing driver reaction times.
* **Visuals:** Vehicles turn **Blue** during the storm to indicate "Wet Mode."

## 🛠️ Tech Stack

* **Simulation:** [SUMO (Simulation of Urban MObility)](https://eclipse.dev/sumo/)
* **Quantum SDK:** [Qiskit](https://www.ibm.com/quantum/qiskit)
* **Interface:** TraCI (Traffic Control Interface)
* **Analytics:** Matplotlib, NumPy, SciPy

## 📂 Project Structure

```bash
├── main.py               # Core Controller (Simulation Loop, Logic, & Visualization)
├── solver.py             # Quantum Module: Sets up QAOA & Classical Optimizers
├── qubo_generator.py     # Math Layer: Converts Traffic State -> QUBO Problem
├── traffic_model.py      # Network Graph: Manages Intersection Data & Stats
├── visualization.py      # Analytics: Generates Diagnostic Graphs
├── config.sumocfg        # SUMO Config Linking Network & Routes
├── traffic.rou.xml       # Traffic Demand (Cars + Ambulances)
└── intersection.net.xml  # Physical Road Network Geometry