import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                            QTextEdit, QComboBox, QListWidget, QMessageBox,
                            QSplitter, QFrame)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont

class MockupDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ADE Training Manager - Mockup")
        self.setMinimumSize(1200, 800)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Create left panel for dataset management
        left_panel = self.create_left_panel()
        
        # Create right panel for chat interface
        right_panel = self.create_right_panel()
        
        # Add panels to main layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter)
        
        # Set up mock data
        self.setup_mock_data()
        
    def create_left_panel(self):
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(panel)
        
        # GitHub Integration Section
        github_group = QFrame()
        github_group.setFrameStyle(QFrame.Shape.StyledPanel)
        github_layout = QVBoxLayout(github_group)
        
        github_label = QLabel("GitHub Integration")
        github_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        github_layout.addWidget(github_label)
        
        # Repository selection
        repo_layout = QHBoxLayout()
        repo_label = QLabel("Repository:")
        self.repo_combo = QComboBox()
        self.repo_combo.addItems(["Select Repository", "ade-platform", "model-training"])
        repo_layout.addWidget(repo_label)
        repo_layout.addWidget(self.repo_combo)
        github_layout.addLayout(repo_layout)
        
        # Branch selection
        branch_layout = QHBoxLayout()
        branch_label = QLabel("Branch:")
        self.branch_combo = QComboBox()
        self.branch_combo.addItems(["main", "develop", "feature/dataset"])
        branch_layout.addWidget(branch_label)
        branch_layout.addWidget(self.branch_combo)
        github_layout.addLayout(branch_layout)
        
        # Dataset Selection Section
        dataset_group = QFrame()
        dataset_group.setFrameStyle(QFrame.Shape.StyledPanel)
        dataset_layout = QVBoxLayout(dataset_group)
        
        dataset_label = QLabel("Dataset Selection")
        dataset_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        dataset_layout.addWidget(dataset_label)
        
        # Dataset list
        self.dataset_list = QListWidget()
        dataset_layout.addWidget(self.dataset_list)
        
        # Dataset actions
        dataset_actions = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_datasets)
        self.select_btn = QPushButton("Select Dataset")
        self.select_btn.clicked.connect(self.select_dataset)
        dataset_actions.addWidget(self.refresh_btn)
        dataset_actions.addWidget(self.select_btn)
        dataset_layout.addLayout(dataset_actions)
        
        # Add groups to main layout
        layout.addWidget(github_group)
        layout.addWidget(dataset_group)
        
        return panel
        
    def create_right_panel(self):
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(panel)
        
        # Chat Interface Section
        chat_label = QLabel("Dataset Creation Assistant")
        chat_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(chat_label)
        
        # Chat history
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        layout.addWidget(self.chat_history)
        
        # Chat input
        chat_input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask about dataset creation strategies...")
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_message)
        chat_input_layout.addWidget(self.chat_input)
        chat_input_layout.addWidget(self.send_btn)
        layout.addLayout(chat_input_layout)
        
        return panel
        
    def setup_mock_data(self):
        # Add mock datasets
        mock_datasets = [
            "training_data_v1.csv",
            "validation_data_v1.csv",
            "test_data_v1.csv",
            "augmented_dataset_v1.csv"
        ]
        self.dataset_list.addItems(mock_datasets)
        
        # Add welcome message to chat
        self.chat_history.append("Assistant: Welcome to the ADE Training Manager! I can help you with dataset creation strategies and management. How can I assist you today?")
        
    def refresh_datasets(self):
        self.dataset_list.clear()
        self.setup_mock_data()
        QMessageBox.information(self, "Refresh", "Dataset list refreshed!")
        
    def select_dataset(self):
        current_item = self.dataset_list.currentItem()
        if current_item:
            QMessageBox.information(self, "Selection", f"Selected dataset: {current_item.text()}")
        else:
            QMessageBox.warning(self, "Warning", "Please select a dataset first!")
            
    def send_message(self):
        message = self.chat_input.text().strip()
        if message:
            self.chat_history.append(f"You: {message}")
            # Mock response
            self.chat_history.append("Assistant: I understand you're asking about dataset creation. Here are some strategies you might consider:\n"
                                   "1. Data augmentation\n"
                                   "2. Synthetic data generation\n"
                                   "3. Active learning\n"
                                   "4. Transfer learning")
            self.chat_input.clear()

def main():
    app = QApplication(sys.argv)
    window = MockupDashboard()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 