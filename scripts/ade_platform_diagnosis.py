#!/usr/bin/env python
"""
ADE Platform Comprehensive Diagnosis Tool

This script performs a thorough diagnosis of the entire ADE platform,
focusing on critical components needed for local testing and cloud deployment.
It identifies issues, provides solutions, and can automatically fix common problems.
"""

import os
import sys
import subprocess
import importlib
import logging
import json
import re
import time
import pkg_resources
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("ade_diagnosis.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ade_diagnosis")

class ADEDiagnosisTool:
    """Comprehensive diagnosis tool for the ADE platform"""

    def __init__(self, auto_fix=False):
        """Initialize the diagnosis tool"""
        self.project_root = Path(__file__).parent.parent
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.auto_fix = auto_fix
        
        # Initialize issue trackers
        self.issues = {
            "backend": [],
            "frontend": [],
            "system": []
        }
        
        # Store fix functions
        self.fix_functions = {
            "missing_init": self.fix_missing_init_files,
            "import_error": self.fix_import_errors,
            "dependency_missing": self.fix_missing_dependency,
            "wrong_dependency_version": self.fix_dependency_version,
            "frontend_dependency": self.fix_frontend_dependency,
            "missing_critical_file": self.fix_missing_critical_file
        }

    def print_header(self, title):
        """Print a formatted header"""
        print("\n" + "=" * 80)
        print(f" {title} ".center(80, "="))
        print("=" * 80)

    def run_command(self, command, cwd=None, capture_output=True):
        """Run a command and capture its output"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or self.project_root,
                capture_output=capture_output,
                text=True
            )
            return result
        except Exception as e:
            logger.error(f"Error running command '{command}': {str(e)}")
            return None

    def check_backend_structure(self):
        """Check backend directory structure"""
        self.print_header("CHECKING BACKEND STRUCTURE")
        
        # Check critical directories
        critical_dirs = [
            "agents",
            "agents/specialized_agents",
            "routes",
            "services",
            "services/coordination",
            "utils"
        ]
        
        for dir_path in critical_dirs:
            full_path = self.backend_dir / dir_path
            if not full_path.exists():
                logger.warning(f"Missing critical directory: {dir_path}")
                self.issues["backend"].append({
                    "type": "missing_directory",
                    "path": str(full_path),
                    "severity": "high"
                })
            else:
                logger.info(f"✓ Found directory: {dir_path}")
        
        # Check for __init__.py files
        for root, dirs, files in os.walk(self.backend_dir):
            if "__pycache__" in root:
                continue
                
            rel_path = os.path.relpath(root, self.backend_dir)
            if rel_path == ".":
                rel_path = ""
                
            init_path = os.path.join(root, "__init__.py")
            if not os.path.exists(init_path):
                logger.warning(f"Missing __init__.py in: {rel_path}")
                self.issues["backend"].append({
                    "type": "missing_init",
                    "path": init_path,
                    "severity": "medium"
                })
    
    def check_critical_files(self):
        """Check for critical files in the codebase"""
        self.print_header("CHECKING CRITICAL FILES")
        
        # Critical backend files
        critical_files = [
            "backend/main.py",
            "backend/agents/agent_coordinator.py",
            "backend/agents/base_agent.py",
            "backend/services/coordination/agent_interface.py",
            "backend/services/coordination/agent_coordinator.py",
            "backend/routes/coordination_api.py",
            "backend/utils/error_logging.py",
            "frontend/src/App.tsx",
            "frontend/src/components/agents/CoordinationSystem.tsx",
            "frontend/src/services/api.ts"
        ]
        
        for file_path in critical_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                logger.warning(f"Missing critical file: {file_path}")
                self.issues["system"].append({
                    "type": "missing_critical_file",
                    "path": str(full_path),
                    "severity": "high",
                    "component": file_path.split("/")[0]
                })
            else:
                logger.info(f"✓ Found critical file: {file_path}")
    
    def check_backend_imports(self):
        """Check backend imports"""
        self.print_header("CHECKING BACKEND IMPORTS")
        
        # Create a simplified import test script
        temp_script = self.project_root / "temp_import_check.py"
        
        # Critical modules to check
        critical_modules = [
            "backend.main",
            "backend.agents.agent_coordinator",
            "backend.services.coordination.agent_interface",
            "backend.routes.coordination_api",
            "backend.utils.error_logging"
        ]
        
        for module in critical_modules:
            logger.info(f"Checking import for: {module}")
            
            import_script = f"""
