from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QTabWidget, QTextEdit, QSpinBox, QDoubleSpinBox,
    QCheckBox, QMessageBox, QFileDialog, QProgressBar,
    QGroupBox, QGridLayout, QSplitter, QFrame, QScrollArea,
    QToolButton, QMenu, QStatusBar, QSystemTrayIcon, QMenuBar
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor, QPainter, QPen
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from datetime import datetime
import psutil
import GPUtil
from typing import Dict, List, Optional

class ResourceMonitor(QWidget):
    """Widget for monitoring system resources."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_metrics)
        self.update_timer.start(1000)  # Update every second
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # CPU Usage
        cpu_group = QGroupBox("CPU Usage")
        cpu_layout = QVBoxLayout()
        self.cpu_progress = QProgressBar()
        self.cpu_label = QLabel("0%")
        cpu_layout.addWidget(self.cpu_progress)
        cpu_layout.addWidget(self.cpu_label)
        cpu_group.setLayout(cpu_layout)
        layout.addWidget(cpu_group)
        
        # Memory Usage
        memory_group = QGroupBox("Memory Usage")
        memory_layout = QVBoxLayout()
        self.memory_progress = QProgressBar()
        self.memory_label = QLabel("0%")
        memory_layout.addWidget(self.memory_progress)
        memory_layout.addWidget(self.memory_label)
        memory_group.setLayout(memory_layout)
        layout.addWidget(memory_group)
        
        # GPU Usage
        gpu_group = QGroupBox("GPU Usage")
        gpu_layout = QVBoxLayout()
        self.gpu_progress = QProgressBar()
        self.gpu_label = QLabel("0%")
        gpu_layout.addWidget(self.gpu_progress)
        gpu_layout.addWidget(self.gpu_label)
        gpu_group.setLayout(gpu_layout)
        layout.addWidget(gpu_group)
    
    def update_metrics(self):
        # CPU Usage
        cpu_percent = psutil.cpu_percent()
        self.cpu_progress.setValue(int(cpu_percent))
        self.cpu_label.setText(f"{cpu_percent}%")
        
        # Memory Usage
        memory = psutil.virtual_memory()
        self.memory_progress.setValue(int(memory.percent))
        self.memory_label.setText(f"{memory.percent}% ({memory.used / 1024 / 1024:.1f} MB)")
        
        # GPU Usage
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                self.gpu_progress.setValue(int(gpu.load * 100))
                self.gpu_label.setText(f"{gpu.load * 100:.1f}% ({gpu.memoryUsed}MB)")
            else:
                self.gpu_progress.setValue(0)
                self.gpu_label.setText("No GPU detected")
        except Exception as e:
            self.gpu_progress.setValue(0)
            self.gpu_label.setText("GPU monitoring error")

class MetricsPlot(QWidget):
    """Widget for plotting training metrics."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.metrics_history = {
            "loss": [],
            "accuracy": [],
            "learning_rate": []
        }
        self.timestamps = []
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create matplotlib figure
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Metrics selection
        metrics_layout = QHBoxLayout()
        self.metrics_combo = QComboBox()
        self.metrics_combo.addItems(["loss", "accuracy", "learning_rate"])
        self.metrics_combo.currentTextChanged.connect(self.update_plot)
        metrics_layout.addWidget(QLabel("Metric:"))
        metrics_layout.addWidget(self.metrics_combo)
        layout.addLayout(metrics_layout)
    
    def update_metrics(self, metrics: Dict[str, float]):
        timestamp = datetime.now()
        self.timestamps.append(timestamp)
        
        for metric, value in metrics.items():
            if metric in self.metrics_history:
                self.metrics_history[metric].append(value)
        
        self.update_plot()
    
    def update_plot(self):
        self.ax.clear()
        metric = self.metrics_combo.currentText()
        
        if metric in self.metrics_history and self.metrics_history[metric]:
            self.ax.plot(self.timestamps, self.metrics_history[metric])
            self.ax.set_title(f"Training {metric.capitalize()}")
            self.ax.set_xlabel("Time")
            self.ax.set_ylabel(metric.capitalize())
            self.ax.grid(True)
        
        self.canvas.draw()

