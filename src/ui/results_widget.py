from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QComboBox, QTableWidget, QTableWidgetItem,
                             QFileDialog, QMessageBox, QGroupBox, QFormLayout,
                             QTextEdit)
from PyQt6.QtCore import Qt
from typing import Dict, Any, Optional
import json
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

class ResultsWidget(QWidget):
    """Widget for displaying training results and metrics"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the results display UI"""
        layout = QVBoxLayout(self)
        
        # Results selection
        selection_group = QGroupBox("Results Selection")
        selection_layout = QHBoxLayout()
        
        self.experiment_combo = QComboBox()
        selection_layout.addWidget(QLabel("Experiment:"))
        selection_layout.addWidget(self.experiment_combo)
        
        self.run_combo = QComboBox()
        selection_layout.addWidget(QLabel("Run:"))
        selection_layout.addWidget(self.run_combo)
        
        selection_group.setLayout(selection_layout)
        layout.addWidget(selection_group)
        
        # Metrics display
        metrics_group = QGroupBox("Metrics")
        metrics_layout = QVBoxLayout()
        
        # Metrics table
        self.metrics_table = QTableWidget()
        self.metrics_table.setColumnCount(3)
        self.metrics_table.setHorizontalHeaderLabels([
            "Metric", "Training", "Validation"
        ])
        metrics_layout.addWidget(self.metrics_table)
        
        # Metrics plot
        self.metrics_plot = FigureCanvas(plt.figure(figsize=(8, 6)))
        metrics_layout.addWidget(self.metrics_plot)
        
        metrics_group.setLayout(metrics_layout)
        layout.addWidget(metrics_group)
        
        # Training curves
        curves_group = QGroupBox("Training Curves")
        curves_layout = QVBoxLayout()
        
        # Loss curve
        self.loss_plot = FigureCanvas(plt.figure(figsize=(8, 4)))
        curves_layout.addWidget(self.loss_plot)
        
        # Learning rate curve
        self.lr_plot = FigureCanvas(plt.figure(figsize=(8, 4)))
        curves_layout.addWidget(self.lr_plot)
        
        curves_group.setLayout(curves_layout)
        layout.addWidget(curves_group)
        
        # Resource usage
        resources_group = QGroupBox("Resource Usage")
        resources_layout = QVBoxLayout()
        
        # Resource usage plot
        self.resources_plot = FigureCanvas(plt.figure(figsize=(8, 4)))
        resources_layout.addWidget(self.resources_plot)
        
        resources_group.setLayout(resources_layout)
        layout.addWidget(resources_group)
        
        # Model performance
        performance_group = QGroupBox("Model Performance")
        performance_layout = QVBoxLayout()
        
        # Performance metrics table
        self.performance_table = QTableWidget()
        self.performance_table.setColumnCount(4)
        self.performance_table.setHorizontalHeaderLabels([
            "Metric", "Training", "Validation", "Test"
        ])
        performance_layout.addWidget(self.performance_table)
        
        # Performance plot
        self.performance_plot = FigureCanvas(plt.figure(figsize=(8, 4)))
        performance_layout.addWidget(self.performance_plot)
        
        performance_group.setLayout(performance_layout)
        layout.addWidget(performance_group)
        
        # Export options
        export_layout = QHBoxLayout()
        
        export_metrics_button = QPushButton("Export Metrics")
        export_metrics_button.clicked.connect(self.export_metrics)
        export_layout.addWidget(export_metrics_button)
        
        export_plots_button = QPushButton("Export Plots")
        export_plots_button.clicked.connect(self.export_plots)
        export_layout.addWidget(export_plots_button)
        
        export_report_button = QPushButton("Export Report")
        export_report_button.clicked.connect(self.export_report)
        export_layout.addWidget(export_report_button)
        
        layout.addLayout(export_layout)
        
        # Connect signals
        self.experiment_combo.currentTextChanged.connect(self.update_run_list)
        self.run_combo.currentTextChanged.connect(self.update_results)
        
    def update_experiment_list(self, experiments: list):
        """Update the experiment selection combobox"""
        self.experiment_combo.clear()
        
        for experiment in experiments:
            self.experiment_combo.addItem(experiment["name"])
            
    def update_run_list(self, experiment: str):
        """Update the run selection combobox based on selected experiment"""
        self.run_combo.clear()
        
        if not experiment:
            return
            
        try:
            # Get runs for selected experiment
            runs = self.parent().model_trainer.get_experiment_runs(experiment)
            
            for run in runs:
                self.run_combo.addItem(run["name"])
                
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to load runs: {str(e)}")
            
    def update_results(self, run: str):
        """Update all results displays based on selected run"""
        if not run:
            return
            
        try:
            # Get results for selected run
            results = self.parent().model_trainer.get_run_results(run)
            
            # Update metrics table
            self.update_metrics_table(results["metrics"])
            
            # Update metrics plot
            self.update_metrics_plot(results["metrics_history"])
            
            # Update training curves
            self.update_training_curves(results["training_history"])
            
            # Update resource usage
            self.update_resource_usage(results["resource_usage"])
            
            # Update performance metrics
            self.update_performance_metrics(results["performance"])
            
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to load results: {str(e)}")
            
    def update_metrics_table(self, metrics: Dict[str, float]):
        """Update the metrics table with current values"""
        self.metrics_table.setRowCount(len(metrics))
        
        for i, (metric, value) in enumerate(metrics.items()):
            # Metric name
            self.metrics_table.setItem(i, 0, QTableWidgetItem(metric))
            
            # Training value
            self.metrics_table.setItem(i, 1, QTableWidgetItem(f"{value:.4f}"))
            
            # Validation value (if available)
            val_value = metrics.get(f"val_{metric}", "N/A")
            self.metrics_table.setItem(i, 2, QTableWidgetItem(str(val_value)))
            
    def update_metrics_plot(self, history: Dict[str, list]):
        """Update the metrics plot with historical data"""
        self.metrics_plot.figure.clear()
        ax = self.metrics_plot.figure.add_subplot(111)
        
        for metric, values in history.items():
            if metric.startswith("val_"):
                continue
            ax.plot(values, label=metric)
            
        ax.set_title("Training Metrics")
        ax.set_xlabel("Step")
        ax.set_ylabel("Value")
        ax.grid(True)
        ax.legend()
        
        self.metrics_plot.draw()
        
    def update_training_curves(self, history: Dict[str, list]):
        """Update the training curves with historical data"""
        # Update loss curve
        self.loss_plot.figure.clear()
        loss_ax = self.loss_plot.figure.add_subplot(111)
        
        if "loss" in history:
            loss_ax.plot(history["loss"], label="Training Loss")
        if "val_loss" in history:
            loss_ax.plot(history["val_loss"], label="Validation Loss")
            
        loss_ax.set_title("Loss Curves")
        loss_ax.set_xlabel("Step")
        loss_ax.set_ylabel("Loss")
        loss_ax.grid(True)
        loss_ax.legend()
        
        self.loss_plot.draw()
        
        # Update learning rate curve
        self.lr_plot.figure.clear()
        lr_ax = self.lr_plot.figure.add_subplot(111)
        
        if "learning_rate" in history:
            lr_ax.plot(history["learning_rate"], label="Learning Rate")
            
        lr_ax.set_title("Learning Rate Schedule")
        lr_ax.set_xlabel("Step")
        lr_ax.set_ylabel("Learning Rate")
        lr_ax.grid(True)
        lr_ax.legend()
        
        self.lr_plot.draw()
        
    def update_resource_usage(self, usage: Dict[str, list]):
        """Update the resource usage plot"""
        self.resources_plot.figure.clear()
        ax = self.resources_plot.figure.add_subplot(111)
        
        for resource, values in usage.items():
            ax.plot(values, label=resource)
            
        ax.set_title("Resource Usage")
        ax.set_xlabel("Time")
        ax.set_ylabel("Usage (%)")
        ax.grid(True)
        ax.legend()
        
        self.resources_plot.draw()
        
    def update_performance_metrics(self, performance: Dict[str, Dict[str, float]]):
        """Update the performance metrics table and plot"""
        # Update performance table
        self.performance_table.setRowCount(len(performance))
        
        for i, (metric, values) in enumerate(performance.items()):
            # Metric name
            self.performance_table.setItem(i, 0, QTableWidgetItem(metric))
            
            # Training value
            self.performance_table.setItem(i, 1, QTableWidgetItem(f"{values['train']:.4f}"))
            
            # Validation value
            self.performance_table.setItem(i, 2, QTableWidgetItem(f"{values['val']:.4f}"))
            
            # Test value
            self.performance_table.setItem(i, 3, QTableWidgetItem(f"{values['test']:.4f}"))
            
        # Update performance plot
        self.performance_plot.figure.clear()
        ax = self.performance_plot.figure.add_subplot(111)
        
        metrics = list(performance.keys())
        train_values = [performance[m]["train"] for m in metrics]
        val_values = [performance[m]["val"] for m in metrics]
        test_values = [performance[m]["test"] for m in metrics]
        
        x = np.arange(len(metrics))
        width = 0.25
        
        ax.bar(x - width, train_values, width, label="Training")
        ax.bar(x, val_values, width, label="Validation")
        ax.bar(x + width, test_values, width, label="Test")
        
        ax.set_title("Model Performance")
        ax.set_xlabel("Metric")
        ax.set_ylabel("Value")
        ax.set_xticks(x)
        ax.set_xticklabels(metrics, rotation=45)
        ax.grid(True)
        ax.legend()
        
        self.performance_plot.draw()
        
    def export_metrics(self):
        """Export metrics to CSV file"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Metrics",
                "",
                "CSV Files (*.csv)"
            )
            
            if not file_path:
                return
                
            # Get current metrics
            metrics = self.parent().model_trainer.get_run_results(
                self.run_combo.currentText()
            )["metrics"]
            
            # Write to CSV
            with open(file_path, 'w') as f:
                f.write("Metric,Training,Validation\n")
                for metric, value in metrics.items():
                    val_value = metrics.get(f"val_{metric}", "N/A")
                    f.write(f"{metric},{value},{val_value}\n")
                    
            QMessageBox.information(self, "Success", "Metrics exported successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export metrics: {str(e)}")
            
    def export_plots(self):
        """Export plots to image files"""
        try:
            dir_path = QFileDialog.getExistingDirectory(
                self,
                "Select Directory for Plots"
            )
            
            if not dir_path:
                return
                
            dir_path = Path(dir_path)
            
            # Save plots
            self.metrics_plot.figure.savefig(dir_path / "metrics.png")
            self.loss_plot.figure.savefig(dir_path / "loss.png")
            self.lr_plot.figure.savefig(dir_path / "learning_rate.png")
            self.resources_plot.figure.savefig(dir_path / "resources.png")
            self.performance_plot.figure.savefig(dir_path / "performance.png")
            
            QMessageBox.information(self, "Success", "Plots exported successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export plots: {str(e)}")
            
    def export_report(self):
        """Export a complete training report"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Report",
                "",
                "HTML Files (*.html)"
            )
            
            if not file_path:
                return
                
            # Get current results
            results = self.parent().model_trainer.get_run_results(
                self.run_combo.currentText()
            )
            
            # Generate HTML report
            html = f"""
            <html>
            <head>
                <title>Training Report - {self.run_combo.currentText()}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    h1, h2 {{ color: #333; }}
                </style>
            </head>
            <body>
                <h1>Training Report</h1>
                <h2>Run Information</h2>
                <p>Experiment: {self.experiment_combo.currentText()}</p>
                <p>Run: {self.run_combo.currentText()}</p>
                
                <h2>Final Metrics</h2>
                <table>
                    <tr>
                        <th>Metric</th>
                        <th>Training</th>
                        <th>Validation</th>
                    </tr>
            """
            
            for metric, value in results["metrics"].items():
                if not metric.startswith("val_"):
                    val_value = results["metrics"].get(f"val_{metric}", "N/A")
                    html += f"""
                    <tr>
                        <td>{metric}</td>
                        <td>{value:.4f}</td>
                        <td>{val_value}</td>
                    </tr>
                    """
                    
            html += """
                </table>
                
                <h2>Performance Summary</h2>
                <table>
                    <tr>
                        <th>Metric</th>
                        <th>Training</th>
                        <th>Validation</th>
                        <th>Test</th>
                    </tr>
            """
            
            for metric, values in results["performance"].items():
                html += f"""
                <tr>
                    <td>{metric}</td>
                    <td>{values['train']:.4f}</td>
                    <td>{values['val']:.4f}</td>
                    <td>{values['test']:.4f}</td>
                </tr>
                """
                
            html += """
                </table>
                
                <h2>Resource Usage Summary</h2>
                <table>
                    <tr>
                        <th>Resource</th>
                        <th>Average Usage (%)</th>
                        <th>Peak Usage (%)</th>
                    </tr>
            """
            
            for resource, values in results["resource_usage"].items():
                avg_usage = np.mean(values)
                peak_usage = np.max(values)
                html += f"""
                <tr>
                    <td>{resource}</td>
                    <td>{avg_usage:.2f}</td>
                    <td>{peak_usage:.2f}</td>
                </tr>
                """
                
            html += """
                </table>
            </body>
            </html>
            """
            
            # Save report
            with open(file_path, 'w') as f:
                f.write(html)
                
            QMessageBox.information(self, "Success", "Report exported successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export report: {str(e)}") 