# Quantum Traffic Light Optimization (QAOA) 🚦⚛️

A Bachelor Thesis Project (BTP) exploring the application of Quantum Computing to smart city traffic management. This project uses the **Quantum Approximate Optimization Algorithm (QAOA)** to dynamically control traffic signals in SUMO, integrating real-world constraints like emergency vehicles, weather conditions, and safety protocols.



## 🌟 Key Features

### 1. Quantum Optimization (QAOA)
Uses IBM's Qiskit to solve the Maximum Independent Set (MIS) problem, finding optimal traffic phases. Generates a **Quantum Circuit Diagram** for every decision.

### 2. Priority Systems 🚑 🚌
* **Emergency Vehicle Priority (EVP):** Instantly overrides signals for ambulances.
* **Transit Signal Priority (TSP):** Extends green lights for approaching Buses to improve public transit efficiency.

### 3. Safety Engineering ⚠️
* **Dilemma Zone Protection:** Detects high-speed vehicles approaching a yellow light and extends the green phase to prevent dangerous sudden braking.

### 4. Adaptive & Environmental Logic 🌿
* **Adaptive Timing:** Allocates green time dynamically (10s–35s) based on exact queue length.
* **CO2 Tracking:** Real-time monitoring of carbon emission reductions.
* **Weather Simulation:** Simulates "Rain Mode" with reduced friction and visual cues (Blue vehicles).

## 🛠️ Tech Stack

* **Simulation:** [SUMO (Simulation of Urban MObility)](https://eclipse.dev/sumo/)
* **Quantum SDK:** [Qiskit](https://www.ibm.com/quantum/qiskit)
* **Interface:** TraCI
* **Analytics:** Matplotlib, NumPy

## 🚀 How to Run

### 1. Prerequisites
* Python 3.8+
* SUMO installed and added to `PATH`.
* Environment Variable `SUMO_HOME` set.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
pip install pylatexenc  # Required for circuit diagrams