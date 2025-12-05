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
MAX_STEPS = 1500          
ANIMATION_DELAY = 0.0     
YELLOW_DURATION = 4      
EMERGENCY_YELLOW = 2     

# Weather Settings
RAIN_MODE = False          
RAIN_START_TIME = 15      
RAIN_FRICTION = 0.6       
RAIN_SIGMA = 0.9          

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
    if not history['time']:
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
    lane_phase_map = {"n_in_0": 0, "s_in_0": 0, "e_in_0": 2, "w_in_0": 2}
    for lane_id, phase in lane_phase_map.items():
        try:
            veh_ids = traci.lane.getLastStepVehicleIDs(lane_id)
            for veh in veh_ids:
                if traci.vehicle.getTypeID(veh) == "ambulance":
                    return True, phase
        except: continue
    return False, -1

def check_bus_priority():
    current_phase = traci.trafficlight.getPhase("J1")
    green_lanes = []
    if current_phase == 0: green_lanes = ["n_in_0", "s_in_0"]
    elif current_phase == 2: green_lanes = ["e_in_0", "w_in_0"]
    for lane in green_lanes:
        try:
            veh_ids = traci.lane.getLastStepVehicleIDs(lane)
            for veh in veh_ids:
                if traci.vehicle.getTypeID(veh) == "bus":
                    return True 
        except: pass
    return False

def check_dilemma_zone():
    current_phase = traci.trafficlight.getPhase("J1")
    green_lanes = []
    if current_phase == 0: green_lanes = ["n_in_0", "s_in_0"]
    elif current_phase == 2: green_lanes = ["e_in_0", "w_in_0"]
    for lane in green_lanes:
        try:
            veh_ids = traci.lane.getLastStepVehicleIDs(lane)
            lane_len = traci.lane.getLength(lane)
            for veh in veh_ids:
                speed = traci.vehicle.getSpeed(veh) 
                pos = traci.vehicle.getLanePosition(veh)
                dist_to_stop = lane_len - pos
                if speed > 10 and 10 < dist_to_stop < 40:
                    return True
        except: pass
    return False

def apply_weather_physics():
    try:
        veh_ids = traci.vehicle.getIDList()
        for veh in veh_ids:
            v_type = traci.vehicle.getTypeID(veh)
            if v_type == "ambulance": continue
            if v_type == "bus":
                traci.vehicle.setImperfection(veh, RAIN_SIGMA)
                traci.vehicle.setSpeedFactor(veh, 0.7) 
                continue
            traci.vehicle.setColor(veh, (0, 0, 139, 255)) 
            traci.vehicle.setImperfection(veh, RAIN_SIGMA)
            traci.vehicle.setSpeedFactor(veh, 0.8)
    except: pass

def calculate_dynamic_green_time(queue_length):
    if queue_length < 5: return 10 
    elif queue_length < 15: return 20 
    else: return 35 

def run_presentation_scenario(step):
    if step == 300:
        print(f"\n[DEMO SCRIPT] 🚑 Spawning Ambulance (North) for EVP Test...")
        try:
            vid = f"user_amb_{step}"
            traci.route.add(f"route_user_amb_{step}", ["n_in", "s_out"])
            traci.vehicle.add(vid, f"route_user_amb_{step}", typeID="ambulance")
        except: pass
        
    elif step == 500:
        print(f"\n[DEMO SCRIPT] 🚌 Spawning Bus (East) for Priority Test...")
        try:
            vid = f"user_bus_{step}"
            traci.route.add(f"route_user_bus_{step}", ["e_in", "w_out"])
            traci.vehicle.add(vid, f"route_user_bus_{step}", typeID="bus")
        except: pass
        
    elif step == 700:
        print(f"\n[DEMO SCRIPT] ⚠️ Spawning High-Speed Car for Dilemma Zone Test...")
        try:
            vid = f"user_fast_{step}"
            traci.route.add(f"route_user_fast_{step}", ["n_in", "s_out"])
            traci.vehicle.add(vid, f"route_user_fast_{step}", typeID="car")
            traci.vehicle.setColor(vid, (255, 0, 0, 255)) 
            traci.vehicle.setSpeedMode(vid, 0) 
            traci.vehicle.setSpeed(vid, 25) 
        except: pass

