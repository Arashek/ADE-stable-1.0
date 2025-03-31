import os
import sys
import subprocess
import shutil
from pathlib import Path
import winreg
import ctypes
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QProgressBar, QPushButton
from PyQt6.QtCore import Qt, QThread, pyqtSignal

class InstallerThread(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool)
    
    def __init__(self, install_dir):
        super().__init__()
        self.install_dir = install_dir
    
    def run(self):
        try:
            # Create installation directory
            self.status.emit("Creating installation directory...")
            os.makedirs(self.install_dir, exist_ok=True)
            self.progress.emit(10)
            
            # Copy program files
            self.status.emit("Copying program files...")
            src_dir = Path(__file__).parent
            for item in src_dir.glob("**/*"):
                if item.is_file() and not item.name.endswith(('.pyc', '.pyo')):
                    rel_path = item.relative_to(src_dir)
                    dst_path = self.install_dir / rel_path
                    os.makedirs(dst_path.parent, exist_ok=True)
                    shutil.copy2(item, dst_path)
            self.progress.emit(30)
            
            # Create virtual environment
            self.status.emit("Creating virtual environment...")
            venv_path = self.install_dir / "venv"
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
            self.progress.emit(50)
            
            # Install requirements
            self.status.emit("Installing requirements...")
            pip_path = venv_path / "Scripts" / "pip.exe"
            requirements_path = self.install_dir / "requirements.txt"
            subprocess.run([str(pip_path), "install", "-r", str(requirements_path)], check=True)
            self.progress.emit(70)
            
            # Create desktop shortcut
            self.status.emit("Creating desktop shortcut...")
            self._create_shortcut()
            self.progress.emit(90)
            
            # Register uninstaller
            self.status.emit("Registering uninstaller...")
            self._register_uninstaller()
            self.progress.emit(100)
            
            self.finished.emit(True)
            
        except Exception as e:
            self.status.emit(f"Installation failed: {str(e)}")
            self.finished.emit(False)
    
    def _create_shortcut(self):
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        shortcut_path = os.path.join(desktop, "ADE Training Manager.lnk")
        
        with open(shortcut_path, "w") as f:
            f.write(f"""[InternetShortcut]
URL=file:///{self.install_dir}/modeltrainingmanager.exe
IconFile={self.install_dir}/assets/icon.ico
IconIndex=0
""")
    
    def _register_uninstaller(self):
        uninstaller_path = self.install_dir / "uninstaller.exe"
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\ADE Training Manager") as key:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "ADE Training Manager")
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, str(uninstaller_path))
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(self.install_dir))

class InstallerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ADE Training Manager Installer")
        self.setFixedSize(400, 200)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Welcome message
        welcome_label = QLabel("Welcome to ADE Training Manager Installer")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcome_label)
        
        # Status label
        self.status_label = QLabel("Preparing installation...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # Install button
        self.install_button = QPushButton("Install")
        self.install_button.clicked.connect(self.start_installation)
        layout.addWidget(self.install_button)
        
        # Set default install directory
        self.install_dir = Path("D:/ADE Training Manager")
    
    def start_installation(self):
        self.install_button.setEnabled(False)
        self.installer_thread = InstallerThread(self.install_dir)
        self.installer_thread.progress.connect(self.update_progress)
        self.installer_thread.status.connect(self.update_status)
        self.installer_thread.finished.connect(self.installation_finished)
        self.installer_thread.start()
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
    
    def update_status(self, message):
        self.status_label.setText(message)
    
    def installation_finished(self, success):
        if success:
            self.status_label.setText("Installation completed successfully!")
            self.install_button.setText("Launch")
            self.install_button.setEnabled(True)
            self.install_button.clicked.disconnect()
            self.install_button.clicked.connect(self.launch_program)
        else:
            self.status_label.setText("Installation failed. Please check the error message above.")
            self.install_button.setText("Retry")
            self.install_button.setEnabled(True)
    
    def launch_program(self):
        program_path = self.install_dir / "modeltrainingmanager.exe"
        if program_path.exists():
            subprocess.Popen([str(program_path)])
            self.close()
        else:
            self.status_label.setText("Error: Program executable not found!")

def main():
    app = QApplication(sys.argv)
    window = InstallerWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 