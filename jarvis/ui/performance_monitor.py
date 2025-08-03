"""
Performance Monitor GUI for JARVIS
--------------------------------
A real-time monitoring dashboard for JARVIS AI performance metrics.
"""

import tkinter as tk
from tkinter import ttk
import json
import time
import threading
import queue
from typing import Dict, List, Optional, Any
from dataclasses import asdict

# Import JARVIS AI components
from jarvis.ai.ai_task_router import AITaskRouter
from jarvis.ai.fallback_ai_manager import FallbackAIManager

class PerformanceMonitor:
    """Real-time performance monitoring dashboard for JARVIS AI."""
    
    def __init__(self, root: tk.Tk, update_interval: int = 2000):
        """
        Initialize the performance monitor.
        
        Args:
            root: The root Tkinter window
            update_interval: Update interval in milliseconds
        """
        self.root = root
        self.update_interval = update_interval
        self.running = False
        
        # Initialize AI components
        self.task_router = AITaskRouter()
        self.fallback_manager = FallbackAIManager()
        
        # Data queues for thread-safe updates
        self.metrics_queue = queue.Queue()
        self.command_queue = queue.Queue()
        
        # Setup the UI
        self._setup_ui()
        
        # Start the update thread
        self._start_update_thread()
    
    def _setup_ui(self):
        """Set up the user interface."""
        self.root.title("JARVIS AI Performance Monitor")
        self.root.geometry("1200x800")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Create main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # System status frame
        status_frame = ttk.LabelFrame(main_frame, text="System Status", padding="10")
        status_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # System status labels
        self.gpu_status = self._create_status_label(status_frame, "GPU Status:", "Checking...", 0)
        self.gpu_memory = self._create_status_label(status_frame, "GPU Memory:", "-", 1)
        self.overall_health = self._create_status_label(status_frame, "Overall Health:", "-", 2)
        
        # Models frame
        models_frame = ttk.LabelFrame(main_frame, text="AI Models", padding="10")
        models_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Models treeview
        self.models_tree = ttk.Treeview(
            models_frame, 
            columns=('status', 'memory', 'success_rate', 'last_used'),
            show='headings',
            selectmode='browse'
        )
        
        # Configure columns
        self.models_tree.heading('status', text='Status')
        self.models_tree.heading('memory', text='Memory (MB)')
        self.models_tree.heading('success_rate', text='Success Rate')
        self.models_tree.heading('last_used', text='Last Used')
        
        # Set column widths
        self.models_tree.column('status', width=100, anchor=tk.CENTER)
        self.models_tree.column('memory', width=100, anchor=tk.CENTER)
        self.models_tree.column('success_rate', width=100, anchor=tk.CENTER)
        self.models_tree.column('last_used', width=150, anchor=tk.CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(models_frame, orient=tk.VERTICAL, command=self.models_tree.yview)
        self.models_tree.configure(yscroll=scrollbar.set)
        
        # Grid the tree and scrollbar
        self.models_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights
        models_frame.columnconfigure(0, weight=1)
        models_frame.rowconfigure(0, weight=1)
        
        # Performance metrics frame
        metrics_frame = ttk.LabelFrame(main_frame, text="Performance Metrics", padding="10")
        metrics_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Add charts/gauges here (placeholder for now)
        self.metrics_canvas = tk.Canvas(metrics_frame, bg='white', width=400, height=300)
        self.metrics_canvas.pack(expand=True, fill=tk.BOTH)
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="System Log", padding="10")
        log_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Log text widget
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, height=10)
        self.log_text.pack(expand=True, fill=tk.BOTH)
        
        # Add scrollbar to log
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Control buttons
        self.start_button = ttk.Button(buttons_frame, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(buttons_frame, text="Stop Monitoring", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.refresh_button = ttk.Button(buttons_frame, text="Refresh Now", command=self.refresh_metrics)
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights for main frame
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
    
    def _create_status_label(self, parent: ttk.Frame, label: str, value: str, row: int) -> ttk.Label:
        """Create a status label with a value."""
        ttk.Label(parent, text=label, font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=2)
        value_label = ttk.Label(parent, text=value, font=('Arial', 10))
        value_label.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        return value_label
    
    def _start_update_thread(self):
        """Start the background update thread."""
        self.update_thread = threading.Thread(target=self._update_worker, daemon=True)
        self.running = True
        self.update_thread.start()
        
        # Start the UI update loop
        self._update_ui()
    
    def _update_worker(self):
        """Background worker that updates metrics."""
        while self.running:
            try:
                # Get system metrics
                system_status = self.task_router.get_system_status()
                health_status = self.fallback_manager.get_system_health()
                
                # Put metrics in the queue
                self.metrics_queue.put({
                    'system': system_status,
                    'health': health_status,
                    'timestamp': time.time()
                })
                
                # Sleep for the update interval
                time.sleep(self.update_interval / 1000)
                
            except Exception as e:
                self.log(f"Error in update worker: {str(e)}")
    
    def _update_ui(self):
        """Update the UI with the latest metrics."""
        try:
            # Process any pending metrics updates
            while not self.metrics_queue.empty():
                metrics = self.metrics_queue.get_nowait()
                self._process_metrics(metrics)
            
            # Process any pending commands
            while not self.command_queue.empty():
                command, args = self.command_queue.get_nowait()
                if command == 'log':
                    self.log(args['message'], args.get('level', 'info'))
            
        except Exception as e:
            self.log(f"Error updating UI: {str(e)}", 'error')
        
        # Schedule the next update
        if self.running:
            self.root.after(200, self._update_ui)
    
    def _process_metrics(self, metrics: Dict[str, Any]):
        """Process metrics and update the UI."""
        try:
            system = metrics.get('system', {})
            health = metrics.get('health', {})
            
            # Update system status
            self.gpu_status.config(
                text=f"{'✅' if system.get('gpu_available', False) else '❌'} "
                     f"{'Available' if system.get('gpu_available', False) else 'Unavailable'}"
            )
            
            self.gpu_memory.config(
                text=f"{system.get('gpu_memory_mb', 0):,} MB"
            )
            
            self.overall_health.config(
                text=health.get('overall_health', 'unknown').title(),
                foreground={
                    'healthy': 'green',
                    'degraded': 'orange',
                    'unhealthy': 'red'
                }.get(health.get('overall_health', '').lower(), 'black')
            )
            
            # Update models tree
            self._update_models_tree(health.get('models', {}))
            
            # Update performance metrics
            self._update_performance_metrics(metrics)
            
        except Exception as e:
            self.log(f"Error processing metrics: {str(e)}", 'error')
    
    def _update_models_tree(self, models: Dict[str, Any]):
        """Update the models tree with the latest data."""
        # Clear existing items
        for item in self.models_tree.get_children():
            self.models_tree.delete(item)
        
        # Add models to the tree
        for model_name, model_data in models.items():
            status = model_data.get('status', 'unknown')
            memory = model_data.get('memory_requirement_mb', 0)
            success_rate = model_data.get('success_rate', 0)
            last_used = model_data.get('last_used', 0)
            
            # Format values
            status_icon = {
                'healthy': '✅',
                'degraded': '⚠️',
                'unhealthy': '❌'
            }.get(status.lower(), '❓')
            
            success_pct = f"{success_rate * 100:.1f}%" if isinstance(success_rate, (int, float)) else "N/A"
            last_used_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_used)) if last_used > 0 else "Never"
            
            # Insert into tree
            self.models_tree.insert('', 'end', values=(
                f"{status_icon} {status.title()}",
                f"{memory:,}",
                success_pct,
                last_used_str
            ), tags=(status.lower(),))
            
            # Configure row colors
            if status.lower() == 'healthy':
                self.models_tree.tag_configure('healthy', background='#e6ffe6')
            elif status.lower() == 'degraded':
                self.models_tree.tag_configure('degraded', background='#fff2cc')
            elif status.lower() == 'unhealthy':
                self.models_tree.tag_configure('unhealthy', background='#ffdddd')
    
    def _update_performance_metrics(self, metrics: Dict[str, Any]):
        """Update performance metrics visualization."""
        # This is a placeholder - in a real implementation, you would update charts/gauges here
        pass
    
    def log(self, message: str, level: str = 'info'):
        """Add a message to the log."""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        level_emoji = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '❌',
            'success': '✅'
        }.get(level.lower(), 'ℹ️')
        
        # Insert at the beginning to show newest first
        self.log_text.insert('1.0', f"[{timestamp}] {level_emoji} {message}\n")
        
        # Auto-scroll to the top
        self.log_text.see('1.0')
    
    def start_monitoring(self):
        """Start the monitoring process."""
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.log("Monitoring started", 'info')
    
    def stop_monitoring(self):
        """Stop the monitoring process."""
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log("Monitoring stopped", 'info')
    
    def refresh_metrics(self):
        """Force a refresh of the metrics."""
        self.log("Manual refresh triggered", 'info')
        # Force an immediate update by putting a command in the queue
        self.command_queue.put(('log', {'message': 'Refreshing metrics...', 'level': 'info'}))

def main():
    """Main entry point for the performance monitor."""
    root = tk.Tk()
    app = PerformanceMonitor(root)
    
    # Start monitoring by default
    app.start_monitoring()
    
    # Set window icon and title
    root.title("JARVIS AI Performance Monitor")
    
    # Run the application
    root.mainloop()

if __name__ == "__main__":
    main()
