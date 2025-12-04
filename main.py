import traci
import os
import sys
import time
import warnings
import matplotlib.pyplot as plt
import numpy as np

# --- CONFIGURATION ---
MAX_STEPS = 3600        # Run for 1 hour traffic time
# A tiny delay (e.g., 0.02s) makes the animation smooth to the human eye
# 0.0 = As fast as possible (Jerky)
# 0.05 = Smooth 20 FPS
ANIMATION_DELAY = 0.02  
YELLOW_DURATION = 4     # Seconds for yellow light
# ---------------------

# Filter warnings
warnings.filterwarnings("ignore")
try:
    from scipy.sparse import SparseEfficiencyWarning
    warnings.simplefilter('ignore', SparseEfficiencyWarning)
except ImportError:
    pass

from traffic_model import TrafficNetwork
from qubo_generator import QUBOGenerator
from solver import QAOATrafficSolver

def get_sumo_binary():
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
    else:
        sys.exit("Please declare environment variable 'SUMO_HOME'")
    return "sumo-gui"

def show_final_report(history, stats):
    """
    Generates a Dashboard with a Graph AND a Table after simulation ends.
    """
    print("\n=== Generating Final Report... ===")
    
    if not history['time']:
        print("No simulation data collected. Skipping report.")
        return

    plt.style.use('default') 
    fig, (ax_graph, ax_table) = plt.subplots(2, 1, figsize=(10, 8))
    fig.suptitle("Quantum Traffic Optimization Results", fontsize=16, weight='bold')
    
    # --- 1. THE GRAPH ---
    ax_graph.plot(history['time'], history['total_queue'], color='blue', linewidth=1.5, label="Total Stopped Cars")
    ax_graph.set_title("Network Congestion Profile", fontsize=12)
    ax_graph.set_xlabel("Simulation Step (s)")
    ax_graph.set_ylabel("Total Queue Length")
    ax_graph.grid(True, alpha=0.3)
    ax_graph.legend()

    # --- 2. THE TABLE ---
    ax_table.axis('tight')
    ax_table.axis('off')
    
    table_data = []
    columns = ["Direction", "Avg Queue (Cars)", "Max Queue (Cars)", "Avg Wait Time (s)"]
    
    for direction, data in stats.items():
        avg_q = np.mean(data["queues"]) if data["queues"] else 0
        max_q = np.max(data["queues"]) if data["queues"] else 0
        avg_w = np.mean(data["wait_time"]) if data["wait_time"] else 0
        
        table_data.append([
            direction, 
            f"{avg_q:.2f}", 
            f"{max_q}", 
            f"{avg_w:.2f}"
        ])

    all_q = [x for d in stats.values() for x in d['queues']]
    all_w = [x for d in stats.values() for x in d['wait_time']]
    
    if all_q:
        table_data.append([
            "NETWORK TOTAL",
            f"{np.mean(all_q):.2f}",
            f"{np.max(all_q)}",
            f"{np.mean(all_w):.2f}"
        ])

    the_table = ax_table.table(
        cellText=table_data,
        colLabels=columns,
        loc='center',
        cellLoc='center'
    )
    the_table.auto_set_font_size(False)
    the_table.set_fontsize(12)
    the_table.scale(1, 1.8)

    for i in range(len(columns)):
        cell = the_table[(5, i)]
        cell.set_facecolor('#e6e6e6')
        cell.set_text_props(weight='bold')

    plt.tight_layout()
    plt.show(block=True)

