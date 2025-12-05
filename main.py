import traci
import os
import sys
import time
import warnings
import matplotlib.pyplot as plt
import numpy as np
from traffic_model import TrafficNetwork
from qubo_generator import QUBOGenerator
from solver import QAOATrafficSolver
from visualization import TrafficVisualizer

# --- CONFIGURATION ---
MAX_STEPS = 3600
ANIMATION_DELAY = 0.02
YELLOW_DURATION = 4

warnings.filterwarnings("ignore")
try:
    from scipy.sparse import SparseEfficiencyWarning
    warnings.simplefilter('ignore', SparseEfficiencyWarning)
except ImportError:
    pass

def get_sumo_binary(gui=True):
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
    else:
        sys.exit("Please declare environment variable 'SUMO_HOME'")
    return "sumo-gui" if gui else "sumo"

def show_final_report(history, stats, title="Simulation Results"):
    print(f"\n=== Generating Dashboard for: {title} ===")
    if not history['time']:
        print("No simulation data collected.")
        return

    plt.style.use('default') 
    fig, (ax_graph, ax_table) = plt.subplots(2, 1, figsize=(10, 8))
    fig.suptitle(f"{title} - Detailed Analysis", fontsize=16, weight='bold')
    
    ax_graph.plot(history['time'], history['total_queue'], color='blue', linewidth=1.5, label="Total Stopped Cars")
    ax_graph.set_title("Network Congestion Profile", fontsize=12)
    ax_graph.set_xlabel("Simulation Step (s)")
    ax_graph.set_ylabel("Total Queue Length")
    ax_graph.grid(True, alpha=0.3)
    ax_graph.legend()

    ax_table.axis('tight'); ax_table.axis('off')
    
    table_data = []
    columns = ["Direction", "Avg Queue", "Max Queue", "Avg Wait (s)"]
    
    for direction, data in stats.items():
        avg_q = np.mean(data["queues"]) if data["queues"] else 0
        max_q = np.max(data["queues"]) if data["queues"] else 0
        avg_w = np.mean(data["wait_time"]) if data["wait_time"] else 0
        table_data.append([direction, f"{avg_q:.2f}", f"{max_q}", f"{avg_w:.2f}"])

    all_q = [x for d in stats.values() for x in d['queues']]
    all_w = [x for d in stats.values() for x in d['wait_time']]
    if all_q:
        table_data.append(["NETWORK TOTAL", f"{np.mean(all_q):.2f}", f"{np.max(all_q)}", f"{np.mean(all_w):.2f}"])

    the_table = ax_table.table(cellText=table_data, colLabels=columns, loc='center', cellLoc='center')
    the_table.auto_set_font_size(False); the_table.set_fontsize(12); the_table.scale(1, 1.8)
    for i in range(len(columns)):
        cell = the_table[(5, i)]; cell.set_facecolor('#e6e6e6'); cell.set_text_props(weight='bold')

    plt.tight_layout()
    print(">> Please CLOSE this window to proceed.")
    plt.show(block=True)

def check_emergency_vehicles(lanes_map):
    """
    Scans for ambulances safely.
    """
    lane_phase_map = {
        "n_in_0": 0, "s_in_0": 0,
        "e_in_0": 2, "w_in_0": 2
    }
    
    for lane_id, phase in lane_phase_map.items():
        try:
            # Safe call: if lane doesn't exist, this throws error, caught by except
            veh_ids = traci.lane.getLastStepVehicleIDs(lane_id)
            for veh in veh_ids:
                if traci.vehicle.getTypeID(veh) == "ambulance":
                    return True, phase
        except:
            # If lane doesn't exist, just skip it
            continue
    return False, -1

