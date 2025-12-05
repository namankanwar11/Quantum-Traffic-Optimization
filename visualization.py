import matplotlib.pyplot as plt
import numpy as np
import os

class TrafficVisualizer:
    def __init__(self):
        self.save_dir = "results"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    # ... (Existing methods: generate_qaoa_diagnostics, generate_comparison_report, generate_before_after_bars) ...

    def generate_qaoa_diagnostics(self, history):
        print("\n=== Generating QAOA Diagnostics Graphs ===")
        if not history['time']:
             print("No data to visualize.")
             return

        plt.figure(figsize=(18, 5))

        # Plot 1: Congestion
        plt.subplot(1, 3, 1)
        plt.plot(history['time'], history['total_queue'], color='tab:blue', label='Total Vehicles')
        plt.xlabel("Step")
        plt.ylabel("Count")
        plt.title("Congestion Reduction")
        plt.grid(True, alpha=0.3)
        plt.legend()

        # Plot 2: Balancing
        plt.subplot(1, 3, 2)
        if 'queue_variance' in history:
            plt.plot(history['time'], history['queue_variance'], color='tab:green', label='Variance')
            plt.xlabel("Step")
            plt.ylabel("Variance")
            plt.title("Traffic Signal Balancing")
            plt.grid(True, alpha=0.3)
            plt.legend()

        # Plot 3: CO2
        plt.subplot(1, 3, 3)
        if 'total_co2' in history:
            co2_g = [x / 1000 for x in history['total_co2']]
            plt.plot(history['time'], co2_g, color='tab:red', label='CO2 Emissions')
            plt.xlabel("Step")
            plt.ylabel("Emissions (g/sec)")
            plt.title("Environmental Impact (CO2)")
            plt.grid(True, alpha=0.3)
            plt.legend()

        plt.tight_layout()
        save_path = os.path.join(self.save_dir, "qaoa_diagnostics.png")
        plt.savefig(save_path)
        print(f"Diagnostics saved to: {save_path}")
        plt.show(block=False) 
        plt.pause(0.1)

    def generate_comparison_report(self, baseline_history, qaoa_history):
        print("\n=== BASELINE VS QAOA COMPARISON REPORT ===")
        
        # Calculate comparison stats... (omitted for brevity)

        min_len = min(len(baseline_history['time']), len(qaoa_history['time']))
        plot_time = qaoa_history['time'][:min_len]
        plot_base_q = baseline_history['total_queue'][:min_len]
        plot_qaoa_q = qaoa_history['total_queue'][:min_len]

        plt.figure(figsize=(12, 6))
        plt.plot(plot_time, plot_base_q, color='grey', linestyle='--', label='Baseline')
        plt.plot(plot_time, plot_qaoa_q, color='green', linewidth=2, label='QAOA Optimized')
        plt.fill_between(plot_time, plot_base_q, plot_qaoa_q, color='green', alpha=0.1)

        plt.title("Traffic Congestion Profile: Before (Baseline) vs After (QAOA)", fontsize=14)
        plt.xlabel("Simulation Step (s)")
        plt.ylabel("Total Queue Length")
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        save_path = os.path.join(self.save_dir, "comparison_result.png")
        plt.savefig(save_path)
        plt.show(block=True)

    def generate_before_after_bars(self, baseline_stats, qaoa_stats):
        # ... (implementation omitted for brevity) ...
        pass

    def generate_proactive_comparison(self, reactive_history, proactive_history):
        """
        [NEW FEATURE] Proactive QAOA vs Reactive QAOA
        """
        print("\n=== PROACTIVE VS REACTIVE QAOA COMPARISON ===")
        
        react_avg = np.mean(reactive_history['total_queue']) if reactive_history['total_queue'] else 0
        proact_avg = np.mean(proactive_history['total_queue']) if proactive_history['total_queue'] else 0
        
        improvement = ((react_avg - proact_avg) / react_avg) * 100 if react_avg > 0 else 0
        
        min_len = min(len(reactive_history['time']), len(proactive_history['time']))
        plot_time = proactive_history['time'][:min_len]
        plot_react_q = reactive_history['total_queue'][:min_len]
        plot_proact_q = proactive_history['total_queue'][:min_len]

        plt.figure(figsize=(10, 5))
        
        plt.plot(plot_time, plot_react_q, color='red', linestyle='--', label='Reactive QAOA (No Lookahead)')
        plt.plot(plot_time, plot_proact_q, color='blue', linewidth=2, label='Proactive QAOA (With Prediction)')
        
        plt.title(f"Proactive vs Reactive: Congestion Analysis (Proactive Gain: {improvement:.2f}%)")
        plt.xlabel("Simulation Step (s)")
        plt.ylabel("Total Queue Length")
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        save_path = os.path.join(self.save_dir, "proactive_vs_reactive.png")
        plt.savefig(save_path)
        print(f"Proactive comparison graph saved to: {save_path}")
        plt.show(block=True)