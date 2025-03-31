import sys
import os
import asyncio
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame, QScrollArea,
    QSystemTrayIcon, QMenu, QMessageBox, QGroupBox, QGridLayout,
    QDoubleSpinBox, QSpinBox, QCheckBox, QLineEdit, QComboBox, QTextEdit, QDialog
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor
from .ui_components import (
    ResourceMonitor, MetricsPlot, CloudProviderWidget,
    NotificationWidget
)
from .process_manager import TrainingProcessManager
from .cloud_manager import CloudManager
from .notifications import NotificationManager
from .model_trainer import ModelTrainer
import json

class DashboardWindow(QMainWindow):
    def __init__(self, trainer: ModelTrainer = None):
        super().__init__()
        self.setWindowTitle("ADE Model Training Manager")
        self.setMinimumSize(1400, 800)
        
        # Initialize managers
        self.process_manager = TrainingProcessManager()
        self.cloud_manager = CloudManager()
        self.notification_manager = NotificationManager()
        self.model_trainer = trainer
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Create sidebar
        sidebar = self._create_sidebar()
        layout.addWidget(sidebar)
        
        # Create main content area
        self.content = QStackedWidget()
        layout.addWidget(self.content)
        
        # Add pages
        self._add_pages()
        
        # Create system tray icon
        self._create_tray_icon()
        
        # Set style
        self._apply_style()
    
    def _create_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setFrameShape(QFrame.Shape.StyledPanel)
        sidebar.setMaximumWidth(250)
        layout = QVBoxLayout(sidebar)
        
        # Logo and title
        title = QLabel("ADE Training Manager")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Navigation buttons
        nav_buttons = [
            ("Dashboard", self._show_dashboard),
            ("Training", self._show_training),
            ("Datasets", self._show_datasets),
            ("Cloud Providers", self._show_cloud_providers),
            ("Monitoring", self._show_monitoring),
            ("Settings", self._show_settings)
        ]
        
        for text, callback in nav_buttons:
            btn = QPushButton(text)
            btn.setMinimumHeight(40)
            btn.clicked.connect(callback)
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # Status section
        status_frame = QFrame()
        status_frame.setFrameShape(QFrame.Shape.StyledPanel)
        status_layout = QVBoxLayout(status_frame)
        
        status_label = QLabel("System Status")
        status_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        status_layout.addWidget(status_label)
        
        self.status_text = QLabel("Ready")
        status_layout.addWidget(self.status_text)
        
        layout.addWidget(status_frame)
        
        return sidebar
    
    def _add_pages(self):
        # Dashboard page
        dashboard = QWidget()
        dashboard_layout = QVBoxLayout(dashboard)
        
        # ADE Model Overview
        model_overview = QFrame()
        model_overview.setFrameShape(QFrame.Shape.StyledPanel)
        model_layout = QVBoxLayout(model_overview)
        
        model_title = QLabel("ADE Model Overview")
        model_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        model_layout.addWidget(model_title)
        
        # Model capabilities
        capabilities_group = QGroupBox("Model Capabilities")
        capabilities_layout = QGridLayout()
        
        capabilities = [
            ("Code Awareness", "Understanding code structure and semantics"),
            ("Planning", "Generating execution plans"),
            ("Execution", "Code execution and debugging"),
            ("Code Generation", "Generating code from specifications")
        ]
        
        for i, (capability, description) in enumerate(capabilities):
            capabilities_layout.addWidget(QLabel(capability), i, 0)
            capabilities_layout.addWidget(QLabel(description), i, 1)
        
        capabilities_group.setLayout(capabilities_layout)
        model_layout.addWidget(capabilities_group)
        
        # Training rules
        rules_group = QGroupBox("Training Rules")
        rules_layout = QVBoxLayout()
        
        rules = [
            "1. Code Structure Understanding",
            "2. Semantic Analysis",
            "3. Execution Flow Prediction",
            "4. Error Detection and Correction",
            "5. Code Generation Quality",
            "6. Performance Optimization"
        ]
        
        for rule in rules:
            rules_layout.addWidget(QLabel(rule))
        
        rules_group.setLayout(rules_layout)
        model_layout.addWidget(rules_group)
        
        dashboard_layout.addWidget(model_overview)
        
        # Quick stats
        stats_layout = QHBoxLayout()
        stats = [
            ("Active Training Jobs", "0"),
            ("Completed Training Jobs", "0"),
            ("Failed Training Jobs", "0"),
            ("Total Datasets", "0"),
            ("Model Version", "1.0.0")
        ]
        
        for title, value in stats:
            stat_widget = QFrame()
            stat_widget.setFrameShape(QFrame.Shape.StyledPanel)
            stat_layout = QVBoxLayout(stat_widget)
            
            stat_title = QLabel(title)
            stat_title.setFont(QFont("Arial", 10))
            stat_layout.addWidget(stat_title)
            
            stat_value = QLabel(value)
            stat_value.setFont(QFont("Arial", 20, QFont.Weight.Bold))
            stat_layout.addWidget(stat_value)
            
            stats_layout.addWidget(stat_widget)
        
        dashboard_layout.addLayout(stats_layout)
        
        # Resource monitor
        self.resource_monitor = ResourceMonitor()
        dashboard_layout.addWidget(self.resource_monitor)
        
        # Recent activity
        activity_frame = QFrame()
        activity_frame.setFrameShape(QFrame.Shape.StyledPanel)
        activity_layout = QVBoxLayout(activity_frame)
        
        activity_title = QLabel("Recent Activity")
        activity_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        activity_layout.addWidget(activity_title)
        
        self.activity_list = QTextEdit()
        self.activity_list.setReadOnly(True)
        activity_layout.addWidget(self.activity_list)
        
        # Add some example activities
        activities = [
            "Initialized ADE Model Training Environment",
            "Loaded Code-Aware Training Dataset",
            "Configured Training Rules and Parameters",
            "Started Model Training Process",
            "Monitoring Training Progress"
        ]
        
        for activity in activities:
            self.activity_list.append(f"• {activity}")
        
        dashboard_layout.addWidget(activity_frame)
        
        self.content.addWidget(dashboard)
        
        # Add other pages
        self.content.addWidget(self._create_training_page())
        self.content.addWidget(self._create_datasets_page())
        self.content.addWidget(self._create_cloud_providers_page())
        self.content.addWidget(self._create_monitoring_page())
        self.content.addWidget(self._create_settings_page())
    
    def _create_training_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Split into left and right panels
        split_layout = QHBoxLayout()
        
        # Left panel - Model configuration
        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.Shape.StyledPanel)
        left_layout = QVBoxLayout(left_panel)
        
        # Model components
        components_group = QGroupBox("Model Components")
        components_layout = QVBoxLayout()
        
        # Component selection
        component_type = QComboBox()
        component_type.addItems([
            "Code Understanding (CodeLlama-34B)",
            "Tool Use (Claude 3 Sonnet)",
            "Planning (Claude 3 Sonnet)",
            "Code Generation (StarCoder2-33B)"
        ])
        components_layout.addWidget(QLabel("Component:"))
        components_layout.addWidget(component_type)
        
        # Training controls
        controls_layout = QHBoxLayout()
        train_btn = QPushButton("Train Component")
        train_btn.clicked.connect(lambda: self._train_component(component_type.currentText()))
        controls_layout.addWidget(train_btn)
        
        eval_btn = QPushButton("Evaluate")
        eval_btn.clicked.connect(lambda: self._evaluate_component(component_type.currentText()))
        controls_layout.addWidget(eval_btn)
        
        components_layout.addLayout(controls_layout)
        
        # Training progress
        progress_group = QGroupBox("Training Progress")
        progress_layout = QVBoxLayout()
        
        self.progress_text = QTextEdit()
        self.progress_text.setReadOnly(True)
        progress_layout.addWidget(self.progress_text)
        
        progress_group.setLayout(progress_layout)
        components_layout.addWidget(progress_group)
        
        components_group.setLayout(components_layout)
        left_layout.addWidget(components_group)
        
        # Training parameters
        params_group = QGroupBox("Training Parameters")
        params_layout = QGridLayout()
        
        params = [
            ("Batch Size", QSpinBox(), "4"),
            ("Learning Rate", QDoubleSpinBox(), "2e-5"),
            ("Epochs", QSpinBox(), "3"),
            ("Max Length", QSpinBox(), "2048")
        ]
        
        for i, (label, widget, default) in enumerate(params):
            params_layout.addWidget(QLabel(label), i, 0)
            if isinstance(widget, QSpinBox):
                widget.setValue(int(default))
            elif isinstance(widget, QDoubleSpinBox):
                widget.setValue(float(default))
            params_layout.addWidget(widget, i, 1)
        
        params_group.setLayout(params_layout)
        left_layout.addWidget(params_group)
        
        split_layout.addWidget(left_panel)
        
        # Right panel - Metrics and monitoring
        right_panel = QFrame()
        right_panel.setFrameShape(QFrame.Shape.StyledPanel)
        right_layout = QVBoxLayout(right_panel)
        
        # Metrics plot
        metrics_plot = MetricsPlot()
        right_layout.addWidget(metrics_plot)
        
        # Resource monitor
        resource_monitor = ResourceMonitor()
        right_layout.addWidget(resource_monitor)
        
        split_layout.addWidget(right_panel)
        
        layout.addLayout(split_layout)
        
        return page
    
    def _create_datasets_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Dataset management controls
        controls_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Dataset")
        add_btn.clicked.connect(self._add_dataset)
        controls_layout.addWidget(add_btn)
        
        import_btn = QPushButton("Import from Cloud")
        import_btn.clicked.connect(self._import_dataset)
        controls_layout.addWidget(import_btn)
        
        github_btn = QPushButton("Import from GitHub")
        github_btn.clicked.connect(self._import_from_github)
        controls_layout.addWidget(github_btn)
        
        layout.addLayout(controls_layout)
        
        # Dataset source selection
        source_group = QGroupBox("Dataset Sources")
        source_layout = QVBoxLayout()
        
        # Source type selection
        source_type_layout = QHBoxLayout()
        source_type_layout.addWidget(QLabel("Source Type:"))
        self.source_type_combo = QComboBox()
        self.source_type_combo.addItems([
            "GitHub Repository",
            "Local Directory",
            "Cloud Storage",
            "Public Dataset",
            "Custom Source"
        ])
        self.source_type_combo.currentTextChanged.connect(self._change_source_type)
        source_type_layout.addWidget(self.source_type_combo)
        source_layout.addLayout(source_type_layout)
        
        # Source configuration stack
        self.source_config_stack = QStackedWidget()
        
        # GitHub configuration
        github_config = QWidget()
        github_layout = QVBoxLayout(github_config)
        
        github_url_layout = QHBoxLayout()
        github_url_layout.addWidget(QLabel("Repository URL:"))
        self.github_url = QLineEdit()
        github_url_layout.addWidget(self.github_url)
        github_layout.addLayout(github_url_layout)
        
        github_branch_layout = QHBoxLayout()
        github_branch_layout.addWidget(QLabel("Branch:"))
        self.github_branch = QComboBox()
        self.github_branch.addItems(["main", "master", "develop"])
        github_branch_layout.addWidget(self.github_branch)
        github_layout.addLayout(github_branch_layout)
        
        github_pattern_layout = QHBoxLayout()
        github_pattern_layout.addWidget(QLabel("File Patterns:"))
        self.github_pattern = QLineEdit("*.py,*.js,*.java,*.cpp")
        github_pattern_layout.addWidget(self.github_pattern)
        github_layout.addLayout(github_pattern_layout)
        
        github_config.setLayout(github_layout)
        self.source_config_stack.addWidget(github_config)
        
        # Local directory configuration
        local_config = QWidget()
        local_layout = QVBoxLayout(local_config)
        
        local_path_layout = QHBoxLayout()
        local_path_layout.addWidget(QLabel("Directory Path:"))
        self.local_path = QLineEdit()
        local_path_layout.addWidget(self.local_path)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._browse_directory)
        local_path_layout.addWidget(browse_btn)
        local_layout.addLayout(local_path_layout)
        
        local_pattern_layout = QHBoxLayout()
        local_pattern_layout.addWidget(QLabel("File Patterns:"))
        self.local_pattern = QLineEdit("*.py,*.js,*.java,*.cpp")
        local_pattern_layout.addWidget(self.local_pattern)
        local_layout.addLayout(local_pattern_layout)
        
        local_config.setLayout(local_layout)
        self.source_config_stack.addWidget(local_config)
        
        # Cloud storage configuration
        cloud_config = QWidget()
        cloud_layout = QVBoxLayout(cloud_config)
        
        cloud_provider_layout = QHBoxLayout()
        cloud_provider_layout.addWidget(QLabel("Provider:"))
        self.cloud_provider = QComboBox()
        self.cloud_provider.addItems(["AWS S3", "Google Cloud Storage", "Azure Blob"])
        cloud_provider_layout.addWidget(self.cloud_provider)
        cloud_layout.addLayout(cloud_provider_layout)
        
        cloud_bucket_layout = QHBoxLayout()
        cloud_bucket_layout.addWidget(QLabel("Bucket/Container:"))
        self.cloud_bucket = QLineEdit()
        cloud_bucket_layout.addWidget(self.cloud_bucket)
        cloud_layout.addLayout(cloud_bucket_layout)
        
        cloud_prefix_layout = QHBoxLayout()
        cloud_prefix_layout.addWidget(QLabel("Prefix:"))
        self.cloud_prefix = QLineEdit()
        cloud_prefix_layout.addWidget(self.cloud_prefix)
        cloud_layout.addLayout(cloud_prefix_layout)
        
        cloud_config.setLayout(cloud_layout)
        self.source_config_stack.addWidget(cloud_config)
        
        # Public dataset configuration
        public_config = QWidget()
        public_layout = QVBoxLayout(public_config)
        
        public_source_layout = QHBoxLayout()
        public_source_layout.addWidget(QLabel("Dataset Source:"))
        self.public_source = QComboBox()
        self.public_source.addItems([
            "CodeSearchNet",
            "CodeXGLUE",
            "CodeNet",
            "BigCode",
            "CodeParrot"
        ])
        public_source_layout.addWidget(self.public_source)
        public_layout.addLayout(public_source_layout)
        
        public_version_layout = QHBoxLayout()
        public_version_layout.addWidget(QLabel("Version:"))
        self.public_version = QComboBox()
        self.public_version.addItems(["latest", "stable", "beta"])
        public_version_layout.addWidget(self.public_version)
        public_layout.addLayout(public_version_layout)
        
        public_config.setLayout(public_layout)
        self.source_config_stack.addWidget(public_config)
        
        # Custom source configuration
        custom_config = QWidget()
        custom_layout = QVBoxLayout(custom_config)
        
        custom_url_layout = QHBoxLayout()
        custom_url_layout.addWidget(QLabel("Source URL:"))
        self.custom_url = QLineEdit()
        custom_url_layout.addWidget(self.custom_url)
        custom_layout.addLayout(custom_url_layout)
        
        custom_format_layout = QHBoxLayout()
        custom_format_layout.addWidget(QLabel("Format:"))
        self.custom_format = QComboBox()
        self.custom_format.addItems(["JSON", "CSV", "SQLite", "Custom"])
        custom_format_layout.addWidget(self.custom_format)
        custom_layout.addLayout(custom_format_layout)
        
        custom_config.setLayout(custom_layout)
        self.source_config_stack.addWidget(custom_config)
        
        source_layout.addWidget(self.source_config_stack)
        source_group.setLayout(source_layout)
        layout.addWidget(source_group)
        
        # Dataset manipulation
        manipulation_group = QGroupBox("Dataset Manipulation")
        manipulation_layout = QVBoxLayout()
        
        # Data cleaning
        cleaning_group = QGroupBox("Data Cleaning")
        cleaning_layout = QVBoxLayout()
        
        cleaning_options = [
            "Remove Comments",
            "Normalize Whitespace",
            "Remove Imports",
            "Standardize Formatting",
            "Remove Duplicates",
            "Fix Syntax Errors"
        ]
        
        for option in cleaning_options:
            cleaning_layout.addWidget(QCheckBox(option))
        
        cleaning_group.setLayout(cleaning_layout)
        manipulation_layout.addWidget(cleaning_group)
        
        # Data augmentation
        augmentation_group = QGroupBox("Data Augmentation")
        augmentation_layout = QVBoxLayout()
        
        augmentation_options = [
            "Variable Renaming",
            "Code Reordering",
            "Dead Code Insertion",
            "Comment Generation",
            "Code Style Transformation",
            "API Usage Pattern Generation"
        ]
        
        for option in augmentation_options:
            augmentation_layout.addWidget(QCheckBox(option))
        
        augmentation_group.setLayout(augmentation_layout)
        manipulation_layout.addWidget(augmentation_group)
        
        # Synthetic data generation
        synthetic_group = QGroupBox("Synthetic Data Generation")
        synthetic_layout = QVBoxLayout()
        
        # Generation scenarios
        scenario_layout = QHBoxLayout()
        scenario_layout.addWidget(QLabel("Scenario:"))
        self.scenario_combo = QComboBox()
        self.scenario_combo.addItems([
            "Code Completion",
            "Bug Detection",
            "Code Refactoring",
            "API Usage",
            "Security Analysis",
            "Performance Optimization"
        ])
        scenario_layout.addWidget(self.scenario_combo)
        synthetic_layout.addLayout(scenario_layout)
        
        # Generation rules
        rules_layout = QHBoxLayout()
        rules_layout.addWidget(QLabel("Rules:"))
        self.rules_combo = QComboBox()
        self.rules_combo.addItems([
            "Best Practices",
            "Security Guidelines",
            "Performance Standards",
            "Code Style Guide",
            "API Design Patterns",
            "Custom Rules"
        ])
        rules_layout.addWidget(self.rules_combo)
        synthetic_layout.addLayout(rules_layout)
        
        # Generation parameters
        params_layout = QGridLayout()
        
        params_layout.addWidget(QLabel("Sample Size:"), 0, 0)
        self.sample_size = QSpinBox()
        self.sample_size.setRange(100, 1000000)
        self.sample_size.setValue(1000)
        params_layout.addWidget(self.sample_size, 0, 1)
        
        params_layout.addWidget(QLabel("Complexity Level:"), 1, 0)
        self.complexity_level = QComboBox()
        self.complexity_level.addItems(["Low", "Medium", "High", "Mixed"])
        params_layout.addWidget(self.complexity_level, 1, 1)
        
        params_layout.addWidget(QLabel("Language:"), 2, 0)
        self.gen_language = QComboBox()
        self.gen_language.addItems(["Python", "JavaScript", "Java", "C++", "All"])
        params_layout.addWidget(self.gen_language, 2, 1)
        
        synthetic_layout.addLayout(params_layout)
        
        # Generate button
        generate_btn = QPushButton("Generate Synthetic Data")
        generate_btn.clicked.connect(self._generate_synthetic_data)
        synthetic_layout.addWidget(generate_btn)
        
        synthetic_group.setLayout(synthetic_layout)
        manipulation_layout.addWidget(synthetic_group)
        
        manipulation_group.setLayout(manipulation_layout)
        layout.addWidget(manipulation_group)
        
        # Dataset list
        self.dataset_table = QTableWidget()
        self.dataset_table.setColumnCount(6)
        self.dataset_table.setHorizontalHeaderLabels([
            "Name", "Size", "Type", "Source", "Status", "Last Modified"
        ])
        layout.addWidget(self.dataset_table)
        
        return page
    
    def _create_cloud_providers_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Provider selection
        provider_group = QGroupBox("Cloud Provider")
        provider_layout = QVBoxLayout()
        
        provider_select_layout = QHBoxLayout()
        provider_select_layout.addWidget(QLabel("Provider:"))
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["AWS", "Google Cloud", "Azure"])
        self.provider_combo.currentTextChanged.connect(self._change_provider)
        provider_select_layout.addWidget(self.provider_combo)
        
        provider_layout.addLayout(provider_select_layout)
        provider_group.setLayout(provider_layout)
        layout.addWidget(provider_group)
        
        # AWS Configuration
        self.aws_config = QWidget()
        aws_layout = QVBoxLayout(self.aws_config)
        
        # Credentials
        aws_creds_group = QGroupBox("Credentials")
        aws_creds_layout = QGridLayout()
        
        aws_creds_layout.addWidget(QLabel("Access Key:"), 0, 0)
        self.aws_access_key = QLineEdit()
        self.aws_access_key.setEchoMode(QLineEdit.EchoMode.Password)
        aws_creds_layout.addWidget(self.aws_access_key, 0, 1)
        
        aws_creds_layout.addWidget(QLabel("Secret Key:"), 1, 0)
        self.aws_secret_key = QLineEdit()
        self.aws_secret_key.setEchoMode(QLineEdit.EchoMode.Password)
        aws_creds_layout.addWidget(self.aws_secret_key, 1, 1)
        
        aws_creds_layout.addWidget(QLabel("Region:"), 2, 0)
        self.aws_region = QComboBox()
        self.aws_region.addItems([
            "us-east-1", "us-east-2", "us-west-1", "us-west-2",
            "eu-west-1", "eu-west-2", "eu-central-1", "ap-southeast-1",
            "ap-southeast-2", "ap-northeast-1", "ap-northeast-2"
        ])
        aws_creds_layout.addWidget(self.aws_region, 2, 1)
        
        aws_creds_group.setLayout(aws_creds_layout)
        aws_layout.addWidget(aws_creds_group)
        
        # S3 Configuration
        aws_s3_group = QGroupBox("S3 Configuration")
        aws_s3_layout = QGridLayout()
        
        aws_s3_layout.addWidget(QLabel("Bucket Name:"), 0, 0)
        self.aws_bucket = QLineEdit()
        aws_s3_layout.addWidget(self.aws_bucket, 0, 1)
        
        aws_s3_layout.addWidget(QLabel("Prefix:"), 1, 0)
        self.aws_prefix = QLineEdit()
        aws_s3_layout.addWidget(self.aws_prefix, 1, 1)
        
        aws_s3_group.setLayout(aws_s3_layout)
        aws_layout.addWidget(aws_s3_group)
        
        # SageMaker Configuration
        aws_sagemaker_group = QGroupBox("SageMaker Configuration")
        aws_sagemaker_layout = QGridLayout()
        
        aws_sagemaker_layout.addWidget(QLabel("Role ARN:"), 0, 0)
        self.aws_role_arn = QLineEdit()
        aws_sagemaker_layout.addWidget(self.aws_role_arn, 0, 1)
        
        aws_sagemaker_layout.addWidget(QLabel("Instance Type:"), 1, 0)
        self.aws_instance_type = QComboBox()
        self.aws_instance_type.addItems([
            "ml.p3.2xlarge", "ml.p3.8xlarge", "ml.p3.16xlarge",
            "ml.p3dn.24xlarge", "ml.g4dn.xlarge", "ml.g4dn.2xlarge",
            "ml.g4dn.4xlarge", "ml.g4dn.8xlarge", "ml.g4dn.16xlarge"
        ])
        aws_sagemaker_layout.addWidget(self.aws_instance_type, 1, 1)
        
        aws_sagemaker_layout.addWidget(QLabel("Instance Count:"), 2, 0)
        self.aws_instance_count = QSpinBox()
        self.aws_instance_count.setRange(1, 10)
        self.aws_instance_count.setValue(1)
        aws_sagemaker_layout.addWidget(self.aws_instance_count, 2, 1)
        
        aws_sagemaker_group.setLayout(aws_sagemaker_layout)
        aws_layout.addWidget(aws_sagemaker_group)
        
        # Google Cloud Configuration
        self.gcp_config = QWidget()
        gcp_layout = QVBoxLayout(self.gcp_config)
        
        # Project Configuration
        gcp_project_group = QGroupBox("Project Configuration")
        gcp_project_layout = QGridLayout()
        
        gcp_project_layout.addWidget(QLabel("Project ID:"), 0, 0)
        self.gcp_project_id = QLineEdit()
        gcp_project_layout.addWidget(self.gcp_project_id, 0, 1)
        
        gcp_project_layout.addWidget(QLabel("Service Account:"), 1, 0)
        self.gcp_service_account = QLineEdit()
        gcp_project_layout.addWidget(self.gcp_service_account, 1, 1)
        
        gcp_project_group.setLayout(gcp_project_layout)
        gcp_layout.addWidget(gcp_project_group)
        
        # Vertex AI Configuration
        gcp_vertex_group = QGroupBox("Vertex AI Configuration")
        gcp_vertex_layout = QGridLayout()
        
        gcp_vertex_layout.addWidget(QLabel("Region:"), 0, 0)
        self.gcp_region = QComboBox()
        self.gcp_region.addItems([
            "us-central1", "us-east1", "us-east4", "us-west1",
            "us-west4", "europe-west1", "europe-west2", "europe-west3",
            "europe-west4", "europe-west9", "asia-east1", "asia-northeast1"
        ])
        gcp_vertex_layout.addWidget(self.gcp_region, 0, 1)
        
        gcp_vertex_layout.addWidget(QLabel("Machine Type:"), 1, 0)
        self.gcp_machine_type = QComboBox()
        self.gcp_machine_type.addItems([
            "n1-standard-4", "n1-standard-8", "n1-standard-16",
            "n1-standard-32", "n1-standard-64", "n1-standard-96",
            "n1-highmem-4", "n1-highmem-8", "n1-highmem-16",
            "n1-highmem-32", "n1-highmem-64", "n1-highmem-96"
        ])
        gcp_vertex_layout.addWidget(self.gcp_machine_type, 1, 1)
        
        gcp_vertex_layout.addWidget(QLabel("Accelerator Type:"), 2, 0)
        self.gcp_accelerator = QComboBox()
        self.gcp_accelerator.addItems([
            "NVIDIA_TESLA_K80", "NVIDIA_TESLA_P100", "NVIDIA_TESLA_V100",
            "NVIDIA_TESLA_P4", "NVIDIA_TESLA_T4", "NVIDIA_A100"
        ])
        gcp_vertex_layout.addWidget(self.gcp_accelerator, 2, 1)
        
        gcp_vertex_group.setLayout(gcp_vertex_layout)
        gcp_layout.addWidget(gcp_vertex_group)
        
        # Azure Configuration
        self.azure_config = QWidget()
        azure_layout = QVBoxLayout(self.azure_config)
        
        # Subscription Configuration
        azure_sub_group = QGroupBox("Subscription Configuration")
        azure_sub_layout = QGridLayout()
        
        azure_sub_layout.addWidget(QLabel("Subscription ID:"), 0, 0)
        self.azure_subscription_id = QLineEdit()
        azure_sub_layout.addWidget(self.azure_subscription_id, 0, 1)
        
        azure_sub_layout.addWidget(QLabel("Tenant ID:"), 1, 0)
        self.azure_tenant_id = QLineEdit()
        azure_sub_layout.addWidget(self.azure_tenant_id, 1, 1)
        
        azure_sub_layout.addWidget(QLabel("Client ID:"), 2, 0)
        self.azure_client_id = QLineEdit()
        azure_sub_layout.addWidget(self.azure_client_id, 2, 1)
        
        azure_sub_layout.addWidget(QLabel("Client Secret:"), 3, 0)
        self.azure_client_secret = QLineEdit()
        self.azure_client_secret.setEchoMode(QLineEdit.EchoMode.Password)
        azure_sub_layout.addWidget(self.azure_client_secret, 3, 1)
        
        azure_sub_group.setLayout(azure_sub_layout)
        azure_layout.addWidget(azure_sub_group)
        
        # Azure ML Configuration
        azure_ml_group = QGroupBox("Azure ML Configuration")
        azure_ml_layout = QGridLayout()
        
        azure_ml_layout.addWidget(QLabel("Resource Group:"), 0, 0)
        self.azure_resource_group = QLineEdit()
        azure_ml_layout.addWidget(self.azure_resource_group, 0, 1)
        
        azure_ml_layout.addWidget(QLabel("Workspace Name:"), 1, 0)
        self.azure_workspace = QLineEdit()
        azure_ml_layout.addWidget(self.azure_workspace, 1, 1)
        
        azure_ml_layout.addWidget(QLabel("Compute Target:"), 2, 0)
        self.azure_compute = QComboBox()
        self.azure_compute.addItems([
            "Standard_NC6", "Standard_NC12", "Standard_NC24",
            "Standard_NC24r", "Standard_ND6s", "Standard_ND12s",
            "Standard_ND24s", "Standard_ND24rs", "Standard_NC4as_T4_v3",
            "Standard_NC8as_T4_v3", "Standard_NC16as_T4_v3",
            "Standard_NC64as_T4_v3"
        ])
        azure_ml_layout.addWidget(self.azure_compute, 2, 1)
        
        azure_ml_group.setLayout(azure_ml_layout)
        azure_layout.addWidget(azure_ml_group)
        
        # Add provider configurations to stacked widget
        self.provider_configs = QStackedWidget()
        self.provider_configs.addWidget(self.aws_config)
        self.provider_configs.addWidget(self.gcp_config)
        self.provider_configs.addWidget(self.azure_config)
        layout.addWidget(self.provider_configs)
        
        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self._save_provider_settings)
        layout.addWidget(save_btn)
        
        return page
    
    def _create_monitoring_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Resource monitor
        self.monitor = ResourceMonitor()
        layout.addWidget(self.monitor)
        
        # Metrics plot
        self.monitoring_plot = MetricsPlot()
        layout.addWidget(self.monitoring_plot)
        
        return page
    
    def _create_settings_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Notification settings
        self.notification_widget = NotificationWidget()
        layout.addWidget(self.notification_widget)
        
        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self._save_settings)
        layout.addWidget(save_btn)
        
        return page
    
    def _create_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("assets/icon.ico"))
        
        # Create tray menu
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show")
        show_action.triggered.connect(self.show)
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(self.close)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    def _apply_style(self):
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #2C3E50;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #34495E;
            }
            QPushButton:disabled {
                background-color: #95A5A6;
            }
            QLabel {
                color: #2C3E50;
            }
            QFrame {
                background-color: white;
                border-radius: 4px;
            }
            QGroupBox {
                background-color: white;
                border-radius: 4px;
                margin-top: 1em;
                padding-top: 1em;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #3498DB;
                color: white;
            }
            QProgressBar {
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498DB;
            }
        """)
    
    def _show_dashboard(self):
        self.content.setCurrentIndex(0)
    
    def _show_training(self):
        self.content.setCurrentIndex(1)
    
    def _show_datasets(self):
        self.content.setCurrentIndex(2)
    
    def _show_cloud_providers(self):
        self.content.setCurrentIndex(3)
    
    def _show_monitoring(self):
        self.content.setCurrentIndex(4)
    
    def _show_settings(self):
        self.content.setCurrentIndex(5)
    
    def _start_training(self):
        """Start training all components"""
        if not self.model_trainer:
            QMessageBox.warning(self, "Error", "Model trainer not initialized")
            return
            
        asyncio.create_task(self.model_trainer.train_all_components())
    
    def _stop_training(self):
        """Stop all training processes"""
        # Implementation for stopping training
        pass
    
    def _pause_training(self):
        """Pause/resume training processes"""
        # Implementation for pausing/resuming training
        pass
    
    def _add_dataset(self):
        # Implementation for adding a dataset
        pass
    
    def _import_dataset(self):
        # Implementation for importing dataset from cloud
        pass
    
    def _import_from_github(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Import from GitHub")
        layout = QVBoxLayout(dialog)
        
        # Repository URL
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("Repository URL:"))
        repo_url = QLineEdit()
        url_layout.addWidget(repo_url)
        layout.addLayout(url_layout)
        
        # Branch selection
        branch_layout = QHBoxLayout()
        branch_layout.addWidget(QLabel("Branch:"))
        branch_combo = QComboBox()
        branch_combo.addItems(["main", "master", "develop"])
        branch_layout.addWidget(branch_combo)
        layout.addLayout(branch_layout)
        
        # File patterns
        pattern_layout = QHBoxLayout()
        pattern_layout.addWidget(QLabel("File Patterns:"))
        pattern_edit = QLineEdit("*.py,*.js,*.java,*.cpp")
        pattern_layout.addWidget(pattern_edit)
        layout.addLayout(pattern_layout)
        
        # Import button
        import_btn = QPushButton("Import")
        import_btn.clicked.connect(dialog.accept)
        layout.addWidget(import_btn)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Implementation for GitHub import
            pass
    
    def _generate_dataset(self):
        # Implementation for dataset generation
        pass
    
    def _send_chat_message(self):
        message = self.chat_input.text()
        if message:
            self.chat_text.append(f"You: {message}")
            
            # Get selected model and context
            model = self.chat_model_combo.currentText()
            context = self.context_combo.currentText()
            
            # Generate response based on model and context
            response = self._get_code_aware_response(message, model, context)
            self.chat_text.append(f"Assistant: {response}")
            self.chat_input.clear()
    
    def _get_code_aware_response(self, message: str, model: str, context: str) -> str:
        message = message.lower()
        
        if context == "Dataset Generation":
            if "strategy" in message or "approach" in message:
                return """For code-aware dataset generation, I recommend:
1. AST Analysis:
   - Parse code into Abstract Syntax Trees
   - Extract structural patterns
   - Identify code dependencies
2. Semantic Analysis:
   - Variable and function relationships
   - Control flow patterns
   - Data flow tracking
3. Code Quality Metrics:
   - Complexity analysis
   - Code coverage
   - Maintainability scores
4. Domain-Specific Features:
   - Language-specific patterns
   - Framework usage
   - Best practices compliance"""
            
            elif "preprocessing" in message:
                return """Code-aware preprocessing pipeline:
1. Tokenization:
   - BPE for code-specific tokens
   - Special token handling for code constructs
   - Whitespace preservation
2. Code Cleaning:
   - Comment removal
   - Import normalization
   - Code formatting
3. Data Augmentation:
   - Variable renaming
   - Code reordering
   - Dead code insertion
4. Quality Filtering:
   - Syntax validation
   - Style checking
   - Performance profiling"""
        
        elif context == "Training Rules":
            if "rules" in message or "guidelines" in message:
                return """Code-aware training rules:
1. Code Structure Understanding:
   - Syntax tree traversal
   - Dependency graph analysis
   - Control flow mapping
2. Semantic Analysis:
   - Variable scope tracking
   - Function call patterns
   - Type inference
3. Error Detection:
   - Syntax error patterns
   - Runtime error prediction
   - Code smell detection