def run_simulation(gui=True, use_qaoa=True, label="Simulation"):
    print(f"\n>>> STARTING {label} (GUI={gui}, QAOA={use_qaoa}) <<<")
    sumo_cmd = [get_sumo_binary(gui), "-c", "config.sumocfg", "--start", "--step-length", "0.1"]
    
    try:
        traci.start(sumo_cmd)
    except Exception as e:
        print(f"CRITICAL ERROR: Could not start SUMO. Error: {e}")
        return None, None
    
    # Wait for SUMO to initialize ports
    time.sleep(1)

    net = TrafficNetwork()
    net.create_intersection(1)
    solver = QAOATrafficSolver()
    
    stats = {
        "North": {"queues": [], "wait_time": []},
        "South": {"queues": [], "wait_time": []},
        "East":  {"queues": [], "wait_time": []},
        "West":  {"queues": [], "wait_time": []}
    }
    history = {"time": [], "total_queue": [], "queue_variance": [], "total_co2": []}
    
    yellow_timer = 0
    target_phase = -1
    decision_interval = 100 
    current_sim_time = 0
    step = 0

    try:
        while current_sim_time < MAX_STEPS:
            try:
                traci.simulationStep()
            except traci.TraCIException:
                print("Simulation closed by SUMO.")
                break
            
            # --- 1. Data Collection ---
            if step % 10 == 0:
                try:
                    # Safe Data Collection
                    n = traci.lane.getLastStepVehicleNumber("n_in_0")
                    s = traci.lane.getLastStepVehicleNumber("s_in_0")
                    e = traci.lane.getLastStepVehicleNumber("e_in_0")
                    w = traci.lane.getLastStepVehicleNumber("w_in_0")
                    
                    nw = traci.lane.getWaitingTime("n_in_0")
                    sw = traci.lane.getWaitingTime("s_in_0")
                    ew = traci.lane.getWaitingTime("e_in_0")
                    ww = traci.lane.getWaitingTime("w_in_0")
                    
                    # Safe CO2 Collection
                    co2 = 0
                    for lid in ["n_in_0", "s_in_0", "e_in_0", "w_in_0"]:
                        try: co2 += traci.lane.getCO2Emission(lid)
                        except: pass
                except Exception as e:
                    # If lanes don't exist, use zeros to prevent crash
                    print(f"Warning: Lane ID error ({e}). Using 0 values.")
                    n=s=e=w=nw=sw=ew=ww=co2=0

                stats["North"]["queues"].append(n); stats["North"]["wait_time"].append(nw)
                stats["South"]["queues"].append(s); stats["South"]["wait_time"].append(sw)
                stats["East"]["queues"].append(e);  stats["East"]["wait_time"].append(ew)
                stats["West"]["queues"].append(w);  stats["West"]["wait_time"].append(ww)
                
                total_q = n + s + e + w
                variance = np.var([n, s, e, w]) if any([n,s,e,w]) else 0

                history['time'].append(current_sim_time)
                history['total_queue'].append(total_q)
                history['queue_variance'].append(variance)
                history['total_co2'].append(co2)

            # --- 2. Control Logic ---
            if use_qaoa:
                # SAFE EMERGENCY CHECK
                emergency_found, emergency_phase = check_emergency_vehicles(None)
                
                if emergency_found:
                    current_phase = traci.trafficlight.getPhase("J1")
                    if current_phase != emergency_phase and target_phase != emergency_phase:
                        print(f"!!! AMBULANCE DETECTED !!! Forcing Phase {emergency_phase}")
                        target_phase = emergency_phase
                        yellow_timer = 2 
                
                elif yellow_timer > 0:
                    yellow_timer -= 0.1
                    if yellow_timer <= 0:
                        traci.trafficlight.setPhase("J1", target_phase)
                        yellow_timer = 0
                
                elif step % decision_interval == 0:
                    # SAFE PEDESTRIAN CHECK (The likely cause of previous crash)
                    peds_n = 0
                    try:
                        peds_n = traci.edge.getLastStepPersonNumber("n_in")
                        if peds_n > 5:
                            print("High Pedestrian Traffic Detected.")
                    except:
                        # If edge 'n_in' doesn't exist, just ignore pedestrians
                        pass
                    
                    # QAOA Logic
                    current_traffic = {
                        "N_1": n, "S_1": s, "E_1": e, "W_1": w
                    }
                    net.update_queues(current_traffic, current_co2=0)
                    
                    if sum(current_traffic.values()) > 0:
                        qubo = QUBOGenerator(net, lambda_4=100.0).generate_qubo()
                        solution = solver.solve(qubo)
                        mode = solution.get(1, 0)
                        
                        current_phase = traci.trafficlight.getPhase("J1")
                        desired_phase = -1
                        if mode == 1: desired_phase = 0 
                        elif mode == 3: desired_phase = 2 
                        
                        if desired_phase != -1 and desired_phase != current_phase:
                            if current_phase == 0:
                                traci.trafficlight.setPhase("J1", 1) 
                                target_phase = 2 
                                yellow_timer = YELLOW_DURATION
                            elif current_phase == 2:
                                traci.trafficlight.setPhase("J1", 3) 
                                target_phase = 0 
                                yellow_timer = YELLOW_DURATION
            
            step += 1
            current_sim_time += 0.1
            if gui and ANIMATION_DELAY > 0:
                time.sleep(ANIMATION_DELAY)

    except KeyboardInterrupt:
        print(f"Stopped {label} by User.")
    except Exception as e:
        print(f"Error in main loop: {e}")
    finally:
        try:
            traci.close()
            # Give SUMO time to fully close before next run
            time.sleep(2)
        except:
            pass
        print(f">>> FINISHED {label}")
        return history, stats

if __name__ == "__main__":
    visualizer = TrafficVisualizer()

    print("--- Phase 1: Running Baseline (Fixed Time) ---")
    baseline_history, _ = run_simulation(gui=False, use_qaoa=False, label="BASELINE")
    
    if baseline_history is None or not baseline_history['time']:
        print("Baseline failed (likely lane ID mismatch). Aborting.")
        sys.exit()

    print("\n--- Phase 2: Running QAOA (Quantum Optimized + EVP + CO2) ---")
    qaoa_history, qaoa_stats = run_simulation(gui=True, use_qaoa=True, label="QAOA")
    
    if qaoa_history and qaoa_history['time']:
        print("\n=== GENERATING REPORTS ===")
        # 1. Original Dashboard
        show_final_report(qaoa_history, qaoa_stats, title="QAOA Run Stats")
        
        # 2. Diagnostics (Congestion, Variance, CO2)
        visualizer.generate_qaoa_diagnostics(qaoa_history)
        
        # 3. Final Comparison
        visualizer.generate_comparison_report(baseline_history, qaoa_history)
    else:
        print("QAOA run failed or gathered no data.")