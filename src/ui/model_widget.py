from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QLabel, QComboBox,
                             QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox,
                             QFileDialog, QMessageBox, QGroupBox, QFormLayout,
                             QTextEdit)
from PyQt6.QtCore import Qt
from typing import Dict, Any, Optional
import json
from pathlib import Path

class ModelWidget(QWidget):
    """Widget for managing model configurations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the model management UI"""
        layout = QVBoxLayout(self)
        
        # Model list
        self.model_table = QTableWidget()
        self.model_table.setColumnCount(5)
        self.model_table.setHorizontalHeaderLabels([
            "Name", "Type", "Size", "Status", "Actions"
        ])
        layout.addWidget(self.model_table)
        
        # Add model button
        add_button = QPushButton("Add Model")
        add_button.clicked.connect(self.show_add_model_dialog)
        layout.addWidget(add_button)
        
        # Model configuration group
        config_group = QGroupBox("Model Configuration")
        config_layout = QFormLayout()
        
        # Basic configuration
        basic_group = QGroupBox("Basic Configuration")
        basic_layout = QFormLayout()
        
        self.model_name = QLineEdit()
        basic_layout.addRow("Model Name:", self.model_name)
        
        self.model_type = QComboBox()
        self.model_type.addItems([
            "Transformer", "CNN", "RNN", "LSTM", "GRU",
            "Autoencoder", "GAN", "Custom"
        ])
        basic_layout.addRow("Model Type:", self.model_type)
        
        self.model_version = QLineEdit()
        basic_layout.addRow("Version:", self.model_version)
        
        basic_group.setLayout(basic_layout)
        config_layout.addRow(basic_group)
        
        # Architecture configuration
        arch_group = QGroupBox("Architecture Configuration")
        arch_layout = QFormLayout()
        
        self.hidden_size = QSpinBox()
        self.hidden_size.setRange(64, 4096)
        self.hidden_size.setValue(768)
        arch_layout.addRow("Hidden Size:", self.hidden_size)
        
        self.num_layers = QSpinBox()
        self.num_layers.setRange(1, 24)
        self.num_layers.setValue(6)
        arch_layout.addRow("Number of Layers:", self.num_layers)
        
        self.num_heads = QSpinBox()
        self.num_heads.setRange(1, 64)
        self.num_heads.setValue(12)
        arch_layout.addRow("Number of Heads:", self.num_heads)
        
        self.ffn_size = QSpinBox()
        self.ffn_size.setRange(128, 16384)
        self.ffn_size.setValue(3072)
        arch_layout.addRow("FFN Size:", self.ffn_size)
        
        self.max_position = QSpinBox()
        self.max_position.setRange(128, 8192)
        self.max_position.setValue(512)
        arch_layout.addRow("Max Position:", self.max_position)
        
        self.vocab_size = QSpinBox()
        self.vocab_size.setRange(1000, 1000000)
        self.vocab_size.setValue(50257)
        arch_layout.addRow("Vocabulary Size:", self.vocab_size)
        
        arch_group.setLayout(arch_layout)
        config_layout.addRow(arch_group)
        
        # Training configuration
        train_group = QGroupBox("Training Configuration")
        train_layout = QFormLayout()
        
        self.batch_size = QSpinBox()
        self.batch_size.setRange(1, 1024)
        self.batch_size.setValue(32)
        train_layout.addRow("Batch Size:", self.batch_size)
        
        self.learning_rate = QDoubleSpinBox()
        self.learning_rate.setRange(1e-6, 1e-2)
        self.learning_rate.setValue(1e-4)
        self.learning_rate.setSingleStep(1e-5)
        train_layout.addRow("Learning Rate:", self.learning_rate)
        
        self.epochs = QSpinBox()
        self.epochs.setRange(1, 1000)
        self.epochs.setValue(10)
        train_layout.addRow("Number of Epochs:", self.epochs)
        
        self.warmup_steps = QSpinBox()
        self.warmup_steps.setRange(0, 10000)
        self.warmup_steps.setValue(1000)
        train_layout.addRow("Warmup Steps:", self.warmup_steps)
        
        self.weight_decay = QDoubleSpinBox()
        self.weight_decay.setRange(0.0, 1.0)
        self.weight_decay.setValue(0.01)
        self.weight_decay.setSingleStep(0.001)
        train_layout.addRow("Weight Decay:", self.weight_decay)
        
        self.gradient_clipping = QDoubleSpinBox()
        self.gradient_clipping.setRange(0.0, 10.0)
        self.gradient_clipping.setValue(1.0)
        self.gradient_clipping.setSingleStep(0.1)
        train_layout.addRow("Gradient Clipping:", self.gradient_clipping)
        
        train_group.setLayout(train_layout)
        config_layout.addRow(train_group)
        
        # Advanced configuration
        advanced_group = QGroupBox("Advanced Configuration")
        advanced_layout = QFormLayout()
        
        self.use_amp = QCheckBox()
        advanced_layout.addRow("Use Automatic Mixed Precision:", self.use_amp)
        
        self.use_gradient_checkpointing = QCheckBox()
        advanced_layout.addRow("Use Gradient Checkpointing:", self.use_gradient_checkpointing)
        
        self.use_ema = QCheckBox()
        advanced_layout.addRow("Use Exponential Moving Average:", self.use_ema)
        
        self.ema_decay = QDoubleSpinBox()
        self.ema_decay.setRange(0.0, 1.0)
        self.ema_decay.setValue(0.999)
        self.ema_decay.setSingleStep(0.001)
        advanced_layout.addRow("EMA Decay:", self.ema_decay)
        
        self.custom_params = QTextEdit()
        self.custom_params.setPlaceholderText("Enter custom parameters in JSON format")
        advanced_layout.addRow("Custom Parameters:", self.custom_params)
        
        advanced_group.setLayout(advanced_layout)
        config_layout.addRow(advanced_group)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Save configuration button
        save_button = QPushButton("Save Configuration")
        save_button.clicked.connect(self.save_configuration)
        layout.addWidget(save_button)
        
    def save_configuration(self):
        """Save the current model configuration"""
        try:
            # Create configuration dictionary
            config = {
                "name": self.model_name.text(),
                "model_type": self.model_type.currentText(),
                "version": self.model_version.text(),
                "architecture": {
                    "hidden_size": self.hidden_size.value(),
                    "num_layers": self.num_layers.value(),
                    "num_heads": self.num_heads.value(),
                    "ffn_size": self.ffn_size.value(),
                    "max_position": self.max_position.value(),
                    "vocab_size": self.vocab_size.value()
                },
                "training": {
                    "batch_size": self.batch_size.value(),
                    "learning_rate": self.learning_rate.value(),
                    "epochs": self.epochs.value(),
                    "warmup_steps": self.warmup_steps.value(),
                    "weight_decay": self.weight_decay.value(),
                    "gradient_clipping": self.gradient_clipping.value()
                },
                "advanced": {
                    "use_amp": self.use_amp.isChecked(),
                    "use_gradient_checkpointing": self.use_gradient_checkpointing.isChecked(),
                    "use_ema": self.use_ema.isChecked(),
                    "ema_decay": self.ema_decay.value(),
                    "custom_params": self.custom_params.toPlainText()
                }
            }
            
            # Save to file
            config_dir = Path("configs")
            config_dir.mkdir(exist_ok=True)
            
            config_file = config_dir / f"{config['name']}_config.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=4)
                
            QMessageBox.information(self, "Success", "Model configuration saved successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {str(e)}")
            
    def load_configuration(self, config_file: str):
        """Load model configuration from file"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                
            # Update basic configuration
            self.model_name.setText(config["name"])
            self.model_type.setCurrentText(config["model_type"])
            self.model_version.setText(config["version"])
            
            # Update architecture configuration
            arch_config = config["architecture"]
            self.hidden_size.setValue(arch_config["hidden_size"])
            self.num_layers.setValue(arch_config["num_layers"])
            self.num_heads.setValue(arch_config["num_heads"])
            self.ffn_size.setValue(arch_config["ffn_size"])
            self.max_position.setValue(arch_config["max_position"])
            self.vocab_size.setValue(arch_config["vocab_size"])
            
            # Update training configuration
            train_config = config["training"]
            self.batch_size.setValue(train_config["batch_size"])
            self.learning_rate.setValue(train_config["learning_rate"])
            self.epochs.setValue(train_config["epochs"])
            self.warmup_steps.setValue(train_config["warmup_steps"])
            self.weight_decay.setValue(train_config["weight_decay"])
            self.gradient_clipping.setValue(train_config["gradient_clipping"])
            
            # Update advanced configuration
            adv_config = config["advanced"]
            self.use_amp.setChecked(adv_config["use_amp"])
            self.use_gradient_checkpointing.setChecked(adv_config["use_gradient_checkpointing"])
            self.use_ema.setChecked(adv_config["use_ema"])
            self.ema_decay.setValue(adv_config["ema_decay"])
            self.custom_params.setPlainText(adv_config["custom_params"])
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load configuration: {str(e)}")
            
    def update_model_table(self, models: list):
        """Update the model table with current models"""
        self.model_table.setRowCount(len(models))
        
        for i, model in enumerate(models):
            # Name
            self.model_table.setItem(i, 0, QTableWidgetItem(model["name"]))
            
            # Type
            self.model_table.setItem(i, 1, QTableWidgetItem(model["type"]))
            
            # Size
            self.model_table.setItem(i, 2, QTableWidgetItem(str(model["size"])))
            
            # Status
            self.model_table.setItem(i, 3, QTableWidgetItem(model["status"]))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_button = QPushButton("Edit")
            edit_button.clicked.connect(lambda checked, m=model: self.edit_model(m))
            actions_layout.addWidget(edit_button)
            
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda checked, m=model: self.delete_model(m))
            actions_layout.addWidget(delete_button)
            
            self.model_table.setCellWidget(i, 4, actions_widget)
            
    def edit_model(self, model: Dict[str, Any]):
        """Edit a model configuration"""
        # TODO: Implement model editing
        pass
        
    def delete_model(self, model: Dict[str, Any]):
        """Delete a model"""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete model '{model['name']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # TODO: Implement model deletion
                QMessageBox.information(self, "Success", "Model deleted successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete model: {str(e)}")
                
    def show_add_model_dialog(self):
        """Show dialog for adding a new model"""
        # TODO: Implement add model dialog
        pass 