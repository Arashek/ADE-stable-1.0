import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame, QScrollArea,
    QSystemTrayIcon, QMenu, QMessageBox, QGroupBox, QGridLayout,
    QDoubleSpinBox, QSpinBox, QCheckBox, QLineEdit, QComboBox, QTextEdit
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor, QPixmap
from PyQt6.QtPrintSupport import QPrinter
import matplotlib.pyplot as plt
import numpy as np

class MockupGenerator:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.mockup_dir = Path("docs/mockups")
        self.mockup_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate all mockups
        self.generate_overview()
        self.generate_installation()
        self.generate_sidebar()
        self.generate_dashboard()
        self.generate_training_config()
        self.generate_dataset_management()
        self.generate_aws_config()
        self.generate_gcp_config()
        self.generate_monitoring()
        
        # Generate example plots
        self.generate_example_plots()
    
    def generate_overview(self):
        window = QMainWindow()
        window.setWindowTitle("ADE Training Manager - Overview")
        window.setMinimumSize(1200, 800)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("ADE Training Manager")
        header.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Features
        features = QGroupBox("Key Features")
        features_layout = QGridLayout()
        
        feature_items = [
            ("Code-Aware Training", "Advanced code understanding and analysis"),
            ("Cloud Integration", "Seamless cloud provider support"),
            ("Dataset Management", "Comprehensive dataset handling"),
            ("Real-time Monitoring", "Live training metrics and resources"),
            ("Model Selection", "Flexible model architecture options")
        ]
        
        for i, (title, desc) in enumerate(feature_items):
            features_layout.addWidget(QLabel(title), i, 0)
            features_layout.addWidget(QLabel(desc), i, 1)
        
        features.setLayout(features_layout)
        layout.addWidget(features)
        
        window.setCentralWidget(widget)
        self._capture_window(window, "overview")
    
    def generate_installation(self):
        window = QMainWindow()
        window.setWindowTitle("Installation Guide")
        window.setMinimumSize(800, 600)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Installation steps
        steps = QGroupBox("Installation Steps")
        steps_layout = QVBoxLayout()
        
        step_items = [
            "1. Download the latest release",
            "2. Run the installer",
            "3. Configure system requirements",
            "4. Set up cloud credentials",
            "5. Initialize the training environment"
        ]
        
        for step in step_items:
            steps_layout.addWidget(QLabel(step))
        
        steps.setLayout(steps_layout)
        layout.addWidget(steps)
        
        # System requirements
        requirements = QGroupBox("System Requirements")
        req_layout = QGridLayout()
        
        req_items = [
            ("CPU", "8+ cores"),
            ("RAM", "16GB+"),
            ("GPU", "NVIDIA GPU with 8GB+ VRAM"),
            ("Storage", "100GB+ SSD"),
            ("OS", "Windows 10/11, Linux, macOS")
        ]
        
        for i, (item, value) in enumerate(req_items):
            req_layout.addWidget(QLabel(item), i, 0)
            req_layout.addWidget(QLabel(value), i, 1)
        
        requirements.setLayout(req_layout)
        layout.addWidget(requirements)
        
        window.setCentralWidget(widget)
        self._capture_window(window, "installation")
    
    def generate_sidebar(self):
        window = QMainWindow()
        window.setWindowTitle("Navigation Sidebar")
        window.setMinimumSize(300, 800)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Logo
        logo = QLabel("ADE")
        logo.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)
        
        # Navigation buttons
        nav_items = [
            "Dashboard",
            "Training",
            "Datasets",
            "Cloud Providers",
            "Monitoring",
            "Settings"
        ]
        
        for item in nav_items:
            btn = QPushButton(item)
            btn.setMinimumHeight(40)
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # Status
        status = QGroupBox("System Status")
        status_layout = QVBoxLayout()
        status_layout.addWidget(QLabel("Ready"))
        status.setLayout(status_layout)
        layout.addWidget(status)
        
        window.setCentralWidget(widget)
        self._capture_window(window, "sidebar")
    
    def generate_dashboard(self):
        window = QMainWindow()
        window.setWindowTitle("Dashboard")
        window.setMinimumSize(1200, 800)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Quick stats
        stats = QGroupBox("Quick Statistics")
        stats_layout = QHBoxLayout()
        
        stat_items = [
            ("Active Jobs", "3"),
            ("Completed", "12"),
            ("Failed", "1"),
            ("Datasets", "5")
        ]
        
        for title, value in stat_items:
            stat_widget = QFrame()
            stat_layout = QVBoxLayout(stat_widget)
            stat_layout.addWidget(QLabel(title))
            stat_layout.addWidget(QLabel(value))
            stats_layout.addWidget(stat_widget)
        
        stats.setLayout(stats_layout)
        layout.addWidget(stats)
        
        # Resource monitor
        monitor = QGroupBox("Resource Monitor")
        monitor_layout = QGridLayout()
        
        resources = [
            ("CPU Usage", "45%"),
            ("Memory Usage", "60%"),
            ("GPU Usage", "75%"),
            ("Disk Usage", "40%")
        ]
        
        for i, (name, value) in enumerate(resources):
            monitor_layout.addWidget(QLabel(name), i, 0)
            monitor_layout.addWidget(QLabel(value), i, 1)
        
        monitor.setLayout(monitor_layout)
        layout.addWidget(monitor)
        
        window.setCentralWidget(widget)
        self._capture_window(window, "dashboard")
    
    def generate_training_config(self):
        window = QMainWindow()
        window.setWindowTitle("Training Configuration")
        window.setMinimumSize(1000, 800)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Model selection
        model = QGroupBox("Model Configuration")
        model_layout = QVBoxLayout()
        
        model_layout.addWidget(QLabel("Model Type:"))
        model_layout.addWidget(QComboBox())
        
        model_layout.addWidget(QLabel("Base Model:"))
        model_layout.addWidget(QComboBox())
        
        model.setLayout(model_layout)
        layout.addWidget(model)
        
        # Training parameters
        params = QGroupBox("Training Parameters")
        params_layout = QGridLayout()
        
        param_items = [
            ("Learning Rate", "0.001"),
            ("Batch Size", "32"),
            ("Epochs", "100"),
            ("Optimizer", "Adam")
        ]
        
        for i, (name, value) in enumerate(param_items):
            params_layout.addWidget(QLabel(name), i, 0)
            params_layout.addWidget(QLabel(value), i, 1)
        
        params.setLayout(params_layout)
        layout.addWidget(params)
        
        window.setCentralWidget(widget)
        self._capture_window(window, "training_config")
    
    def generate_dataset_management(self):
        window = QMainWindow()
        window.setWindowTitle("Dataset Management")
        window.setMinimumSize(1000, 800)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Dataset sources
        sources = QGroupBox("Dataset Sources")
        sources_layout = QVBoxLayout()
        
        source_items = [
            "GitHub Repository",
            "Local Directory",
            "Cloud Storage",
            "Public Dataset"
        ]
        
        for item in source_items:
            sources_layout.addWidget(QCheckBox(item))
        
        sources.setLayout(sources_layout)
        layout.addWidget(sources)
        
        # Dataset manipulation
        manipulation = QGroupBox("Dataset Manipulation")
        manipulation_layout = QVBoxLayout()
        
        manipulation_items = [
            "Data Cleaning",
            "Data Augmentation",
            "Synthetic Data Generation",
            "Quality Assessment"
        ]
        
        for item in manipulation_items:
            manipulation_layout.addWidget(QCheckBox(item))
        
        manipulation.setLayout(manipulation_layout)
        layout.addWidget(manipulation)
        
        window.setCentralWidget(widget)
        self._capture_window(window, "dataset_management")
    
    def generate_aws_config(self):
        window = QMainWindow()
        window.setWindowTitle("AWS Configuration")
        window.setMinimumSize(800, 600)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # AWS credentials
        creds = QGroupBox("AWS Credentials")
        creds_layout = QGridLayout()
        
        cred_items = [
            ("Access Key", "********"),
            ("Secret Key", "********"),
            ("Region", "us-east-1")
        ]
        
        for i, (name, value) in enumerate(cred_items):
            creds_layout.addWidget(QLabel(name), i, 0)
            creds_layout.addWidget(QLabel(value), i, 1)
        
        creds.setLayout(creds_layout)
        layout.addWidget(creds)
        
        # S3 configuration
        s3 = QGroupBox("S3 Configuration")
        s3_layout = QGridLayout()
        
        s3_items = [
            ("Bucket Name", "ade-training-data"),
            ("Prefix", "datasets/"),
            ("Region", "us-east-1")
        ]
        
        for i, (name, value) in enumerate(s3_items):
            s3_layout.addWidget(QLabel(name), i, 0)
            s3_layout.addWidget(QLabel(value), i, 1)
        
        s3.setLayout(s3_layout)
        layout.addWidget(s3)
        
        window.setCentralWidget(widget)
        self._capture_window(window, "aws_config")
    
    def generate_gcp_config(self):
        window = QMainWindow()
        window.setWindowTitle("Google Cloud Configuration")
        window.setMinimumSize(800, 600)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # GCP credentials
        creds = QGroupBox("GCP Credentials")
        creds_layout = QGridLayout()
        
        cred_items = [
            ("Project ID", "ade-training"),
            ("Service Account", "ade-service@ade-training.iam.gserviceaccount.com"),
            ("Region", "us-central1")
        ]
        
        for i, (name, value) in enumerate(cred_items):
            creds_layout.addWidget(QLabel(name), i, 0)
            creds_layout.addWidget(QLabel(value), i, 1)
        
        creds.setLayout(creds_layout)
        layout.addWidget(creds)
        
        # Storage configuration
        storage = QGroupBox("Storage Configuration")
        storage_layout = QGridLayout()
        
        storage_items = [
            ("Bucket Name", "ade-training-data"),
            ("Prefix", "datasets/"),
            ("Region", "us-central1")
        ]
        
        for i, (name, value) in enumerate(storage_items):
            storage_layout.addWidget(QLabel(name), i, 0)
            storage_layout.addWidget(QLabel(value), i, 1)
        
        storage.setLayout(storage_layout)
        layout.addWidget(storage)
        
        window.setCentralWidget(widget)
        self._capture_window(window, "gcp_config")
    
    def generate_monitoring(self):
        window = QMainWindow()
        window.setWindowTitle("Training Monitoring")
        window.setMinimumSize(1200, 800)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Training metrics
        metrics = QGroupBox("Training Metrics")
        metrics_layout = QVBoxLayout()
        
        # Example plot
        plt.figure(figsize=(10, 4))
        x = np.linspace(0, 100, 100)
        y = np.sin(x/10) + np.random.normal(0, 0.1, 100)
        plt.plot(x, y)
        plt.title('Training Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.savefig(str(self.mockup_dir / "training_metrics.png"))
        plt.close()
        
        metrics_layout.addWidget(QLabel("Training Progress"))
        metrics.setLayout(metrics_layout)
        layout.addWidget(metrics)
        
        # Resource usage
        resources = QGroupBox("Resource Usage")
        resources_layout = QGridLayout()
        
        resource_items = [
            ("CPU Usage", "45%"),
            ("Memory Usage", "60%"),
            ("GPU Usage", "75%"),
            ("Disk Usage", "40%")
        ]
        
        for i, (name, value) in enumerate(resource_items):
            resources_layout.addWidget(QLabel(name), i, 0)
            resources_layout.addWidget(QLabel(value), i, 1)
        
        resources.setLayout(resources_layout)
        layout.addWidget(resources)
        
        window.setCentralWidget(widget)
        self._capture_window(window, "monitoring")
    
    def generate_example_plots(self):
        # Generate example training plots
        plt.figure(figsize=(10, 6))
        x = np.linspace(0, 100, 100)
        y1 = np.sin(x/10) + np.random.normal(0, 0.1, 100)
        y2 = np.cos(x/10) + np.random.normal(0, 0.1, 100)
        plt.plot(x, y1, label="Training Loss")
        plt.plot(x, y2, label="Validation Loss")
        plt.title("Training Progress")
        plt.xlabel("Epoch")
        plt.ylabel("Loss")
        plt.legend()
        plt.savefig(str(self.mockup_dir / "training_progress.png"))
        plt.close()
        
        # Generate example resource usage plot
        plt.figure(figsize=(10, 6))
        x = np.linspace(0, 60, 60)
        y = np.random.normal(50, 10, 60)
        plt.plot(x, y)
        plt.title("Resource Usage Over Time")
        plt.xlabel("Time (minutes)")
        plt.ylabel("Usage (%)")
        plt.savefig(str(self.mockup_dir / "resource_usage.png"))
        plt.close()
    
    def _capture_window(self, window: QMainWindow, name: str):
        window.show()
        window.raise_()
        window.activateWindow()
        
        # Wait for window to be fully rendered
        self.app.processEvents()
        
        # Capture window
        pixmap = window.grab()
        pixmap.save(str(self.mockup_dir / f"{name}.png"))

if __name__ == "__main__":
    generator = MockupGenerator()
    print("Mockup generation completed!") 