def run_simulation(gui=True, use_qaoa=True, label="Simulation", is_proactive=False):
    print(f"\n>>> STARTING {label} (GUI={gui}, QAOA={use_qaoa}) <<<")
    
    sumo_cmd = [get_sumo_binary(gui), "-c", "config.sumocfg", "--start", "--step-length", "0.1"]
    try:
        traci.start(sumo_cmd)
    except Exception as e:
        print(f"CRITICAL ERROR: Could not start SUMO. Error: {e}")
        return None, None, None 
    
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
    next_decision_step = 100 
    current_sim_time = 0
    step = 0
    last_qubo = None 
    weather_alert_printed = False

    try:
        while current_sim_time < MAX_STEPS:
            try: traci.simulationStep()
            except: break
            
            if gui and use_qaoa:
                run_presentation_scenario(step)
            
            if RAIN_MODE and current_sim_time > RAIN_START_TIME:
                if step % 50 == 0:
                    apply_weather_physics()
                    if not weather_alert_printed and gui:
                        print(f"\n[WEATHER] 🌧️ STORM STARTED at {current_sim_time:.1f}s!")
                        weather_alert_printed = True

            if step % 10 == 0:
                try:
                    n = traci.lane.getLastStepVehicleNumber("n_in_0")
                    s = traci.lane.getLastStepVehicleNumber("s_in_0")
                    e = traci.lane.getLastStepVehicleNumber("e_in_0")
                    w = traci.lane.getLastStepVehicleNumber("w_in_0")
                    
                    n_app = traci.edge.getLastStepVehicleNumber("n_in")
                    s_app = traci.edge.getLastStepVehicleNumber("s_in")
                    e_app = traci.edge.getLastStepVehicleNumber("e_in")
                    w_app = traci.edge.getLastStepVehicleNumber("w_in")
                    
                    nw = traci.lane.getWaitingTime("n_in_0"); sw = traci.lane.getWaitingTime("s_in_0")
                    ew = traci.lane.getWaitingTime("e_in_0"); ww = traci.lane.getWaitingTime("w_in_0")
                    co2 = 0
                    for lid in ["n_in_0", "s_in_0", "e_in_0", "w_in_0"]:
                        try: co2 += traci.lane.getCO2Emission(lid)
                        except: pass
                except: n=s=e=w=nw=sw=ew=ww=co2=0; n_app=s_app=e_app=w_app=0

                stats["North"]["queues"].append(n); stats["South"]["queues"].append(s); stats["East"]["queues"].append(e);  stats["West"]["queues"].append(w)
                stats["North"]["wait_time"].append(nw); stats["South"]["wait_time"].append(sw); stats["East"]["wait_time"].append(ew); stats["West"]["wait_time"].append(ww)
                total_q = n + s + e + w; variance = np.var([n, s, e, w]) if any([n,s,e,w]) else 0
                history['time'].append(current_sim_time); history['total_queue'].append(total_q); history['queue_variance'].append(variance); history['total_co2'].append(co2)

            if use_qaoa:
                if yellow_timer > 0:
                    yellow_timer -= 0.1
                    if yellow_timer <= 0:
                        traci.trafficlight.setPhase("J1", target_phase)
                
                if yellow_timer <= 0:
                    emergency_found, emergency_phase = check_emergency_vehicles(None); current_phase = traci.trafficlight.getPhase("J1")

                    if emergency_found:
                        if current_phase != emergency_phase:
                            print(f"!!! AMBULANCE DETECTED !!! Switching to Phase {emergency_phase}")
                            target_phase = emergency_phase; yellow_timer = EMERGENCY_YELLOW; next_decision_step = step + 50 
                    elif step >= next_decision_step:
                        if check_dilemma_zone():
                             print(f"   -> [SAFETY] ⚠️ Dilemma Zone! Fast car approaching. Extending Green 2s.")
                             next_decision_step = step + 20 
                        elif check_bus_priority():
                             print(f"   -> [BUS PRIORITY] 🚌 Bus detected. Extending Green 5s.")
                             next_decision_step = step + 50 
                        else:
                            current_traffic = {"N_1": n, "S_1": s, "E_1": e, "W_1": w}
                            approaching_traffic = {"n_in": n_app, "s_in": s_app, "e_in": e_app, "w_in": w_app}
                            
                            net.update_queues(current_traffic, current_co2=0)
                            
                            if sum(current_traffic.values()) > 0:
                                # [PASSING PROACTIVE FLAG]
                                qubo = QUBOGenerator(net, current_traffic, approaching_traffic, is_proactive=is_proactive).generate_qubo()
                                last_qubo = qubo 
                                
                                solution = solver.solve(qubo); mode = solution.get(1, 0)
                                desired_phase = -1
                                if mode == 1: desired_phase = 0 
                                elif mode == 3: desired_phase = 2 
                                
                                target_queue_size = 0
                                if mode == 1: target_queue_size = n + s
                                elif mode == 3: target_queue_size = e + w
                                
                                green_time_seconds = calculate_dynamic_green_time(target_queue_size)
                                next_decision_step = step + (green_time_seconds * 10) 
                                
                                if desired_phase != -1 and desired_phase != current_phase:
                                    print(f"   -> [ADAPTIVE] Queue: {target_queue_size}. Switch & Hold {green_time_seconds}s. ({'Proactive' if is_proactive else 'Reactive'})")
                                    target_phase = desired_phase; yellow_timer = YELLOW_DURATION
                                else:
                                    print(f"   -> [ADAPTIVE] Queue: {target_queue_size}. Extend {green_time_seconds}s. ({'Proactive' if is_proactive else 'Reactive'})")
                            else:
                                next_decision_step = step + 50
            
            step += 1; current_sim_time += 0.1
            if gui and ANIMATION_DELAY > 0: time.sleep(ANIMATION_DELAY)

    except KeyboardInterrupt: print(f"Stopped {label} by User.");
    except Exception as e: print(f"Error in main loop: {e}"); time.sleep(5)
    finally:
        try: traci.close(); time.sleep(2)
        except: pass
        print(f">>> FINISHED {label}")
        return history, stats, last_qubo