class CloudProviderWidget(QWidget):
    """Widget for cloud provider configuration."""
    
    def __init__(self, provider: str, parent=None):
        super().__init__(parent)
        self.provider = provider
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Provider-specific settings
        if self.provider == "aws":
            self.setup_aws_ui(layout)
        elif self.provider == "google":
            self.setup_google_ui(layout)
        elif self.provider == "azure":
            self.setup_azure_ui(layout)
        
        # Common settings
        common_group = QGroupBox("Common Settings")
        common_layout = QGridLayout()
        
        # Region selection
        common_layout.addWidget(QLabel("Region:"), 0, 0)
        self.region_combo = QComboBox()
        common_layout.addWidget(self.region_combo, 0, 1)
        
        # Instance type selection
        common_layout.addWidget(QLabel("Instance Type:"), 1, 0)
        self.instance_combo = QComboBox()
        common_layout.addWidget(self.instance_combo, 1, 1)
        
        # Storage configuration
        common_layout.addWidget(QLabel("Storage (GB):"), 2, 0)
        self.storage_spin = QSpinBox()
        self.storage_spin.setRange(10, 1000)
        self.storage_spin.setValue(100)
        common_layout.addWidget(self.storage_spin, 2, 1)
        
        common_group.setLayout(common_layout)
        layout.addWidget(common_group)
    
    def setup_aws_ui(self, layout):
        aws_group = QGroupBox("AWS Settings")
        aws_layout = QGridLayout()
        
        aws_layout.addWidget(QLabel("Access Key:"), 0, 0)
        self.access_key = QLineEdit()
        aws_layout.addWidget(self.access_key, 0, 1)
        
        aws_layout.addWidget(QLabel("Secret Key:"), 1, 0)
        self.secret_key = QLineEdit()
        self.secret_key.setEchoMode(QLineEdit.EchoMode.Password)
        aws_layout.addWidget(self.secret_key, 1, 1)
        
        aws_layout.addWidget(QLabel("S3 Bucket:"), 2, 0)
        self.s3_bucket = QLineEdit()
        aws_layout.addWidget(self.s3_bucket, 2, 1)
        
        aws_group.setLayout(aws_layout)
        layout.addWidget(aws_group)
    
    def setup_google_ui(self, layout):
        google_group = QGroupBox("Google Cloud Settings")
        google_layout = QGridLayout()
        
        google_layout.addWidget(QLabel("Project ID:"), 0, 0)
        self.project_id = QLineEdit()
        google_layout.addWidget(self.project_id, 0, 1)
        
        google_layout.addWidget(QLabel("Service Account:"), 1, 0)
        self.service_account = QLineEdit()
        google_layout.addWidget(self.service_account, 1, 1)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_service_account)
        google_layout.addWidget(browse_btn, 1, 2)
        
        google_group.setLayout(google_layout)
        layout.addWidget(google_group)
    
    def setup_azure_ui(self, layout):
        azure_group = QGroupBox("Azure Settings")
        azure_layout = QGridLayout()
        
        azure_layout.addWidget(QLabel("Subscription ID:"), 0, 0)
        self.subscription_id = QLineEdit()
        azure_layout.addWidget(self.subscription_id, 0, 1)
        
        azure_layout.addWidget(QLabel("Resource Group:"), 1, 0)
        self.resource_group = QLineEdit()
        azure_layout.addWidget(self.resource_group, 1, 1)
        
        azure_layout.addWidget(QLabel("Storage Account:"), 2, 0)
        self.storage_account = QLineEdit()
        azure_layout.addWidget(self.storage_account, 2, 1)
        
        azure_group.setLayout(azure_layout)
        layout.addWidget(azure_group)
    
    def browse_service_account(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Service Account File", "", "JSON Files (*.json)"
        )
        if file_path:
            self.service_account.setText(file_path)
    
    def get_settings(self) -> Dict:
        """Get the current settings for the cloud provider."""
        settings = {
            "region": self.region_combo.currentText(),
            "instance_type": self.instance_combo.currentText(),
            "storage_gb": self.storage_spin.value()
        }
        
        if self.provider == "aws":
            settings.update({
                "access_key": self.access_key.text(),
                "secret_key": self.secret_key.text(),
                "s3_bucket": self.s3_bucket.text()
            })
        elif self.provider == "google":
            settings.update({
                "project_id": self.project_id.text(),
                "service_account_path": self.service_account.text()
            })
        elif self.provider == "azure":
            settings.update({
                "subscription_id": self.subscription_id.text(),
                "resource_group": self.resource_group.text(),
                "storage_account": self.storage_account.text()
            })
        
        return settings

