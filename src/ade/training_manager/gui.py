import sys
import asyncio
import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QTabWidget, QTextEdit, QSpinBox, QDoubleSpinBox,
    QCheckBox, QMessageBox, QFileDialog, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QIcon
from .process_manager import TrainingProcessManager
from .training_monitor import TrainingMonitor
from .notifications import NotificationManager, NotificationConfig

class TrainingWorker(QThread):
    """Worker thread for running training processes."""
    progress_updated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    training_completed = pyqtSignal(dict)

    def __init__(self, manager: TrainingProcessManager, model_name: str, hyperparameters: dict):
        super().__init__()
        self.manager = manager
        self.model_name = model_name
        self.hyperparameters = hyperparameters
        self.session_id = None

    def run(self):
        try:
            asyncio.run(self._run_training())
        except Exception as e:
            self.error_occurred.emit(str(e))

    async def _run_training(self):
        try:
            self.session_id = await self.manager.start_training(
                self.model_name, self.hyperparameters
            )
            
            # Monitor training progress
            while self.session_id in self.manager.active_processes:
                session = self.manager.websocket_server.get_session(self.session_id)
                if session:
                    self.progress_updated.emit({
                        "metrics": session.metrics,
                        "gpu_utilization": session.gpu_utilization,
                        "status": session.status
                    })
                await asyncio.sleep(0.1)

            # Training completed
            self.training_completed.emit({
                "session_id": self.session_id,
                "metrics": session.metrics if session else {}
            })

        except Exception as e:
            self.error_occurred.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ADE Training Manager")
        self.setMinimumSize(1200, 800)
        
        # Initialize managers
        self.process_manager = TrainingProcessManager()
        self.monitor = TrainingMonitor()
        self.notification_manager = NotificationManager()
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create tabs
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Add tabs
        tabs.addTab(self._create_training_tab(), "Training")
        tabs.addTab(self._create_monitoring_tab(), "Monitoring")
        tabs.addTab(self._create_settings_tab(), "Settings")
        
        # Initialize managers
        self._init_managers()
        
        # Setup update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_metrics)
        self.update_timer.start(1000)  # Update every second

    def _init_managers(self):
        """Initialize the training managers."""
        try:
            asyncio.run(self.process_manager.start())
            asyncio.run(self.monitor.connect())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to initialize managers: {str(e)}")

    def _create_training_tab(self) -> QWidget:
        """Create the training configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Model selection
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["Local Model", "Cloud Model", "ADE Platform Model"])
        model_layout.addWidget(self.model_combo)
        layout.addLayout(model_layout)
        
        # Hyperparameters
        params_layout = QVBoxLayout()
        
        # Learning rate
        lr_layout = QHBoxLayout()
        lr_layout.addWidget(QLabel("Learning Rate:"))
        self.lr_spin = QDoubleSpinBox()
        self.lr_spin.setRange(0.00001, 0.1)
        self.lr_spin.setValue(0.001)
        self.lr_spin.setSingleStep(0.0001)
        lr_layout.addWidget(self.lr_spin)
        params_layout.addLayout(lr_layout)
        
        # Batch size
        batch_layout = QHBoxLayout()
        batch_layout.addWidget(QLabel("Batch Size:"))
        self.batch_spin = QSpinBox()
        self.batch_spin.setRange(1, 256)
        self.batch_spin.setValue(32)
        batch_layout.addWidget(self.batch_spin)
        params_layout.addLayout(batch_layout)
        
        # Number of epochs
        epochs_layout = QHBoxLayout()
        epochs_layout.addWidget(QLabel("Epochs:"))
        self.epochs_spin = QSpinBox()
        self.epochs_spin.setRange(1, 1000)
        self.epochs_spin.setValue(10)
        epochs_layout.addWidget(self.epochs_spin)
        params_layout.addLayout(epochs_layout)
        
        layout.addLayout(params_layout)
        
        # Dataset selection
        dataset_layout = QHBoxLayout()
        dataset_layout.addWidget(QLabel("Dataset:"))
        self.dataset_path = QLineEdit()
        dataset_layout.addWidget(self.dataset_path)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._browse_dataset)
        dataset_layout.addWidget(browse_btn)
        layout.addLayout(dataset_layout)
        
        # Training controls
        controls_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Training")
        self.start_btn.clicked.connect(self._start_training)
        controls_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self._stop_training)
        self.stop_btn.setEnabled(False)
        controls_layout.addWidget(self.stop_btn)
        
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self._pause_training)
        self.pause_btn.setEnabled(False)
        controls_layout.addWidget(self.pause_btn)
        
        layout.addLayout(controls_layout)
        
        return tab

    def _create_monitoring_tab(self) -> QWidget:
        """Create the monitoring tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Metrics table
        self.metrics_table = QTableWidget()
        self.metrics_table.setColumnCount(4)
        self.metrics_table.setHorizontalHeaderLabels(["Metric", "Value", "GPU Usage", "Status"])
        layout.addWidget(self.metrics_table)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        layout.addWidget(self.log_display)
        
        return tab

    def _create_settings_tab(self) -> QWidget:
        """Create the settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # AWS Settings
        aws_group = QWidget()
        aws_layout = QVBoxLayout(aws_group)
        
        # Region
        region_layout = QHBoxLayout()
        region_layout.addWidget(QLabel("AWS Region:"))
        self.aws_region = QLineEdit()
        region_layout.addLayout(region_layout)
        aws_layout.addLayout(region_layout)
        
        # Access Key
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("Access Key:"))
        self.aws_key = QLineEdit()
        key_layout.addLayout(key_layout)
        aws_layout.addLayout(key_layout)
        
        # Secret Key
        secret_layout = QHBoxLayout()
        secret_layout.addWidget(QLabel("Secret Key:"))
        self.aws_secret = QLineEdit()
        self.aws_secret.setEchoMode(QLineEdit.EchoMode.Password)
        secret_layout.addLayout(secret_layout)
        aws_layout.addLayout(secret_layout)
        
        layout.addWidget(aws_group)
        
        # Notification Settings
        notif_group = QWidget()
        notif_layout = QVBoxLayout(notif_group)
        
        # Email notifications
        self.email_notif = QCheckBox("Enable Email Notifications")
        notif_layout.addWidget(self.email_notif)
        
        # Email settings
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("Email:"))
        self.email_address = QLineEdit()
        email_layout.addLayout(email_layout)
        notif_layout.addLayout(email_layout)
        
        layout.addWidget(notif_group)
        
        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self._save_settings)
        layout.addWidget(save_btn)
        
        return tab

    def _browse_dataset(self):
        """Open file dialog to select dataset."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Dataset", "", "JSON Files (*.json);;All Files (*.*)"
        )
        if file_path:
            self.dataset_path.setText(file_path)

    def _start_training(self):
        """Start a new training process."""
        try:
            # Get hyperparameters
            hyperparameters = {
                "learning_rate": self.lr_spin.value(),
                "batch_size": self.batch_spin.value(),
                "num_epochs": self.epochs_spin.value()
            }
            
            # Create and start worker
            self.worker = TrainingWorker(
                self.process_manager,
                self.model_combo.currentText(),
                hyperparameters
            )
            
            # Connect signals
            self.worker.progress_updated.connect(self._update_progress)
            self.worker.error_occurred.connect(self._handle_error)
            self.worker.training_completed.connect(self._handle_completion)
            
            # Start worker
            self.worker.start()
            
            # Update UI
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.pause_btn.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start training: {str(e)}")

    def _stop_training(self):
        """Stop the current training process."""
        try:
            if hasattr(self, 'worker') and self.worker.session_id:
                asyncio.run(self.process_manager.stop_training(self.worker.session_id))
                self.worker.terminate()
                self.worker.wait()
                
                # Update UI
                self.start_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                self.pause_btn.setEnabled(False)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to stop training: {str(e)}")

    def _pause_training(self):
        """Pause/resume the current training process."""
        try:
            if hasattr(self, 'worker') and self.worker.session_id:
                session = self.process_manager.websocket_server.get_session(self.worker.session_id)
                if session.status == "training":
                    asyncio.run(self.process_manager.pause_training(self.worker.session_id))
                    self.pause_btn.setText("Resume")
                else:
                    asyncio.run(self.process_manager.resume_training(self.worker.session_id))
                    self.pause_btn.setText("Pause")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to pause/resume training: {str(e)}")

    def _update_progress(self, data: dict):
        """Update the progress display."""
        metrics = data.get("metrics", {})
        gpu_util = data.get("gpu_utilization", {})
        status = data.get("status", "Unknown")
        
        # Update metrics table
        self.metrics_table.setRowCount(len(metrics))
        for i, (metric, value) in enumerate(metrics.items()):
            self.metrics_table.setItem(i, 0, QTableWidgetItem(metric))
            self.metrics_table.setItem(i, 1, QTableWidgetItem(str(value)))
            self.metrics_table.setItem(i, 2, QTableWidgetItem(str(gpu_util)))
            self.metrics_table.setItem(i, 3, QTableWidgetItem(status))
        
        # Update progress bar
        if "epoch" in metrics and "num_epochs" in metrics:
            progress = (metrics["epoch"] / metrics["num_epochs"]) * 100
            self.progress_bar.setValue(int(progress))

    def _handle_error(self, error: str):
        """Handle training errors."""
        QMessageBox.critical(self, "Error", f"Training error: {error}")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)

    def _handle_completion(self, data: dict):
        """Handle training completion."""
        QMessageBox.information(
            self,
            "Training Complete",
            f"Training completed successfully!\nFinal metrics: {data.get('metrics', {})}"
        )
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)

    def _save_settings(self):
        """Save application settings."""
        try:
            # Save AWS settings
            aws_config = {
                "region": self.aws_region.text(),
                "access_key": self.aws_key.text(),
                "secret_key": self.aws_secret.text()
            }
            
            # Save notification settings
            notif_config = {
                "email_enabled": self.email_notif.isChecked(),
                "email_recipients": [self.email_address.text()]
            }
            
            # Save to config files
            config_dir = Path("config")
            config_dir.mkdir(exist_ok=True)
            
            with open(config_dir / "aws_config.json", "w") as f:
                json.dump(aws_config, f)
            
            with open(config_dir / "notification_config.json", "w") as f:
                json.dump(notif_config, f)
            
            QMessageBox.information(self, "Success", "Settings saved successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")

    def _update_metrics(self):
        """Update metrics display periodically."""
        if hasattr(self, 'worker') and self.worker.session_id:
            session = self.process_manager.websocket_server.get_session(self.worker.session_id)
            if session:
                self._update_progress({
                    "metrics": session.metrics,
                    "gpu_utilization": session.gpu_utilization,
                    "status": session.status
                })

    def closeEvent(self, event):
        """Handle application closure."""
        try:
            if hasattr(self, 'worker'):
                self._stop_training()
            asyncio.run(self.process_manager.close())
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 