4. Code Generation:
   - Context-aware completion
   - API usage patterns
   - Best practice adherence"""
        
        elif context == "Model Selection":
            if "model" in message or "architecture" in message:
                return """Recommended models for code awareness:
1. Claude 3.7 Sonnet:
   - Excellent code understanding
   - Strong reasoning capabilities
   - Context-aware responses
2. CodeLlama-34B:
   - Specialized for code
   - Large context window
   - Multi-language support
3. StarCoder-33B:
   - Code-specific training
   - Fast inference
   - Good for real-time use"""
        
        elif context == "Code Analysis":
            if "analysis" in message or "metrics" in message:
                return """Code analysis metrics:
1. Complexity Metrics:
   - Cyclomatic complexity
   - Cognitive complexity
   - Maintainability index
2. Quality Metrics:
   - Code coverage
   - Test coverage
   - Bug density
3. Performance Metrics:
   - Execution time
   - Memory usage
   - Resource utilization"""
        
        elif context == "Performance Optimization":
            if "optimize" in message or "performance" in message:
                return """Performance optimization strategies:
1. Code Level:
   - Algorithm optimization
   - Memory management
   - Cache utilization
2. Training Level:
   - Batch size tuning
   - Learning rate scheduling
   - Gradient accumulation
3. System Level:
   - Resource allocation
   - Parallel processing
   - Distributed training"""
        
        return """I can help you with:
