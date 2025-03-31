import tkinter as tk
from tkinter import ttk, messagebox
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import webbrowser
from ..config.training_config import ConfigManager
from ..checkpoint_manager import CheckpointManager
from ..owner.interface.training_monitor import TrainingMonitor
from ..visualization.learning_visualizer import LearningVisualizer
from ...config.logging_config import logger

class LearningHubInterface:
    """Unified interface for managing training activities"""
    
    def __init__(self, root: Optional[tk.Tk] = None):
        self.root = root or tk.Tk()
        self.root.title("ADE Learning Hub")
        self.root.geometry("1200x800")
        
        # Initialize components
        self.config_manager = ConfigManager()
        self.checkpoint_manager = CheckpointManager("data/learning/training")
        self.monitor = TrainingMonitor()
        self.visualizer = LearningVisualizer()
        
        # Create main interface
        self._create_interface()
        
    def _create_interface(self):
        """Create the main interface"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.training_tab = self._create_training_tab()
        self.monitoring_tab = self._create_monitoring_tab()
        self.visualization_tab = self._create_visualization_tab()
        self.config_tab = self._create_config_tab()
        self.analysis_tab = self._create_analysis_tab()
        self.layout_tab = self._create_layout_tab()
        
        # Add tabs to notebook
        self.notebook.add(self.training_tab, text="Training")
        self.notebook.add(self.monitoring_tab, text="Monitoring")
        self.notebook.add(self.visualization_tab, text="Visualization")
        self.notebook.add(self.config_tab, text="Configuration")
        self.notebook.add(self.analysis_tab, text="Analysis")
        self.notebook.add(self.layout_tab, text="Layout")
        
        # Start real-time updates
        self._start_real_time_updates()
        
    def _create_training_tab(self) -> ttk.Frame:
        """Create training management tab"""
        frame = ttk.Frame(self.notebook)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Training controls
        controls_frame = ttk.LabelFrame(frame, text="Training Controls")
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Config selection
        ttk.Label(controls_frame, text="Configuration:").grid(row=0, column=0, padx=5, pady=5)
        self.config_var = tk.StringVar()
        self.config_combo = ttk.Combobox(controls_frame, textvariable=self.config_var)
        self.config_combo['values'] = self._get_config_names()
        self.config_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Output directory
        ttk.Label(controls_frame, text="Output Directory:").grid(row=0, column=2, padx=5, pady=5)
        self.output_dir_var = tk.StringVar(value="data/learning/training")
        ttk.Entry(controls_frame, textvariable=self.output_dir_var).grid(row=0, column=3, padx=5, pady=5)
        
        # Resume from checkpoint
        ttk.Label(controls_frame, text="Resume From:").grid(row=1, column=0, padx=5, pady=5)
        self.resume_var = tk.StringVar()
        self.resume_combo = ttk.Combobox(controls_frame, textvariable=self.resume_var)
        self.resume_combo['values'] = self._get_checkpoint_paths()
        self.resume_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # Port
        ttk.Label(controls_frame, text="Port:").grid(row=1, column=2, padx=5, pady=5)
        self.port_var = tk.StringVar(value="8000")
        ttk.Entry(controls_frame, textvariable=self.port_var).grid(row=1, column=3, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(controls_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Start Training", command=self._start_training).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Stop Training", command=self._stop_training).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Resume Training", command=self._resume_training).pack(side=tk.LEFT, padx=5)
        
        # Active sessions
        sessions_frame = ttk.LabelFrame(frame, text="Active Sessions")
        sessions_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview
        self.sessions_tree = ttk.Treeview(sessions_frame, columns=("config", "started", "episode"))
        self.sessions_tree.heading("config", text="Config")
        self.sessions_tree.heading("started", text="Started")
        self.sessions_tree.heading("episode", text="Episode")
        self.sessions_tree.pack(fill=tk.BOTH, expand=True)
        
        # Refresh button
        ttk.Button(sessions_frame, text="Refresh", command=self._refresh_sessions).pack(pady=5)
        
        return frame
        
    def _create_monitoring_tab(self) -> ttk.Frame:
        """Create monitoring tab"""
        frame = ttk.Frame(self.notebook)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Session selection
        session_frame = ttk.LabelFrame(frame, text="Session Selection")
        session_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(session_frame, text="Session:").pack(side=tk.LEFT, padx=5)
        self.monitor_session_var = tk.StringVar()
        self.monitor_session_combo = ttk.Combobox(session_frame, textvariable=self.monitor_session_var)
        self.monitor_session_combo['values'] = self._get_session_ids()
        self.monitor_session_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(session_frame, text="Show Metrics", command=self._show_metrics).pack(side=tk.LEFT, padx=5)
        ttk.Button(session_frame, text="Open Dashboard", command=self._open_dashboard).pack(side=tk.LEFT, padx=5)
        
        # Metrics display
        metrics_frame = ttk.LabelFrame(frame, text="Metrics")
        metrics_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.metrics_text = tk.Text(metrics_frame, wrap=tk.WORD)
        self.metrics_text.pack(fill=tk.BOTH, expand=True)
        
        return frame
        
    def _create_visualization_tab(self) -> ttk.Frame:
        """Create visualization tab"""
        frame = ttk.Frame(self.notebook)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Visualization controls
        controls_frame = ttk.LabelFrame(frame, text="Visualization Controls")
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Session selection
        ttk.Label(controls_frame, text="Session:").pack(side=tk.LEFT, padx=5)
        self.viz_session_var = tk.StringVar()
        self.viz_session_combo = ttk.Combobox(controls_frame, textvariable=self.viz_session_var)
        self.viz_session_combo['values'] = self._get_session_ids()
        self.viz_session_combo.pack(side=tk.LEFT, padx=5)
        
        # Visualization type
        ttk.Label(controls_frame, text="Type:").pack(side=tk.LEFT, padx=5)
        self.viz_type_var = tk.StringVar(value="dashboard")
        viz_types = ["dashboard", "rewards", "accuracy", "exploration", "learning_curves"]
        ttk.Combobox(controls_frame, textvariable=self.viz_type_var, values=viz_types).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(controls_frame, text="Generate", command=self._generate_visualization).pack(side=tk.LEFT, padx=5)
        
        # Preview frame
        preview_frame = ttk.LabelFrame(frame, text="Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.preview_text = tk.Text(preview_frame, wrap=tk.WORD)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        
        return frame
        
    def _create_config_tab(self) -> ttk.Frame:
        """Create configuration management tab"""
        frame = ttk.Frame(self.notebook)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Config selection
        config_frame = ttk.LabelFrame(frame, text="Configuration")
        config_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(config_frame, text="Config:").pack(side=tk.LEFT, padx=5)
        self.edit_config_var = tk.StringVar()
        self.edit_config_combo = ttk.Combobox(config_frame, textvariable=self.edit_config_var)
        self.edit_config_combo['values'] = self._get_config_names()
        self.edit_config_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(config_frame, text="Edit", command=self._edit_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(config_frame, text="Save As", command=self._save_config_as).pack(side=tk.LEFT, padx=5)
        
        # Config editor
        editor_frame = ttk.LabelFrame(frame, text="Editor")
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.config_editor = tk.Text(editor_frame, wrap=tk.WORD)
        self.config_editor.pack(fill=tk.BOTH, expand=True)
        
        return frame
        
    def _create_analysis_tab(self) -> ttk.Frame:
        """Create analysis tab"""
        frame = ttk.Frame(self.notebook)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Analysis controls
        controls_frame = ttk.LabelFrame(frame, text="Analysis Controls")
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Session selection
        ttk.Label(controls_frame, text="Session:").pack(side=tk.LEFT, padx=5)
        self.analysis_session_var = tk.StringVar()
        self.analysis_session_combo = ttk.Combobox(controls_frame, textvariable=self.analysis_session_var)
        self.analysis_session_combo['values'] = self._get_session_ids()
        self.analysis_session_combo.pack(side=tk.LEFT, padx=5)
        
        # Analysis type
        ttk.Label(controls_frame, text="Type:").pack(side=tk.LEFT, padx=5)
        self.analysis_type_var = tk.StringVar(value="model_architecture")
        analysis_types = [
            "model_architecture",
            "code_coverage",
            "performance_metrics",
            "hyperparameter_analysis"
        ]
        ttk.Combobox(controls_frame, textvariable=self.analysis_type_var, values=analysis_types).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(controls_frame, text="Generate", command=self._generate_analysis).pack(side=tk.LEFT, padx=5)
        
        # Analysis preview
        preview_frame = ttk.LabelFrame(frame, text="Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.analysis_preview = tk.Text(preview_frame, wrap=tk.WORD)
        self.analysis_preview.pack(fill=tk.BOTH, expand=True)
        
        return frame
        
    def _create_layout_tab(self) -> ttk.Frame:
        """Create layout management tab"""
        frame = ttk.Frame(self.notebook)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Layout controls
        controls_frame = ttk.LabelFrame(frame, text="Layout Controls")
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Layout selection
        ttk.Label(controls_frame, text="Layout:").pack(side=tk.LEFT, padx=5)
        self.layout_var = tk.StringVar(value="default")
        layouts = ["default", "grid", "custom"]
        ttk.Combobox(controls_frame, textvariable=self.layout_var, values=layouts).pack(side=tk.LEFT, padx=5)
        
        # Layout editor
        editor_frame = ttk.LabelFrame(frame, text="Layout Editor")
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create grid editor
        self.grid_editor = ttk.Frame(editor_frame)
        self.grid_editor.pack(fill=tk.BOTH, expand=True)
        
        # Grid size
        size_frame = ttk.Frame(self.grid_editor)
        size_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(size_frame, text="Rows:").pack(side=tk.LEFT, padx=5)
        self.rows_var = tk.StringVar(value="2")
        ttk.Entry(size_frame, textvariable=self.rows_var).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(size_frame, text="Columns:").pack(side=tk.LEFT, padx=5)
        self.cols_var = tk.StringVar(value="2")
        ttk.Entry(size_frame, textvariable=self.cols_var).pack(side=tk.LEFT, padx=5)
        
        # Grid preview
        preview_frame = ttk.LabelFrame(self.grid_editor, text="Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.grid_preview = ttk.Frame(preview_frame)
        self.grid_preview.pack(fill=tk.BOTH, expand=True)
        
        # Widget selection
        widget_frame = ttk.LabelFrame(self.grid_editor, text="Widgets")
        widget_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create notebook for widget types
        widget_notebook = ttk.Notebook(widget_frame)
        widget_notebook.pack(fill=tk.X, padx=5, pady=5)
        
        # Basic widgets tab
        basic_frame = ttk.Frame(widget_notebook)
        widget_notebook.add(basic_frame, text="Basic")
        
        self.basic_widgets = tk.Listbox(basic_frame, selectmode=tk.MULTIPLE)
        self.basic_widgets.pack(fill=tk.X, padx=5, pady=5)
        self.basic_widgets.insert(tk.END, "Rewards Plot")
        self.basic_widgets.insert(tk.END, "Accuracy Plot")
        self.basic_widgets.insert(tk.END, "Memory Usage")
        self.basic_widgets.insert(tk.END, "Code Quality")
        
        # Advanced widgets tab
        advanced_frame = ttk.Frame(widget_notebook)
        widget_notebook.add(advanced_frame, text="Advanced")
        
        self.advanced_widgets = tk.Listbox(advanced_frame, selectmode=tk.MULTIPLE)
        self.advanced_widgets.pack(fill=tk.X, padx=5, pady=5)
        self.advanced_widgets.insert(tk.END, "Model Architecture")
        self.advanced_widgets.insert(tk.END, "Gradient Flow")
        self.advanced_widgets.insert(tk.END, "Attention Maps")
        self.advanced_widgets.insert(tk.END, "Performance Metrics")
        
        # Custom widgets tab
        custom_frame = ttk.Frame(widget_notebook)
        widget_notebook.add(custom_frame, text="Custom")
        
        # Custom widget editor
        custom_editor = ttk.Frame(custom_frame)
        custom_editor.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(custom_editor, text="Name:").pack(side=tk.LEFT, padx=5)
        self.custom_name_var = tk.StringVar()
        ttk.Entry(custom_editor, textvariable=self.custom_name_var).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(custom_editor, text="Type:").pack(side=tk.LEFT, padx=5)
        self.custom_type_var = tk.StringVar(value="plot")
        ttk.Combobox(custom_editor, textvariable=self.custom_type_var, values=["plot", "table", "metric"]).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(custom_editor, text="Add", command=self._add_custom_widget).pack(side=tk.LEFT, padx=5)
        
        # Custom widgets list
        self.custom_widgets = tk.Listbox(custom_frame, selectmode=tk.MULTIPLE)
        self.custom_widgets.pack(fill=tk.X, padx=5, pady=5)
        
        # Layout actions
        action_frame = ttk.Frame(self.grid_editor)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(action_frame, text="Update Grid", command=self._update_grid_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Save Layout", command=self._save_layout).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Load Layout", command=self._load_layout).pack(side=tk.LEFT, padx=5)
        
        return frame
        
    def _get_config_names(self) -> List[str]:
        """Get list of available configuration names"""
        try:
            return self.config_manager.list_configs()
        except Exception as e:
            logger.error(f"Error getting config names: {str(e)}")
            return []
            
    def _get_checkpoint_paths(self) -> List[str]:
        """Get list of available checkpoint paths"""
        try:
            checkpoints = self.checkpoint_manager.list_checkpoints()
            return [checkpoint['path'] for checkpoint in checkpoints]
        except Exception as e:
            logger.error(f"Error getting checkpoint paths: {str(e)}")
            return []
            
    def _get_session_ids(self) -> List[str]:
        """Get list of active session IDs"""
        try:
            return list(self.monitor.active_sessions.keys())
        except Exception as e:
            logger.error(f"Error getting session IDs: {str(e)}")
            return []
            
    def _start_training(self):
        """Start a new training session"""
        try:
            config_name = self.config_var.get()
            output_dir = self.output_dir_var.get()
            resume_from = self.resume_var.get()
            port = int(self.port_var.get())
            
            if not config_name:
                messagebox.showerror("Error", "Please select a configuration")
                return
                
            # Start training
            self.monitor.start_session(config_name, config_name)
            self.monitor.run(port=port)
            
            # Refresh sessions
            self._refresh_sessions()
            
        except Exception as e:
            logger.error(f"Error starting training: {str(e)}")
            messagebox.showerror("Error", str(e))
            
    def _stop_training(self):
        """Stop selected training session"""
        try:
            selected = self.sessions_tree.selection()
            if not selected:
                messagebox.showerror("Error", "Please select a session to stop")
                return
                
            session_id = selected[0]
            self.monitor.end_session(session_id)
            
            # Refresh sessions
            self._refresh_sessions()
            
        except Exception as e:
            logger.error(f"Error stopping training: {str(e)}")
            messagebox.showerror("Error", str(e))
            
    def _resume_training(self):
        """Resume training from checkpoint"""
        try:
            checkpoint_path = self.resume_var.get()
            if not checkpoint_path:
                messagebox.showerror("Error", "Please select a checkpoint")
                return
                
            # Resume training
            self._start_training()
            
        except Exception as e:
            logger.error(f"Error resuming training: {str(e)}")
            messagebox.showerror("Error", str(e))
            
    def _refresh_sessions(self):
        """Refresh active sessions display"""
        try:
            # Clear treeview
            for item in self.sessions_tree.get_children():
                self.sessions_tree.delete(item)
                
            # Add sessions
            for session_id, session in self.monitor.active_sessions.items():
                self.sessions_tree.insert("", "end", text=session_id, values=(
                    session['config'],
                    session['start_time'],
                    session['current_episode']
                ))
                
        except Exception as e:
            logger.error(f"Error refreshing sessions: {str(e)}")
            
    def _show_metrics(self):
        """Show metrics for selected session"""
        try:
            session_id = self.monitor_session_var.get()
            if not session_id:
                messagebox.showerror("Error", "Please select a session")
                return
                
            session = self.monitor.active_sessions[session_id]
            
            # Format metrics
            metrics_text = f"Metrics for session {session_id}:\n\n"
            metrics_text += f"Average Reward: {np.mean(session['metrics']['rewards']):.2f}\n"
            metrics_text += f"Completion Accuracy: {np.mean(session['metrics']['accuracy']):.2f}\n"
            metrics_text += f"Exploration Rate: {np.mean(session['metrics']['exploration']):.2f}\n"
            
            self.metrics_text.delete(1.0, tk.END)
            self.metrics_text.insert(tk.END, metrics_text)
            
        except Exception as e:
            logger.error(f"Error showing metrics: {str(e)}")
            messagebox.showerror("Error", str(e))
            
    def _open_dashboard(self):
        """Open training dashboard in browser"""
        try:
            session_id = self.monitor_session_var.get()
            if not session_id:
                messagebox.showerror("Error", "Please select a session")
                return
                
            session = self.monitor.active_sessions[session_id]
            dashboard_path = self.visualizer.create_dashboard(session['metrics'], session['current_episode'])
            
            if dashboard_path:
                webbrowser.open(f"file://{dashboard_path}")
                
        except Exception as e:
            logger.error(f"Error opening dashboard: {str(e)}")
            messagebox.showerror("Error", str(e))
            
    def _generate_visualization(self):
        """Generate selected visualization"""
        try:
            session_id = self.viz_session_var.get()
            viz_type = self.viz_type_var.get()
            
            if not session_id:
                messagebox.showerror("Error", "Please select a session")
                return
                
            session = self.monitor.active_sessions[session_id]
            
            # Generate visualization
            if viz_type == "dashboard":
                viz_path = self.visualizer.create_dashboard(session['metrics'], session['current_episode'])
            elif viz_type == "rewards":
                viz_path = self.visualizer.create_reward_plot(session['metrics']['rewards'], session['current_episode'])
            elif viz_type == "accuracy":
                viz_path = self.visualizer.create_completion_accuracy_plot(session['metrics']['accuracy'], session['current_episode'])
            elif viz_type == "exploration":
                viz_path = self.visualizer.create_exploration_plot(session['metrics']['exploration'], session['current_episode'])
            else:  # learning_curves
                viz_path = self.visualizer.create_learning_curves(session['metrics'], session['current_episode'])
                
            if viz_path:
                self.preview_text.delete(1.0, tk.END)
                self.preview_text.insert(tk.END, f"Generated visualization: {viz_path}")
                webbrowser.open(f"file://{viz_path}")
                
        except Exception as e:
            logger.error(f"Error generating visualization: {str(e)}")
            messagebox.showerror("Error", str(e))
            
    def _edit_config(self):
        """Edit selected configuration"""
        try:
            config_name = self.edit_config_var.get()
            if not config_name:
                messagebox.showerror("Error", "Please select a configuration")
                return
                
            config = self.config_manager.load_config(config_name)
            
            # Format config as YAML
            config_yaml = yaml.dump(config.__dict__, default_flow_style=False)
            
            # Show in editor
            self.config_editor.delete(1.0, tk.END)
            self.config_editor.insert(tk.END, config_yaml)
            
        except Exception as e:
            logger.error(f"Error editing config: {str(e)}")
            messagebox.showerror("Error", str(e))
            
    def _save_config_as(self):
        """Save configuration as new file"""
        try:
            config_name = self.edit_config_var.get()
            if not config_name:
                messagebox.showerror("Error", "Please select a configuration")
                return
                
            # Get new name
            new_name = tk.simpledialog.askstring("Save As", "Enter new configuration name:")
            if not new_name:
                return
                
            # Get config from editor
            config_yaml = self.config_editor.get(1.0, tk.END)
            config_dict = yaml.safe_load(config_yaml)
            
            # Save config
            self.config_manager.save_config(new_name, config_dict)
            
            # Refresh config list
            self.config_combo['values'] = self._get_config_names()
            self.edit_config_combo['values'] = self._get_config_names()
            
        except Exception as e:
            logger.error(f"Error saving config: {str(e)}")
            messagebox.showerror("Error", str(e))
            
    def _start_real_time_updates(self):
        """Start real-time updates"""
        try:
            # Update metrics every second
            self.root.after(1000, self._update_metrics)
            
            # Update visualizations every 5 seconds
            self.root.after(5000, self._update_visualizations)
            
        except Exception as e:
            logger.error(f"Error starting real-time updates: {str(e)}")
            
    def _update_metrics(self):
        """Update metrics in real-time"""
        try:
            if self.monitor_session_var.get():
                self._show_metrics()
                
            # Schedule next update
            self.root.after(1000, self._update_metrics)
            
        except Exception as e:
            logger.error(f"Error updating metrics: {str(e)}")
            
    def _update_visualizations(self):
        """Update visualizations in real-time"""
        try:
            if self.viz_session_var.get():
                self._generate_visualization()
                
            # Schedule next update
            self.root.after(5000, self._update_visualizations)
            
        except Exception as e:
            logger.error(f"Error updating visualizations: {str(e)}")
            
    def _generate_analysis(self):
        """Generate selected analysis"""
        try:
            session_id = self.analysis_session_var.get()
            analysis_type = self.analysis_type_var.get()
            
            if not session_id:
                messagebox.showerror("Error", "Please select a session")
                return
                
            session = self.monitor.active_sessions[session_id]
            
            # Generate analysis
            if analysis_type == "model_architecture":
                viz_path = self.visualizer.create_model_architecture(
                    session['model'],
                    session['current_episode']
                )
            elif analysis_type == "code_coverage":
                viz_path = self.visualizer.create_code_coverage_metrics(
                    session['coverage_data'],
                    session['current_episode']
                )
            elif analysis_type == "performance_metrics":
                viz_path = self.visualizer.create_performance_metrics(
                    session['performance_data'],
                    session['current_episode']
                )
            else:  # hyperparameter_analysis
                viz_path = self.visualizer.create_hyperparameter_analysis(
                    session['hyperparameter_data']
                )
                
            if viz_path:
                self.analysis_preview.delete(1.0, tk.END)
                self.analysis_preview.insert(tk.END, f"Generated analysis: {viz_path}")
                webbrowser.open(f"file://{viz_path}")
                
        except Exception as e:
            logger.error(f"Error generating analysis: {str(e)}")
            messagebox.showerror("Error", str(e))
            
    def _update_grid_preview(self):
        """Update grid preview"""
        try:
            # Clear preview
            for widget in self.grid_preview.winfo_children():
                widget.destroy()
                
            # Get grid size
            rows = int(self.rows_var.get())
            cols = int(self.cols_var.get())
            
            # Configure grid
            for i in range(rows):
                self.grid_preview.grid_rowconfigure(i, weight=1)
            for i in range(cols):
                self.grid_preview.grid_columnconfigure(i, weight=1)
                
            # Add preview cells
            for i in range(rows):
                for j in range(cols):
                    cell = ttk.Label(self.grid_preview, text=f"Cell {i},{j}")
                    cell.grid(row=i, column=j, padx=2, pady=2, sticky="nsew")
                    
        except Exception as e:
            logger.error(f"Error updating grid preview: {str(e)}")
            messagebox.showerror("Error", str(e))
            
    def _save_layout(self):
        """Save current layout"""
        try:
            # Get layout data
            layout_data = {
                'type': self.layout_var.get(),
                'rows': int(self.rows_var.get()),
                'columns': int(self.cols_var.get()),
                'widgets': self.widget_list.curselection()
            }
            
            # Save to file
            filename = tk.filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")]
            )
            
            if filename:
                with open(filename, 'w') as f:
                    json.dump(layout_data, f, indent=2)
                    
                messagebox.showinfo("Success", "Layout saved successfully")
                
        except Exception as e:
            logger.error(f"Error saving layout: {str(e)}")
            messagebox.showerror("Error", str(e))
            
    def _load_layout(self):
        """Load layout from file"""
        try:
            filename = tk.filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json")]
            )
            
            if filename:
                with open(filename, 'r') as f:
                    layout_data = json.load(f)
                    
                # Update layout
                self.layout_var.set(layout_data['type'])
                self.rows_var.set(str(layout_data['rows']))
                self.cols_var.set(str(layout_data['columns']))
                
                # Update widget selection
                self.widget_list.selection_clear(0, tk.END)
                for index in layout_data['widgets']:
                    self.widget_list.selection_set(index)
                    
                # Update preview
                self._update_grid_preview()
                
                messagebox.showinfo("Success", "Layout loaded successfully")
                
        except Exception as e:
            logger.error(f"Error loading layout: {str(e)}")
            messagebox.showerror("Error", str(e))
            
    def _apply_layout(self, session_id: str):
        """Apply selected layout to session"""
        try:
            if not session_id:
                return
                
            session = self.monitor.active_sessions[session_id]
            
            # Get layout data
            layout_type = self.layout_var.get()
            rows = int(self.rows_var.get())
            cols = int(self.cols_var.get())
            selected_widgets = [self.widget_list.get(i) for i in self.widget_list.curselection()]
            
            # Create dashboard with layout
            dashboard_path = self.visualizer.create_dashboard(
                session['metrics'],
                session['current_episode'],
                layout={
                    'type': layout_type,
                    'rows': rows,
                    'columns': cols,
                    'widgets': selected_widgets
                }
            )
            
            if dashboard_path:
                webbrowser.open(f"file://{dashboard_path}")
                
        except Exception as e:
            logger.error(f"Error applying layout: {str(e)}")
            messagebox.showerror("Error", str(e))
            
    def _add_custom_widget(self):
        """Add custom widget to the list"""
        try:
            name = self.custom_name_var.get()
            widget_type = self.custom_type_var.get()
            
            if not name:
                messagebox.showerror("Error", "Please enter a widget name")
                return
                
            # Add to custom widgets list
            self.custom_widgets.insert(tk.END, f"{name} ({widget_type})")
            
            # Clear input
            self.custom_name_var.set("")
            
        except Exception as e:
            logger.error(f"Error adding custom widget: {str(e)}")
            messagebox.showerror("Error", str(e))
            
    def run(self):
        """Run the interface"""
        self.root.mainloop()

if __name__ == '__main__':
    interface = LearningHubInterface()
    interface.run() 