import sys
sys.path.insert(0, '{str(self.project_root)}')
try:
    import {module}
    print("SUCCESS: Module imported successfully")
except Exception as e:
    print(f"ERROR: {{type(e).__name__}}: {{str(e)}}")
"""
            
            with open(temp_script, "w") as f:
                f.write(import_script)
            
            result = self.run_command(f"python {temp_script}")
            
            if result and "SUCCESS" in result.stdout:
                logger.info(f"✓ Module {module} imported successfully")
            else:
                error_msg = result.stdout.strip() if result else "Unknown error"
                logger.warning(f"✗ Import error for {module}: {error_msg}")
                
                # Extract error type
                error_match = re.search(r"ERROR: ([^:]+):", error_msg)
                error_type = error_match.group(1) if error_match else "Unknown"
                
                self.issues["backend"].append({
                    "type": "import_error",
                    "module": module,
                    "error_type": error_type,
                    "error_msg": error_msg,
                    "severity": "high"
                })
        
        # Clean up
        if temp_script.exists():
            temp_script.unlink()
    
    def check_backend_dependencies(self):
        """Check backend dependencies"""
        self.print_header("CHECKING BACKEND DEPENDENCIES")
        
        # Critical dependencies
        critical_deps = {
            "fastapi": ">=0.68.0,<0.70.0",
            "uvicorn": ">=0.15.0,<0.16.0",
            "pydantic": ">=1.8.0,<1.10.0",
            "python-multipart": ">=0.0.5",
            "aiofiles": ">=0.7.0",
            "openai": ">=0.27.0",
            "python-dotenv": ">=0.19.0"
        }
        
        for dep, version_spec in critical_deps.items():
            try:
                # Check if dependency is installed
                pkg_resources.get_distribution(dep)
                
                # Get installed version
                result = self.run_command(f"pip freeze | grep -i {dep}")
                if result and result.stdout:
                    installed_version = result.stdout.strip()
                    logger.info(f"✓ Dependency {dep}: {installed_version}")
                else:
                    logger.info(f"✓ Dependency {dep} is installed")
            except pkg_resources.DistributionNotFound:
                logger.warning(f"✗ Missing dependency: {dep}")
                self.issues["backend"].append({
                    "type": "dependency_missing",
                    "dependency": dep,
                    "required_version": version_spec,
                    "severity": "high"
                })
    
    def check_frontend_dependencies(self):
        """Check frontend dependencies"""
        self.print_header("CHECKING FRONTEND DEPENDENCIES")
        
        # Critical frontend dependencies
        critical_deps = [
            "react",
            "react-dom",
            "typescript",
            "axios",
            "react-syntax-highlighter",
            "react-markdown",
            "@mui/material",
            "@emotion/react",
            "@emotion/styled"
        ]
        
        for dep in critical_deps:
            result = self.run_command(f"npm list {dep} --depth=0", cwd=self.frontend_dir)
            
            if result and result.returncode == 0:
                logger.info(f"✓ Dependency {dep} is installed")
            else:
                logger.warning(f"✗ Missing dependency: {dep}")
                self.issues["frontend"].append({
                    "type": "frontend_dependency",
                    "dependency": dep,
                    "severity": "high"
                })
    
    def check_server_connection(self):
        """Check if servers are running and accessible"""
        self.print_header("CHECKING SERVER CONNECTIONS")
        
        # Check backend server
        backend_result = self.run_command("netstat -ano | findstr :8000")
        if backend_result and "LISTENING" in backend_result.stdout:
            logger.info(f"✓ Backend server is running on port 8000")
            
            # Try to connect to health endpoint
            health_script = """
import requests
try:
    response = requests.get('http://localhost:8000/health', timeout=5)
    print(f"STATUS: {response.status_code}")
    print(f"CONTENT: {response.text[:100]}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {str(e)}")
