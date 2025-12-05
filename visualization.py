import matplotlib.pyplot as plt
import numpy as np
import os

class TrafficVisualizer:
    def __init__(self):
        self.save_dir = "results"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def generate_qaoa_diagnostics(self, history):
        print("\n=== Generating QAOA Diagnostics Graphs ===")
        if not history['time']:
             print("No data to visualize.")
             return

        plt.figure(figsize=(18, 5))

        # --- Plot 1: Congestion ---
        plt.subplot(1, 3, 1)
        plt.plot(history['time'], history['total_queue'], color='tab:blue', label='Total Vehicles')
        plt.xlabel("Step")
        plt.ylabel("Count")
        plt.title("Congestion Reduction")
        plt.grid(True, alpha=0.3)
        plt.legend()

        # --- Plot 2: Balancing ---
        plt.subplot(1, 3, 2)
        if 'queue_variance' in history:
            plt.plot(history['time'], history['queue_variance'], color='tab:green', label='Variance')
            plt.xlabel("Step")
            plt.ylabel("Variance")
            plt.title("Traffic Signal Balancing")
            plt.grid(True, alpha=0.3)
            plt.legend()

        # --- Plot 3: Environmental Impact (CO2) ---
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
        print(">> Please CLOSE this window to proceed.")
        plt.show(block=True)

    def generate_comparison_report(self, baseline_history, qaoa_history):
        print("\n=== FINAL COMPARISON REPORT ===")
        
        # 1. Comparison Stats (Using full available data)
        base_avg = np.mean(baseline_history['total_queue']) if baseline_history['total_queue'] else 0
        qaoa_avg = np.mean(qaoa_history['total_queue']) if qaoa_history['total_queue'] else 0
        improvement = ((base_avg - qaoa_avg) / base_avg) * 100 if base_avg > 0 else 0
        
        base_co2 = np.sum(baseline_history.get('total_co2', [0]))
        qaoa_co2 = np.sum(qaoa_history.get('total_co2', [0]))
        co2_imp = ((base_co2 - qaoa_co2) / base_co2) * 100 if base_co2 > 0 else 0

        print(f"Congestion Improvement: {improvement:.2f}%")
        print(f"CO2 Reduction:          {co2_imp:.2f}%")

        # 2. Graphing (Fix: Slice data to match minimum length)
        min_len = min(len(baseline_history['time']), len(qaoa_history['time']))
        
        # Create sliced arrays for plotting so dimensions match
        plot_time = qaoa_history['time'][:min_len]
        plot_base_q = baseline_history['total_queue'][:min_len]
        plot_qaoa_q = qaoa_history['total_queue'][:min_len]

        plt.figure(figsize=(12, 6))
        
        # Plot Baseline (Sliced)
        plt.plot(plot_time, plot_base_q, color='grey', linestyle='--', label='Baseline')
        
        # Plot QAOA (Sliced)
        plt.plot(plot_time, plot_qaoa_q, color='green', linewidth=2, label='QAOA Optimized')
        
        # Fill Between (Now safe because sizes match)
        plt.fill_between(plot_time, plot_base_q, plot_qaoa_q, color='green', alpha=0.1)

        plt.title(f"Traffic Congestion (Imp: {improvement:.1f}%) | CO2 Red: {co2_imp:.1f}%", fontsize=14)
        plt.xlabel("Simulation Step (s)")
        plt.ylabel("Total Queue Length")
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        save_path = os.path.join(self.save_dir, "comparison_result.png")
        plt.savefig(save_path)
        plt.show(block=True)