if __name__ == "__main__":
    visualizer = TrafficVisualizer()
    solver_instance = QAOATrafficSolver()

    # --- PHASE 1: BASELINE (Fixed Time) ---
    print("--- Phase 1: Running Baseline (Fixed Time) ---")
    baseline_history, baseline_stats, _ = run_simulation(gui=False, use_qaoa=False, label="BASELINE", is_proactive=False)
    
    if not baseline_history or not baseline_history['time']:
        sys.exit()

    # --- PHASE 2: REACTIVE QAOA (No Lookahead) ---
    print("\n--- Phase 2: Running Reactive QAOA (No Prediction) ---")
    reactive_history, _, _ = run_simulation(gui=False, use_qaoa=True, label="REACTIVE", is_proactive=False)

    # --- PHASE 3: PROACTIVE QAOA (Full System Demo) ---
    print("\n--- Phase 3: Running Proactive QAOA (Full System Demo) ---")
    proactive_history, proactive_stats, last_qubo = run_simulation(gui=True, use_qaoa=True, label="PROACTIVE", is_proactive=True)
    
    if proactive_history and proactive_history['time']:
        print("\n=== GENERATING REPORTS ===")
        
        # 1. Quantum Circuit Diagram
        if last_qubo:
            solver_instance.save_circuit_diagram(last_qubo)
            
        # 2. Stats Dashboard (Based on Proactive Run)
        show_final_report(proactive_history, proactive_stats, title="Proactive QAOA Run Stats")
        
        # 3. Diagnostics (CO2, Variance)
        visualizer.generate_qaoa_diagnostics(proactive_history)
        
        # 4. Bar Chart (Baseline vs Proactive Stats)
        visualizer.generate_before_after_bars(baseline_stats, proactive_stats)

        # 5. Proactive vs Reactive Timeline [NEW GRAPH]
        if reactive_history and reactive_history['time']:
             visualizer.generate_proactive_comparison(reactive_history, proactive_history)
        
        # 6. Baseline vs Proactive Timeline
        visualizer.generate_comparison_report(baseline_history, proactive_history)
    else:
        print("QAOA run failed or gathered no data.")