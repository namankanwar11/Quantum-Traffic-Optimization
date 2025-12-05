# Quantum Traffic Light Optimization (QAOA) 🚦⚛️

A Bachelor Thesis Project (BTP) exploring the application of Quantum Computing to smart city traffic management. This project demonstrates a **Proactive Traffic Control System** that anticipates congestion using look-ahead data and optimizes signal timings via the Quantum Approximate Optimization Algorithm (QAOA).



## 🌟 Key Features

### 1. Triple-Phase Comparative Architecture 📊
The system runs three distinct simulation modes for comprehensive academic comparison:
* **Phase 1 (Baseline):** Unoptimized fixed-time traffic control.
* **Phase 2 (Reactive QAOA):** Optimizes only based on current queue lengths (no lookahead).
* **Phase 3 (Proactive QAOA):** Optimizes based on a weighted prediction of future congestion (Look-Ahead Control).

### 2. Proactive Look-Ahead Control 🔮
The QAOA objective function ($\text{Ising Hamiltonian}$) is constructed using a weighted average of **waiting traffic** (reactive) and **approaching traffic** (proactive), allowing the system to clear lanes before they become fully jammed.

### 3. Safety & Priority Systems 🚑 🚌 ⚠️
* **Dilemma Zone Protection:** Extends green light when high-speed vehicles are in the critical stopping zone.
* **Emergency Vehicle Priority (EVP):** Instantly overrides signals for ambulances.
* **Transit Signal Priority (TSP):** Extends green lights for approaching Buses to improve person throughput.

### 4. Adaptive & Environmental Logic 🌿
* **Adaptive Timing:** Allocates green time dynamically (10s–35s) based on exact queue length.
* **CO2 Tracking:** Real-time monitoring of carbon emission reductions.
* **Weather Simulation:** Simulates "Rain Mode" physics with visual cues (Blue vehicles).

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
pip install pylatexenc