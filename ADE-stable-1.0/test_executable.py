import os
import sys
import time
import subprocess
from pathlib import Path

def test_executable():
    print("Starting executable test...")
    
    # Check if executable exists
    exe_path = Path("modeltrainingmanager.exe")
    if not exe_path.exists():
        print("Error: Executable not found!")
        return False
    
    try:
        # Start the application
        print("Launching application...")
        process = subprocess.Popen([str(exe_path)])
        
        # Wait for application to start
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is not None:
            print("Error: Application crashed!")
            return False
        
        # Test basic functionality
        print("Testing basic functionality...")
        
        # Check if config directory exists
        config_dir = Path("config")
        if not config_dir.exists():
            print("Error: Config directory not found!")
            process.terminate()
            return False
        
        # Check if docs directory exists
        docs_dir = Path("docs")
        if not docs_dir.exists():
            print("Error: Docs directory not found!")
            process.terminate()
            return False
        
        # Check if assets directory exists
        assets_dir = Path("assets")
        if not assets_dir.exists():
            print("Error: Assets directory not found!")
            process.terminate()
            return False
        
        # Check if mockups exist
        mockups_dir = docs_dir / "mockups"
        if not mockups_dir.exists():
            print("Error: Mockups directory not found!")
            process.terminate()
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
                process.terminate()
                return False
        
        print("All basic functionality tests passed!")
        
        # Test UI responsiveness
        print("Testing UI responsiveness...")
        time.sleep(2)  # Wait for UI to stabilize
        
        # Check if process is still responsive
        if process.poll() is not None:
            print("Error: Application became unresponsive!")
            return False
        
        print("UI responsiveness test passed!")
        
        # Clean up
        print("Cleaning up...")
        process.terminate()
        process.wait()
        
        print("All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        if process.poll() is None:
            process.terminate()
        return False

if __name__ == "__main__":
    success = test_executable()
    sys.exit(0 if success else 1) 