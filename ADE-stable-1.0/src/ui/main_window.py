from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTabWidget, QToolBar, QStatusBar, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QIcon
import logging
from pathlib import Path

from .monitoring_widget import MonitoringWidget
from ..core.monitoring_manager import MonitoringManager
from ..core.model_config import ModelConfig
from ..core.dataset_manager import DatasetManager
from ..core.model_trainer import ModelTrainer

class MainWindow(QMainWindow):
    """Main window of the training manager application"""
    
    def __init__(self):
        super().__init__()
        self.setup_logging()
        self.setup_managers()
        self.setup_ui()
        
    def setup_logging(self):
        """Setup logging configuration"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        fh = logging.FileHandler(log_dir / "training_manager.log")
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
        
    def setup_managers(self):
        """Initialize all manager instances"""
        try:
            self.monitoring_manager = MonitoringManager()
            self.dataset_manager = DatasetManager()
            self.model_trainer = ModelTrainer()
            self.logger.info("Successfully initialized all managers")
        except Exception as e:
            self.logger.error(f"Error initializing managers: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to initialize managers: {str(e)}")
            
    def setup_ui(self):
        """Setup the main window UI"""
        self.setWindowTitle("Training Manager")
        self.setMinimumSize(1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        layout = QVBoxLayout(central_widget)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Add tabs
        self.setup_tabs()
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
        # Setup update timer for status bar
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  # Update every second
        
    def create_toolbar(self):
        """Create the main toolbar"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # New project action
        new_action = QAction("New Project", self)
        new_action.triggered.connect(self.new_project)
        toolbar.addAction(new_action)
        
        # Open project action
        open_action = QAction("Open Project", self)
        open_action.triggered.connect(self.open_project)
        toolbar.addAction(open_action)
        
        # Save project action
        save_action = QAction("Save Project", self)
        save_action.triggered.connect(self.save_project)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # Start training action
        train_action = QAction("Start Training", self)
        train_action.triggered.connect(self.start_training)
        toolbar.addAction(train_action)
        
        # Stop training action
        stop_action = QAction("Stop Training", self)
        stop_action.triggered.connect(self.stop_training)
        toolbar.addAction(stop_action)
        
        toolbar.addSeparator()
        
        # Settings action
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        toolbar.addAction(settings_action)
        
    def setup_tabs(self):
        """Setup all tabs in the main window"""
        # Monitoring tab
        self.monitoring_widget = MonitoringWidget(self)
        self.tab_widget.addTab(self.monitoring_widget, "Monitoring")
        
        # Dataset tab
        self.dataset_widget = QWidget()  # TODO: Create DatasetWidget
        self.tab_widget.addTab(self.dataset_widget, "Datasets")
        
        # Model tab
        self.model_widget = QWidget()  # TODO: Create ModelWidget
        self.tab_widget.addTab(self.model_widget, "Model")
        
        # Training tab
        self.training_widget = QWidget()  # TODO: Create TrainingWidget
        self.tab_widget.addTab(self.training_widget, "Training")
        
        # Results tab
        self.results_widget = QWidget()  # TODO: Create ResultsWidget
        self.tab_widget.addTab(self.results_widget, "Results")
        
    def update_status(self):
        """Update the status bar with current information"""
        try:
            # Get current metrics
            metrics = self.monitoring_manager.get_resource_usage()
            
            # Format status message
            status = f"CPU: {metrics.get('cpu_usage', 0.0):.1f}% | "
            status += f"Memory: {metrics.get('memory_usage', 0.0):.1f}% | "
            status += f"GPU: {metrics.get('gpu_usage', 0.0):.1f}% | "
            status += f"Disk: {metrics.get('disk_usage', 0.0):.1f}%"
            
            self.statusBar.showMessage(status)
            
        except Exception as e:
            self.logger.error(f"Error updating status: {str(e)}")
            
    def new_project(self):
        """Create a new project"""
        # TODO: Implement new project creation
        pass
        
    def open_project(self):
        """Open an existing project"""
        # TODO: Implement project opening
        pass
        
    def save_project(self):
        """Save the current project"""
        # TODO: Implement project saving
        pass
        
    def start_training(self):
        """Start model training"""
        # TODO: Implement training start
        pass
        
    def stop_training(self):
        """Stop model training"""
        # TODO: Implement training stop
        pass
        
    def show_settings(self):
        """Show settings dialog"""
        # TODO: Implement settings dialog
        pass 