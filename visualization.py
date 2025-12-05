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
        # print(">> Please CLOSE this window to proceed.")
        plt.show(block=False) # Don't block flow, show next graph immediately
        plt.pause(0.1)

    def generate_comparison_report(self, baseline_history, qaoa_history):
        print("\n=== FINAL COMPARISON REPORT ===")
        
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
        """
        [NEW FEATURE] Bar Chart for Before vs After Metrics
        """
        # Calculate Network Totals
        def get_avg_wait(stats):
            all_w = [x for d in stats.values() for x in d['wait_time']]
            return np.mean(all_w) if all_w else 0

        def get_avg_queue(stats):
            all_q = [x for d in stats.values() for x in d['queues']]
            return np.mean(all_q) if all_q else 0

        base_wait = get_avg_wait(baseline_stats)
        qaoa_wait = get_avg_wait(qaoa_stats)
        
        base_queue = get_avg_queue(baseline_stats)
        qaoa_queue = get_avg_queue(qaoa_stats)

        # Plot
        labels = ['Avg Wait Time (s)', 'Avg Queue Length (cars)']
        baseline_vals = [base_wait, base_queue]
        qaoa_vals = [qaoa_wait, qaoa_queue]

        x = np.arange(len(labels))
        width = 0.35

        plt.figure(figsize=(10, 6))
        rects1 = plt.bar(x - width/2, baseline_vals, width, label='Before (Baseline)', color='grey')
        rects2 = plt.bar(x + width/2, qaoa_vals, width, label='After (QAOA)', color='green')

        plt.ylabel('Value')
        plt.title('Performance Metrics: Before vs After')
        plt.xticks(x, labels)
        plt.legend()
        plt.grid(axis='y', alpha=0.3)

        # Add labels on top
        def autolabel(rects):
            for rect in rects:
                height = rect.get_height()
                plt.annotate(f'{height:.1f}',
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3), textcoords="offset points",
                            ha='center', va='bottom')

        autolabel(rects1)
        autolabel(rects2)

        save_path = os.path.join(self.save_dir, "before_vs_after_bars.png")
        plt.savefig(save_path)
        print(f"Bar chart saved to: {save_path}")
        plt.show(block=True)