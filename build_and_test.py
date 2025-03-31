import os
import sys
import subprocess
from pathlib import Path

def build_and_test():
    print("Starting build and test process...")
    
    # 1. Build the executable
    print("\nStep 1: Building executable...")
    try:
        subprocess.run([sys.executable, "build.py"], check=True)
        print("Build completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        return False
    
    # 2. Run the tests
    print("\nStep 2: Running tests...")
    try:
        subprocess.run([sys.executable, "test_executable.py"], check=True)
        print("Tests completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Tests failed with error: {e}")
        return False
    
    # 3. Verify file structure
    print("\nStep 3: Verifying file structure...")
    required_files = [
        "modeltrainingmanager.exe",
        "config/config.yaml",
        "docs/trainingmanagertutorial.md",
        "docs/trainingmanagertutorial.html",
        "assets/icon.ico"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"Error: Required file {file_path} not found!")
            return False
    
    # 4. Verify mockups
    print("\nStep 4: Verifying mockups...")
    mockups_dir = Path("docs/mockups")
    if not mockups_dir.exists():
        print("Error: Mockups directory not found!")
        return False
    
    required_mockups = [
        "overview.png",
        "installation.png",
        "sidebar.png",
        "dashboard.png",
        "training_config.png",
        "dataset_management.png",
        "aws_config.png",
        "gcp_config.png",
        "monitoring.png",
        "training_progress.png",
        "resource_usage.png"
    ]
    
    for mockup in required_mockups:
        if not (mockups_dir / mockup).exists():
            print(f"Error: Required mockup {mockup} not found!")
            return False
    
    print("\nAll steps completed successfully!")
    return True

if __name__ == "__main__":
    success = build_and_test()
    sys.exit(0 if success else 1) 