- Dataset generation strategies
- Training rules and guidelines
- Model selection and architecture
- Code analysis and metrics
- Performance optimization
What would you like to know more about?"""
    
    def _quick_action(self, action: str):
        if action == "Dataset Strategy":
            self.context_combo.setCurrentText("Dataset Generation")
            self.chat_input.setText("What's the best strategy for code-aware dataset generation?")
            self._send_chat_message()
        elif action == "Training Rules":
            self.context_combo.setCurrentText("Training Rules")
            self.chat_input.setText("What are the recommended training rules for code-aware models?")
            self._send_chat_message()
        elif action == "Model Selection":
            self.context_combo.setCurrentText("Model Selection")
            self.chat_input.setText("Which models are best suited for code-aware training?")
            self._send_chat_message()
        elif action == "Code Analysis":
            self.context_combo.setCurrentText("Code Analysis")
            self.chat_input.setText("What metrics should I use for code analysis?")
            self._send_chat_message()
        elif action == "Performance Tips":
            self.context_combo.setCurrentText("Performance Optimization")
            self.chat_input.setText("How can I optimize the training process?")
            self._send_chat_message()
    
    def _change_provider(self, provider: str):
        provider_map = {
            "AWS": 0,
            "Google Cloud": 1,
            "Azure": 2
        }
        self.provider_configs.setCurrentIndex(provider_map[provider])
    
    def _save_provider_settings(self):
        provider = self.provider_combo.currentText()
        settings = {}
        
        if provider == "AWS":
            settings = {
                "access_key": self.aws_access_key.text(),
                "secret_key": self.aws_secret_key.text(),
                "region": self.aws_region.currentText(),
                "bucket": self.aws_bucket.text(),
                "prefix": self.aws_prefix.text(),
                "role_arn": self.aws_role_arn.text(),
                "instance_type": self.aws_instance_type.currentText(),
                "instance_count": self.aws_instance_count.value()
            }
        elif provider == "Google Cloud":
            settings = {
                "project_id": self.gcp_project_id.text(),
                "service_account": self.gcp_service_account.text(),
                "region": self.gcp_region.currentText(),
                "machine_type": self.gcp_machine_type.currentText(),
                "accelerator_type": self.gcp_accelerator.currentText()
            }
        else:  # Azure
            settings = {
                "subscription_id": self.azure_subscription_id.text(),
                "tenant_id": self.azure_tenant_id.text(),
                "client_id": self.azure_client_id.text(),
                "client_secret": self.azure_client_secret.text(),
                "resource_group": self.azure_resource_group.text(),
                "workspace_name": self.azure_workspace.text(),
                "compute_target": self.azure_compute.currentText()
            }
        
        # Save settings to configuration file
        config_path = Path("config") / f"{provider.lower()}_config.json"
        config_path.parent.mkdir(exist_ok=True)
        
        with open(config_path, "w") as f:
            json.dump(settings, f, indent=4)
        
        QMessageBox.information(
            self,
            "Settings Saved",
            f"{provider} settings have been saved successfully."
        )
    
    def _save_settings(self):
        # Implementation for saving application settings
        pass
    
    def closeEvent(self, event):
        # Minimize to tray instead of closing
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "ADE Training Manager",
            "Application minimized to tray",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
    
    def _change_source_type(self, source_type: str):
        source_map = {
            "GitHub Repository": 0,
            "Local Directory": 1,
            "Cloud Storage": 2,
            "Public Dataset": 3,
            "Custom Source": 4
        }
        self.source_config_stack.setCurrentIndex(source_map[source_type])
    
    def _browse_directory(self):
        # Implementation for directory browsing
        pass
    
    def _generate_synthetic_data(self):
        # Implementation for synthetic data generation
        pass
    
    async def _train_component(self, component: str):
        """Train a specific model component"""
        if not self.model_trainer:
            QMessageBox.warning(self, "Error", "Model trainer not initialized")
            return
            
        try:
            # Map UI component names to trainer component names
            component_map = {
                "Code Understanding (CodeLlama-34B)": "code_understanding",
                "Tool Use (Claude 3 Sonnet)": "tool_use",
                "Planning (Claude 3 Sonnet)": "planning",
                "Code Generation (StarCoder2-33B)": "code_generation"
            }
            
            trainer_component = component_map.get(component)
            if not trainer_component:
                QMessageBox.warning(self, "Error", f"Unknown component: {component}")
                return
                
            # Update progress
            self.progress_text.append(f"Starting training for {component}...")
            
            # Train component
            success = await self.model_trainer.train_single_component(trainer_component)
            
            if success:
                self.progress_text.append(f"Successfully trained {component}")
                QMessageBox.information(self, "Success", f"Successfully trained {component}")
            else:
                self.progress_text.append(f"Failed to train {component}")
                QMessageBox.warning(self, "Error", f"Failed to train {component}")
                
        except Exception as e:
            self.progress_text.append(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Training failed: {str(e)}")
            
    async def _evaluate_component(self, component: str):
        """Evaluate a specific model component"""
        if not self.model_trainer:
            QMessageBox.warning(self, "Error", "Model trainer not initialized")
            return
            
        try:
            # Map UI component names to trainer component names
            component_map = {
                "Code Understanding (CodeLlama-34B)": "code_understanding",
                "Tool Use (Claude 3 Sonnet)": "tool_use",
                "Planning (Claude 3 Sonnet)": "planning",
                "Code Generation (StarCoder2-33B)": "code_generation"
            }
            
            trainer_component = component_map.get(component)
            if not trainer_component:
                QMessageBox.warning(self, "Error", f"Unknown component: {component}")
                return
                
            # Update progress
            self.progress_text.append(f"Starting evaluation for {component}...")
            
            # Run A/B test
            await self.model_trainer.run_ab_tests()
            
            self.progress_text.append(f"Completed evaluation for {component}")
            QMessageBox.information(self, "Success", f"Completed evaluation for {component}")
            
        except Exception as e:
            self.progress_text.append(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Evaluation failed: {str(e)}") 