class NotificationWidget(QWidget):
    """Widget for managing notifications."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Email notifications
        email_group = QGroupBox("Email Notifications")
        email_layout = QGridLayout()
        
        email_layout.addWidget(QLabel("Enabled:"), 0, 0)
        self.email_enabled = QCheckBox()
        email_layout.addWidget(self.email_enabled, 0, 1)
        
        email_layout.addWidget(QLabel("SMTP Server:"), 1, 0)
        self.smtp_server = QLineEdit()
        email_layout.addWidget(self.smtp_server, 1, 1)
        
        email_layout.addWidget(QLabel("Port:"), 2, 0)
        self.smtp_port = QSpinBox()
        self.smtp_port.setRange(1, 65535)
        self.smtp_port.setValue(587)
        email_layout.addWidget(self.smtp_port, 2, 1)
        
        email_layout.addWidget(QLabel("Username:"), 3, 0)
        self.smtp_username = QLineEdit()
        email_layout.addWidget(self.smtp_username, 3, 1)
        
        email_layout.addWidget(QLabel("Password:"), 4, 0)
        self.smtp_password = QLineEdit()
        self.smtp_password.setEchoMode(QLineEdit.EchoMode.Password)
        email_layout.addWidget(self.smtp_password, 4, 1)
        
        email_layout.addWidget(QLabel("Recipients:"), 5, 0)
        self.recipients = QLineEdit()
        email_layout.addWidget(self.recipients, 5, 1)
        
        email_group.setLayout(email_layout)
        layout.addWidget(email_group)
        
        # Slack notifications
        slack_group = QGroupBox("Slack Notifications")
        slack_layout = QGridLayout()
        
        slack_layout.addWidget(QLabel("Enabled:"), 0, 0)
        self.slack_enabled = QCheckBox()
        slack_layout.addWidget(self.slack_enabled, 0, 1)
        
        slack_layout.addWidget(QLabel("Webhook URL:"), 1, 0)
        self.slack_webhook = QLineEdit()
        slack_layout.addWidget(self.slack_webhook, 1, 1)
        
        slack_layout.addWidget(QLabel("Channel:"), 2, 0)
        self.slack_channel = QLineEdit()
        slack_layout.addWidget(self.slack_channel, 2, 1)
        
        slack_group.setLayout(slack_layout)
        layout.addWidget(slack_group)
        
        # Notification events
        events_group = QGroupBox("Notification Events")
        events_layout = QVBoxLayout()
        
        self.event_checkboxes = {}
        events = [
            "Training Started",
            "Training Completed",
            "Training Failed",
            "Checkpoint Saved",
            "Milestone Reached",
            "Resource Warning"
        ]
        
        for event in events:
            checkbox = QCheckBox(event)
            checkbox.setChecked(True)
            self.event_checkboxes[event] = checkbox
            events_layout.addWidget(checkbox)
        
        events_group.setLayout(events_layout)
        layout.addWidget(events_group)
    
    def get_settings(self) -> Dict:
        """Get the current notification settings."""
        return {
            "email": {
                "enabled": self.email_enabled.isChecked(),
                "smtp_server": self.smtp_server.text(),
                "smtp_port": self.smtp_port.value(),
                "username": self.smtp_username.text(),
                "password": self.smtp_password.text(),
                "recipients": [r.strip() for r in self.recipients.text().split(",")]
            },
            "slack": {
                "enabled": self.slack_enabled.isChecked(),
                "webhook_url": self.slack_webhook.text(),
                "channel": self.slack_channel.text()
            },
            "events": {
                event: checkbox.isChecked()
                for event, checkbox in self.event_checkboxes.items()
            }
        } 