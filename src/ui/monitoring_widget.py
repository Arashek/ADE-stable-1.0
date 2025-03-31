from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QProgressBar, QFrame, QGridLayout)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from typing import Dict, Any
import numpy as np

class MetricWidget(QFrame):
    """Widget for displaying a single metric"""
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setup_ui(title)
        
    def setup_ui(self, title: str):
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Value
        self.value_label = QLabel("0.0")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(self.value_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        
    def update_value(self, value: float, max_value: float = 100.0):
        """Update the displayed value and progress bar"""
        self.value_label.setText(f"{value:.1f}")
        progress = int((value / max_value) * 100)
        self.progress_bar.setValue(progress)
        
        # Update color based on value
        if progress < 60:
            color = "#4CAF50"  # Green
        elif progress < 80:
            color = "#FFC107"  # Yellow
        else:
            color = "#F44336"  # Red
            
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                background-color: #f0f0f0;
            }}
            QProgressBar::chunk {{
                background-color: {color};
            }}
        """)

class PlotWidget(QFrame):
    """Widget for displaying metric plots"""
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setup_ui(title)
        
    def setup_ui(self, title: str):
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Plot
        self.figure, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        self.setLayout(layout)
        
    def update_plot(self, timestamps: list, values: list):
        """Update the plot with new data"""
        self.ax.clear()
        self.ax.plot(timestamps, values)
        self.ax.set_title(self.title)
        self.ax.grid(True)
        self.ax.tick_params(axis='x', rotation=45)
        self.canvas.draw()

class MonitoringWidget(QWidget):
    """Main widget for displaying system and training metrics"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # System metrics section
        system_group = QFrame()
        system_group.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        system_layout = QGridLayout()
        
        # CPU usage
        self.cpu_widget = MetricWidget("CPU Usage")
        system_layout.addWidget(self.cpu_widget, 0, 0)
        
        # Memory usage
        self.memory_widget = MetricWidget("Memory Usage")
        system_layout.addWidget(self.memory_widget, 0, 1)
        
        # GPU usage
        self.gpu_widget = MetricWidget("GPU Usage")
        system_layout.addWidget(self.gpu_widget, 0, 2)
        
        # Disk usage
        self.disk_widget = MetricWidget("Disk Usage")
        system_layout.addWidget(self.disk_widget, 1, 0)
        
        # Network I/O
        self.network_widget = MetricWidget("Network I/O")
        system_layout.addWidget(self.network_widget, 1, 1)
        
        system_group.setLayout(system_layout)
        layout.addWidget(system_group)
        
        # Training metrics section
        training_group = QFrame()
        training_group.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        training_layout = QGridLayout()
        
        # Loss
        self.loss_widget = MetricWidget("Training Loss")
        training_layout.addWidget(self.loss_widget, 0, 0)
        
        # Learning rate
        self.lr_widget = MetricWidget("Learning Rate")
        training_layout.addWidget(self.lr_widget, 0, 1)
        
        # Epoch
        self.epoch_widget = MetricWidget("Current Epoch")
        training_layout.addWidget(self.epoch_widget, 0, 2)
        
        # Step
        self.step_widget = MetricWidget("Current Step")
        training_layout.addWidget(self.step_widget, 1, 0)
        
        training_group.setLayout(training_layout)
        layout.addWidget(training_group)
        
        # Plots section
        plots_group = QFrame()
        plots_group.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        plots_layout = QGridLayout()
        
        # Loss plot
        self.loss_plot = PlotWidget("Loss Over Time")
        plots_layout.addWidget(self.loss_plot, 0, 0)
        
        # Learning rate plot
        self.lr_plot = PlotWidget("Learning Rate Over Time")
        plots_layout.addWidget(self.lr_plot, 0, 1)
        
        plots_group.setLayout(plots_layout)
        layout.addWidget(plots_group)
        
        self.setLayout(layout)
        
        # Setup update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_metrics)
        self.update_timer.start(1000)  # Update every second
        
    def update_metrics(self):
        """Update all metrics display"""
        # Get current metrics from monitoring manager
        # This should be connected to the actual MonitoringManager instance
        metrics = self.parent().monitoring_manager.get_resource_usage()
        training_metrics = self.parent().monitoring_manager.get_training_progress(None)
        
        # Update system metrics
        self.cpu_widget.update_value(metrics.get("cpu_usage", 0.0))
        self.memory_widget.update_value(metrics.get("memory_usage", 0.0))
        self.gpu_widget.update_value(metrics.get("gpu_usage", 0.0))
        self.disk_widget.update_value(metrics.get("disk_usage", 0.0))
        
        # Update training metrics
        self.loss_widget.update_value(training_metrics.get("loss", 0.0))
        self.lr_widget.update_value(training_metrics.get("learning_rate", 0.0))
        self.epoch_widget.update_value(training_metrics.get("epoch", 0))
        self.step_widget.update_value(training_metrics.get("step", 0))
        
        # Update plots
        # This should be connected to the actual metrics history
        timestamps = self.parent().monitoring_manager.timestamps
        loss_values = self.parent().monitoring_manager.metrics_history.get("loss", [])
        lr_values = self.parent().monitoring_manager.metrics_history.get("learning_rate", [])
        
        if timestamps and loss_values:
            self.loss_plot.update_plot(timestamps, loss_values)
        if timestamps and lr_values:
            self.lr_plot.update_plot(timestamps, lr_values) 