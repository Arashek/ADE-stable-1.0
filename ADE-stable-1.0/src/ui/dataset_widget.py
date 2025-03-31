from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QLabel, QComboBox,
                             QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox,
                             QFileDialog, QMessageBox, QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt
from typing import Dict, Any, Optional
import json
from pathlib import Path

class DatasetWidget(QWidget):
    """Widget for managing datasets"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dataset management UI"""
        layout = QVBoxLayout(self)
        
        # Dataset list
        self.dataset_table = QTableWidget()
        self.dataset_table.setColumnCount(5)
        self.dataset_table.setHorizontalHeaderLabels([
            "Name", "Type", "Size", "Status", "Actions"
        ])
        layout.addWidget(self.dataset_table)
        
        # Add dataset button
        add_button = QPushButton("Add Dataset")
        add_button.clicked.connect(self.show_add_dataset_dialog)
        layout.addWidget(add_button)
        
        # Dataset configuration group
        config_group = QGroupBox("Dataset Configuration")
        config_layout = QFormLayout()
        
        # Source type selection
        self.source_type = QComboBox()
        self.source_type.addItems([
            "Local", "GitHub", "Cloud Storage", "Public Dataset", "Custom"
        ])
        self.source_type.currentTextChanged.connect(self.update_source_config)
        config_layout.addRow("Source Type:", self.source_type)
        
        # Source configuration
        self.source_config = QWidget()
        self.source_layout = QFormLayout(self.source_config)
        config_layout.addRow("Source Config:", self.source_config)
        
        # Processing configuration
        self.processing_config = QGroupBox("Processing Configuration")
        processing_layout = QFormLayout()
        
        self.shuffle_data = QCheckBox()
        processing_layout.addRow("Shuffle Data:", self.shuffle_data)
        
        self.train_split = QDoubleSpinBox()
        self.train_split.setRange(0.0, 1.0)
        self.train_split.setValue(0.8)
        processing_layout.addRow("Train Split:", self.train_split)
        
        self.val_split = QDoubleSpinBox()
        self.val_split.setRange(0.0, 1.0)
        self.val_split.setValue(0.1)
        processing_layout.addRow("Validation Split:", self.val_split)
        
        self.test_split = QDoubleSpinBox()
        self.test_split.setRange(0.0, 1.0)
        self.test_split.setValue(0.1)
        processing_layout.addRow("Test Split:", self.test_split)
        
        self.processing_config.setLayout(processing_layout)
        config_layout.addRow(self.processing_config)
        
        # Augmentation configuration
        self.augmentation_config = QGroupBox("Augmentation Configuration")
        augmentation_layout = QFormLayout()
        
        self.enable_augmentation = QCheckBox()
        augmentation_layout.addRow("Enable Augmentation:", self.enable_augmentation)
        
        self.augmentation_methods = QComboBox()
        self.augmentation_methods.addItems([
            "None", "Random Masking", "Random Deletion", "Random Insertion",
            "Random Substitution", "Back Translation"
        ])
        augmentation_layout.addRow("Augmentation Method:", self.augmentation_methods)
        
        self.augmentation_prob = QDoubleSpinBox()
        self.augmentation_prob.setRange(0.0, 1.0)
        self.augmentation_prob.setValue(0.1)
        augmentation_layout.addRow("Augmentation Probability:", self.augmentation_prob)
        
        self.augmentation_config.setLayout(augmentation_layout)
        config_layout.addRow(self.augmentation_config)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Save configuration button
        save_button = QPushButton("Save Configuration")
        save_button.clicked.connect(self.save_configuration)
        layout.addWidget(save_button)
        
        # Initialize source configuration
        self.update_source_config(self.source_type.currentText())
        
    def update_source_config(self, source_type: str):
        """Update the source configuration UI based on selected source type"""
        # Clear existing widgets
        while self.source_layout.count():
            item = self.source_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        if source_type == "Local":
            # Local file selection
            path_edit = QLineEdit()
            browse_button = QPushButton("Browse")
            browse_button.clicked.connect(lambda: self.browse_local_file(path_edit))
            path_layout = QHBoxLayout()
            path_layout.addWidget(path_edit)
            path_layout.addWidget(browse_button)
            self.source_layout.addRow("Dataset Path:", path_layout)
            
        elif source_type == "GitHub":
            # GitHub repository configuration
            repo_edit = QLineEdit()
            self.source_layout.addRow("Repository URL:", repo_edit)
            
            branch_edit = QLineEdit()
            self.source_layout.addRow("Branch:", branch_edit)
            
            path_edit = QLineEdit()
            self.source_layout.addRow("Dataset Path:", path_edit)
            
        elif source_type == "Cloud Storage":
            # Cloud storage configuration
            provider_combo = QComboBox()
            provider_combo.addItems(["AWS S3", "Google Cloud Storage", "Azure Blob Storage"])
            self.source_layout.addRow("Provider:", provider_combo)
            
            bucket_edit = QLineEdit()
            self.source_layout.addRow("Bucket/Container:", bucket_edit)
            
            path_edit = QLineEdit()
            self.source_layout.addRow("Dataset Path:", path_edit)
            
        elif source_type == "Public Dataset":
            # Public dataset selection
            dataset_combo = QComboBox()
            dataset_combo.addItems([
                "MNIST", "CIFAR-10", "CIFAR-100", "ImageNet", "COCO",
                "SQuAD", "GLUE", "SuperGLUE"
            ])
            self.source_layout.addRow("Dataset:", dataset_combo)
            
        elif source_type == "Custom":
            # Custom dataset configuration
            name_edit = QLineEdit()
            self.source_layout.addRow("Dataset Name:", name_edit)
            
            format_combo = QComboBox()
            format_combo.addItems(["CSV", "JSON", "JSONL", "Text", "Custom"])
            self.source_layout.addRow("Format:", format_combo)
            
            path_edit = QLineEdit()
            browse_button = QPushButton("Browse")
            browse_button.clicked.connect(lambda: self.browse_local_file(path_edit))
            path_layout = QHBoxLayout()
            path_layout.addWidget(path_edit)
            path_layout.addWidget(browse_button)
            self.source_layout.addRow("Dataset Path:", path_layout)
            
    def browse_local_file(self, path_edit: QLineEdit):
        """Open file dialog for selecting local files"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Dataset File",
            "",
            "All Files (*.*);;CSV Files (*.csv);;JSON Files (*.json);;Text Files (*.txt)"
        )
        if file_path:
            path_edit.setText(file_path)
            
    def save_configuration(self):
        """Save the current dataset configuration"""
        try:
            # Get source configuration
            source_type = self.source_type.currentText()
            source_config = {}
            
            if source_type == "Local":
                source_config["path"] = self.source_layout.itemAt(0).widget().itemAt(0).widget().text()
                
            elif source_type == "GitHub":
                source_config["repository"] = self.source_layout.itemAt(0).widget().text()
                source_config["branch"] = self.source_layout.itemAt(1).widget().text()
                source_config["path"] = self.source_layout.itemAt(2).widget().text()
                
            elif source_type == "Cloud Storage":
                source_config["provider"] = self.source_layout.itemAt(0).widget().currentText()
                source_config["bucket"] = self.source_layout.itemAt(1).widget().text()
                source_config["path"] = self.source_layout.itemAt(2).widget().text()
                
            elif source_type == "Public Dataset":
                source_config["name"] = self.source_layout.itemAt(0).widget().currentText()
                
            elif source_type == "Custom":
                source_config["name"] = self.source_layout.itemAt(0).widget().text()
                source_config["format"] = self.source_layout.itemAt(1).widget().currentText()
                source_config["path"] = self.source_layout.itemAt(2).widget().itemAt(0).widget().text()
                
            # Get processing configuration
            processing_config = {
                "shuffle": self.shuffle_data.isChecked(),
                "train_split": self.train_split.value(),
                "val_split": self.val_split.value(),
                "test_split": self.test_split.value()
            }
            
            # Get augmentation configuration
            augmentation_config = {
                "enabled": self.enable_augmentation.isChecked(),
                "method": self.augmentation_methods.currentText(),
                "probability": self.augmentation_prob.value()
            }
            
            # Create complete configuration
            config = {
                "source_type": source_type,
                "source_config": source_config,
                "processing_config": processing_config,
                "augmentation_config": augmentation_config
            }
            
            # Save to file
            config_dir = Path("configs")
            config_dir.mkdir(exist_ok=True)
            
            config_file = config_dir / "dataset_config.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=4)
                
            QMessageBox.information(self, "Success", "Dataset configuration saved successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {str(e)}")
            
    def load_configuration(self, config_file: str):
        """Load dataset configuration from file"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                
            # Set source type and configuration
            self.source_type.setCurrentText(config["source_type"])
            self.update_source_config(config["source_type"])
            
            # Update source configuration widgets
            source_config = config["source_config"]
            if config["source_type"] == "Local":
                self.source_layout.itemAt(0).widget().itemAt(0).widget().setText(source_config["path"])
                
            elif config["source_type"] == "GitHub":
                self.source_layout.itemAt(0).widget().setText(source_config["repository"])
                self.source_layout.itemAt(1).widget().setText(source_config["branch"])
                self.source_layout.itemAt(2).widget().setText(source_config["path"])
                
            elif config["source_type"] == "Cloud Storage":
                self.source_layout.itemAt(0).widget().setCurrentText(source_config["provider"])
                self.source_layout.itemAt(1).widget().setText(source_config["bucket"])
                self.source_layout.itemAt(2).widget().setText(source_config["path"])
                
            elif config["source_type"] == "Public Dataset":
                self.source_layout.itemAt(0).widget().setCurrentText(source_config["name"])
                
            elif config["source_type"] == "Custom":
                self.source_layout.itemAt(0).widget().setText(source_config["name"])
                self.source_layout.itemAt(1).widget().setCurrentText(source_config["format"])
                self.source_layout.itemAt(2).widget().itemAt(0).widget().setText(source_config["path"])
                
            # Update processing configuration
            processing_config = config["processing_config"]
            self.shuffle_data.setChecked(processing_config["shuffle"])
            self.train_split.setValue(processing_config["train_split"])
            self.val_split.setValue(processing_config["val_split"])
            self.test_split.setValue(processing_config["test_split"])
            
            # Update augmentation configuration
            augmentation_config = config["augmentation_config"]
            self.enable_augmentation.setChecked(augmentation_config["enabled"])
            self.augmentation_methods.setCurrentText(augmentation_config["method"])
            self.augmentation_prob.setValue(augmentation_config["probability"])
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load configuration: {str(e)}")
            
    def update_dataset_table(self, datasets: list):
        """Update the dataset table with current datasets"""
        self.dataset_table.setRowCount(len(datasets))
        
        for i, dataset in enumerate(datasets):
            # Name
            self.dataset_table.setItem(i, 0, QTableWidgetItem(dataset["name"]))
            
            # Type
            self.dataset_table.setItem(i, 1, QTableWidgetItem(dataset["type"]))
            
            # Size
            self.dataset_table.setItem(i, 2, QTableWidgetItem(str(dataset["size"])))
            
            # Status
            self.dataset_table.setItem(i, 3, QTableWidgetItem(dataset["status"]))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_button = QPushButton("Edit")
            edit_button.clicked.connect(lambda checked, d=dataset: self.edit_dataset(d))
            actions_layout.addWidget(edit_button)
            
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda checked, d=dataset: self.delete_dataset(d))
            actions_layout.addWidget(delete_button)
            
            self.dataset_table.setCellWidget(i, 4, actions_widget)
            
    def edit_dataset(self, dataset: Dict[str, Any]):
        """Edit a dataset configuration"""
        # TODO: Implement dataset editing
        pass
        
    def delete_dataset(self, dataset: Dict[str, Any]):
        """Delete a dataset"""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete dataset '{dataset['name']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # TODO: Implement dataset deletion
                QMessageBox.information(self, "Success", "Dataset deleted successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete dataset: {str(e)}")
                
    def show_add_dataset_dialog(self):
        """Show dialog for adding a new dataset"""
        # TODO: Implement add dataset dialog
        pass 