def run():
    print(f"=== Quantum Traffic Simulation Starting (Max Steps: {MAX_STEPS}) ===")
    
    # 1. Start SUMO
    # We add "--step-length 0.1" to make the physics smoother (10 frames per second of traffic time)
    sumo_cmd = [
        get_sumo_binary(), 
        "-c", "config.sumocfg", 
        "--start",
        "--step-length", "0.1" 
    ]
    traci.start(sumo_cmd)
    
    # 2. Setup Solver
    net = TrafficNetwork()
    net.create_intersection(1)
    solver = QAOATrafficSolver()
    
    # 3. Initialize Data Storage
    stats = {
        "North": {"queues": [], "wait_time": []},
        "South": {"queues": [], "wait_time": []},
        "East":  {"queues": [], "wait_time": []},
        "West":  {"queues": [], "wait_time": []}
    }
    history = {"time": [], "total_queue": []}

    yellow_timer = 0
    target_phase = -1

    # We track time in seconds, but loop runs in 0.1s steps
    # So 10 seconds = 100 simulation steps
    decision_interval = 100 
    current_sim_time = 0

    step = 0
    try:
        while current_sim_time < MAX_STEPS:
            try:
                traci.simulationStep()
            except traci.TraCIException:
                print("Simulation closed by user.")
                break
            
            # --- A. DATA COLLECTION (Every 1 second / 10 steps) ---
            if step % 10 == 0:
                n_cars = traci.lane.getLastStepVehicleNumber("n_in_0")
                s_cars = traci.lane.getLastStepVehicleNumber("s_in_0")
                e_cars = traci.lane.getLastStepVehicleNumber("e_in_0")
                w_cars = traci.lane.getLastStepVehicleNumber("w_in_0")
                
                n_wait = traci.lane.getWaitingTime("n_in_0")
                s_wait = traci.lane.getWaitingTime("s_in_0")
                e_wait = traci.lane.getWaitingTime("e_in_0")
                w_wait = traci.lane.getWaitingTime("w_in_0")

                stats["North"]["queues"].append(n_cars); stats["North"]["wait_time"].append(n_wait)
                stats["South"]["queues"].append(s_cars); stats["South"]["wait_time"].append(s_wait)
                stats["East"]["queues"].append(e_cars);  stats["East"]["wait_time"].append(e_wait)
                stats["West"]["queues"].append(w_cars);  stats["West"]["wait_time"].append(w_wait)

                total_q = n_cars + s_cars + e_cars + w_cars
                history['time'].append(current_sim_time)
                history['total_queue'].append(total_q)
            
            # --- B. YELLOW LIGHT LOGIC ---
            if yellow_timer > 0:
                # Decrease timer by step length (0.1s)
                yellow_timer -= 0.1
                if yellow_timer <= 0:
                    traci.trafficlight.setPhase("J1", target_phase)
                    print(f"   -> Switched to Green Phase {target_phase}")
                    yellow_timer = 0
            
            # --- C. QUANTUM DECISION (Every 10 seconds of sim time) ---
            elif step % decision_interval == 0:
                # We need fresh data for the decision
                n_cars = traci.lane.getLastStepVehicleNumber("n_in_0")
                s_cars = traci.lane.getLastStepVehicleNumber("s_in_0")
                e_cars = traci.lane.getLastStepVehicleNumber("e_in_0")
                w_cars = traci.lane.getLastStepVehicleNumber("w_in_0")
                current_traffic = {"N_1": n_cars, "S_1": s_cars, "E_1": e_cars, "W_1": w_cars}
                
                net.update_queues(current_traffic)
                
                if sum(current_traffic.values()) > 0:
                    qubo_gen = QUBOGenerator(net, lambda_4=200.0)
                    qubo = qubo_gen.generate_qubo()
                    solution = solver.solve(qubo)
                    
                    mode = solution.get(1, 0)
                    current_phase = traci.trafficlight.getPhase("J1")
                    
                    desired_phase = -1
                    if mode == 1: desired_phase = 0 
                    elif mode == 3: desired_phase = 2 
                    
                    if desired_phase != -1 and desired_phase != current_phase:
                        print(f"[Time {int(current_sim_time)}s] QAOA Requests Switch: Mode {mode}")
                        
                        if current_phase == 0:
                            traci.trafficlight.setPhase("J1", 1) 
                            target_phase = 2 
                            yellow_timer = YELLOW_DURATION
                        elif current_phase == 2:
                            traci.trafficlight.setPhase("J1", 3) 
                            target_phase = 0 
                            yellow_timer = YELLOW_DURATION
            
            step += 1
            current_sim_time += 0.1 # We are stepping by 0.1s
            
            # Tiny delay to make animation visible to human eye
            if ANIMATION_DELAY > 0:
                time.sleep(ANIMATION_DELAY)

    except KeyboardInterrupt:
        print("Stopped by User.")
    finally:
        try:
            traci.close()
        except:
            pass
        
        print("Simulation Ended. Showing results...")
        show_final_report(history, stats)

if __name__ == "__main__":
    run()