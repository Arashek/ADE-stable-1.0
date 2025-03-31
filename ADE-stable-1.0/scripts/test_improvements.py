import os
import sys
from pathlib import Path

def setup_environment():
    """Set up the Python environment for testing"""
    # Add the project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.append(str(project_root))
    
    # Set environment variables
    os.environ["ADE_PROJECT_DIR"] = str(project_root)
    os.environ["PYTHONPATH"] = str(project_root)

def main():
    """Main entry point"""
    try:
        # Set up environment
        setup_environment()
        
        # Import and run the test interface
        from src.tools.self_improvement.test_interface import main as run_interface
        run_interface()
        
    except Exception as e:
        print(f"Error launching test interface: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 