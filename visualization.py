import matplotlib.pyplot as plt
import numpy as np
import os

class TrafficVisualizer:
    def __init__(self):
        self.save_dir = "results"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def generate_qaoa_diagnostics(self, history):
        """
        [NEW FEATURE] Generates the specific "Congestion Reduction" and 
        "Signal Balancing" graphs requested.
        """
        print("\n=== Generating QAOA Diagnostics Graphs ===")
        if not history['time']:
             print("No data to visualize.")
             return

        plt.figure(figsize=(12, 5))

        # --- Plot 1: Real-Time Congestion Reduction ---
        plt.subplot(1, 2, 1)
        # Using total_queue as the metric for total vehicles
        plt.plot(history['time'], history['total_queue'], color='tab:blue', label='QAOA Controlled')
        plt.xlabel("Simulation Step (s)")
        plt.ylabel("Total Vehicles")
        plt.title("Real-Time Congestion Reduction")
        plt.grid(True, alpha=0.3)
        plt.legend()

        # --- Plot 2: Traffic Signal Balancing (Variance) ---
        # Variance measures how uneven the queues are. Lower variance = better balance.
        if 'queue_variance' in history and history['queue_variance']:
            plt.subplot(1, 2, 2)
            plt.plot(history['time'], history['queue_variance'], color='tab:green', label='Queue Variance')
            plt.xlabel("Simulation Step (s)")
            plt.ylabel("Variance (Imbalance)")
            plt.title("Traffic Signal Balancing")
            plt.grid(True, alpha=0.3)
            plt.legend()

        plt.tight_layout()
        save_path = os.path.join(self.save_dir, "qaoa_diagnostics.png")
        plt.savefig(save_path)
        print(f"QAOA diagnostics graphs saved to: {save_path}")
        print(">> Please CLOSE this window to proceed to the Final Comparison.")
        plt.show(block=True)

    def generate_comparison_report(self, baseline_history, qaoa_history):
        print("\n=== FINAL COMPARISON REPORT ===")
        
        # Calculate Averages based on 'total_queue'
        base_avg = np.mean(baseline_history['total_queue'])
        qaoa_avg = np.mean(qaoa_history['total_queue'])
        improvement = ((base_avg - qaoa_avg) / base_avg) * 100 if base_avg > 0 else 0
        
        print(f"Baseline Avg Congestion: {base_avg:.2f} cars")
        print(f"QAOA Avg Congestion:     {qaoa_avg:.2f} cars")
        print(f"Improvement:             {improvement:.2f}%")

        plt.figure(figsize=(12, 6))
        
        plt.plot(baseline_history['time'], baseline_history['total_queue'], 
                 color='grey', linestyle='--', label='Baseline (Fixed Time)')
        
        plt.plot(qaoa_history['time'], qaoa_history['total_queue'], 
                 color='green', linewidth=2, label='QAOA Optimized')
        
        # Fill area to highlight improvement
        plt.fill_between(qaoa_history['time'], baseline_history['total_queue'], 
                         qaoa_history['total_queue'], color='green', alpha=0.1)

        plt.title(f"Before vs After: Traffic Congestion (Imp: {improvement:.1f}%)", fontsize=14)
        plt.xlabel("Simulation Step (s)")
        plt.ylabel("Total Queue Length")
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        save_path = os.path.join(self.save_dir, "comparison_result.png")
        plt.savefig(save_path)
        print(f"Comparison graph saved to: {save_path}")
        plt.show(block=True)