"""
            temp_script = self.project_root / "temp_health_check.py"
            with open(temp_script, "w") as f:
                f.write(health_script)
            
            health_result = self.run_command(f"python {temp_script}")
            
            if health_result and "STATUS: 200" in health_result.stdout:
                logger.info(f"✓ Backend health endpoint is accessible")
            else:
                error_msg = health_result.stdout.strip() if health_result else "Unknown error"
                logger.warning(f"✗ Backend health endpoint is not accessible: {error_msg}")
                self.issues["backend"].append({
                    "type": "server_connection",
                    "port": 8000,
                    "error_msg": error_msg,
                    "severity": "high"
                })
            
            # Clean up
            if temp_script.exists():
                temp_script.unlink()
        else:
            logger.warning(f"✗ Backend server is not running on port 8000")
            self.issues["backend"].append({
                "type": "server_not_running",
                "port": 8000,
                "severity": "high"
            })
        
        # Check frontend server
        frontend_result = self.run_command("netstat -ano | findstr :3000")
        if frontend_result and "LISTENING" in frontend_result.stdout:
            logger.info(f"✓ Frontend server is running on port 3000")
        else:
            logger.warning(f"✗ Frontend server is not running on port 3000")
            self.issues["frontend"].append({
                "type": "server_not_running",
                "port": 3000,
                "severity": "high"
            })
    
    def fix_missing_init_files(self, issue):
        """Fix missing __init__.py files"""
        path = issue["path"]
        logger.info(f"Creating missing __init__.py at {path}")
        
        try:
            # Make sure directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Create the __init__.py file
            with open(path, "w") as f:
                f.write("# Auto-generated __init__.py\n")
            
            return True
        except Exception as e:
            logger.error(f"Failed to create __init__.py at {path}: {str(e)}")
            return False
    
    def fix_import_errors(self, issue):
        """Fix import errors"""
        module = issue["module"]
        error_type = issue["error_type"]
        
        if error_type == "ModuleNotFoundError":
            # Extract the missing module
            error_msg = issue["error_msg"]
            missing_module_match = re.search(r"No module named '([^']+)'", error_msg)
            
            if missing_module_match:
                missing_module = missing_module_match.group(1)
                
                # Check if it's a local module
                if missing_module.startswith("backend."):
                    # Create missing __init__.py files
                    module_path = missing_module.replace(".", "/")
                    path = self.project_root / module_path
                    
                    if not path.exists():
                        logger.info(f"Creating missing module directory: {module_path}")
                        os.makedirs(path, exist_ok=True)
                    
                    # Create __init__.py
                    init_file = path / "__init__.py"
                    if not init_file.exists():
                        with open(init_file, "w") as f:
                            f.write("# Auto-generated __init__.py\n")
                    
                    return True
                else:
                    # It's an external dependency
                    logger.info(f"Installing missing dependency: {missing_module}")
                    result = self.run_command(f"pip install {missing_module}")
                    return result.returncode == 0 if result else False
        
        return False
    
    def fix_missing_dependency(self, issue):
        """Fix missing dependency"""
        dependency = issue["dependency"]
        version = issue["required_version"]
        
        logger.info(f"Installing missing dependency: {dependency} {version}")
        result = self.run_command(f"pip install '{dependency}{version}'")
        
        return result.returncode == 0 if result else False
    
    def fix_dependency_version(self, issue):
        """Fix dependency version"""
        dependency = issue["dependency"]
        required_version = issue["required_version"]
        
        logger.info(f"Updating dependency {dependency} to {required_version}")
        result = self.run_command(f"pip install '{dependency}{required_version}' --force-reinstall")
        
        return result.returncode == 0 if result else False
    
    def fix_frontend_dependency(self, issue):
        """Fix frontend dependency"""
        dependency = issue["dependency"]
        
        logger.info(f"Installing frontend dependency: {dependency}")
        result = self.run_command(f"npm install {dependency} --save", cwd=self.frontend_dir)
        
        return result.returncode == 0 if result else False
    
    def fix_missing_critical_file(self, issue):
        """Fix missing critical file"""
        path = issue["path"]
        component = issue["component"]
        
        # We can only automatically fix certain files
        file_name = os.path.basename(path)
        
        if file_name == "__init__.py":
            logger.info(f"Creating missing __init__.py at {path}")
            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w") as f:
                    f.write("# Auto-generated __init__.py\n")
                return True
            except Exception as e:
                logger.error(f"Failed to create {path}: {str(e)}")
                return False
        else:
            logger.warning(f"Cannot automatically create {file_name}. Manual intervention required.")
            return False
    
    def fix_issues(self):
        """Fix identified issues"""
        self.print_header("FIXING ISSUES")
        
        # Sort issues by severity
        all_issues = []
        for category, issues in self.issues.items():
            for issue in issues:
                issue["category"] = category
                all_issues.append(issue)
        
        # Sort by severity (high first)
        all_issues.sort(key=lambda x: 0 if x["severity"] == "high" else 1 if x["severity"] == "medium" else 2)
        
        # Fix issues
        fixed_count = 0
        for issue in all_issues:
            issue_type = issue["type"]
            
            if issue_type in self.fix_functions:
                logger.info(f"Attempting to fix {issue_type} issue in {issue['category']}")
                if self.fix_functions[issue_type](issue):
                    logger.info(f"✓ Successfully fixed issue")
                    fixed_count += 1
                else:
                    logger.warning(f"✗ Failed to fix issue")
            else:
                logger.warning(f"No fix available for issue type: {issue_type}")
        
        return fixed_count
    
    def generate_report(self):
        """Generate a comprehensive report"""
        self.print_header("DIAGNOSIS REPORT")
        
        # Count issues by severity
        high_count = sum(1 for category in self.issues.values() 
                         for issue in category if issue["severity"] == "high")
        medium_count = sum(1 for category in self.issues.values() 
                           for issue in category if issue["severity"] == "medium")
        low_count = sum(1 for category in self.issues.values() 
                        for issue in category if issue["severity"] == "low")
        
        total_count = high_count + medium_count + low_count
        
        # Print summary
        print(f"\nFound {total_count} issues:")
        print(f"  - High severity: {high_count}")
        print(f"  - Medium severity: {medium_count}")
        print(f"  - Low severity: {low_count}")
        
        # Print high severity issues
        if high_count > 0:
            print("\nHigh Severity Issues:")
            for category, issues in self.issues.items():
                high_issues = [issue for issue in issues if issue["severity"] == "high"]
                if high_issues:
                    print(f"  {category.upper()}:")
                    for issue in high_issues:
                        print(f"    - {issue['type']}: {issue.get('error_msg', '')}")
        
        # Save report to file
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_issues": total_count,
            "high_severity": high_count,
            "medium_severity": medium_count,
            "low_severity": low_count,
            "issues": self.issues
        }
        
        with open("ade_diagnosis_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\nDetailed report saved to: ade_diagnosis_report.json")
        
        # Recommendations
        if total_count > 0:
            print("\nRecommendations:")
            
            if any(issue["type"] == "missing_init" for issue in self.issues["backend"]):
                print("  1. Fix missing __init__.py files to resolve import errors")
            
            if any(issue["type"] == "import_error" for issue in self.issues["backend"]):
                print("  2. Resolve backend import errors in critical modules")
            
            if any(issue["type"] == "dependency_missing" for issue in self.issues["backend"]):
                print("  3. Install missing backend dependencies")
            
            if any(issue["type"] == "frontend_dependency" for issue in self.issues["frontend"]):
                print("  4. Install missing frontend dependencies")
            
            if any(issue["type"] == "server_not_running" for issue in self.issues["backend"] + self.issues["frontend"]):
                print("  5. Start the backend and frontend servers")
        else:
            print("\nNo issues found. The ADE platform should be running correctly!")
    
    def run_diagnosis(self):
        """Run the complete diagnosis"""
        self.print_header("ADE PLATFORM DIAGNOSIS")
        
        # Step 1: Check directory structure
        self.check_backend_structure()
        
        # Step 2: Check critical files
        self.check_critical_files()
        
        # Step 3: Check imports
        self.check_backend_imports()
        
        # Step 4: Check dependencies
        self.check_backend_dependencies()
        self.check_frontend_dependencies()
        
        # Step 5: Check server connections
        self.check_server_connection()
        
        # Step 6: Generate report
        self.generate_report()
        
        # Step 7: Fix issues if auto_fix is enabled
        if self.auto_fix:
            fixed_count = self.fix_issues()
            print(f"\nAutomatically fixed {fixed_count} issues")
            
            if fixed_count > 0:
                print("\nRe-running diagnosis to verify fixes...")
                
                # Clear issues
                self.issues = {
                    "backend": [],
                    "frontend": [],
                    "system": []
                }
                
                # Re-run checks
                self.check_backend_structure()
                self.check_critical_files()
                self.check_backend_imports()
                self.check_backend_dependencies()
                self.check_frontend_dependencies()
                self.check_server_connection()
                
                # Generate updated report
                self.generate_report()

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ADE Platform Diagnosis Tool")
    parser.add_argument("--auto-fix", action="store_true", help="Automatically fix issues when possible")
    args = parser.parse_args()
    
    diagnosis = ADEDiagnosisTool(auto_fix=args.auto_fix)
    diagnosis.run_diagnosis()

if __name__ == "__main__":
    main()
