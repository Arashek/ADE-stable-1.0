#!/usr/bin/env python
"""
Error Tracking Script for ADE Platform

This script systematically tracks and logs errors across the ADE platform,
focusing on critical components for local testing and the Agent Coordination System.
"""

import os
import sys
import subprocess
import json
import re
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("error_tracking.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("error_tracker")

class ErrorTracker:
    """Error tracker for the ADE platform"""
    
    def __init__(self):
        """Initialize the error tracker"""
        self.project_root = Path(__file__).parent.parent
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.errors = {
            "backend": [],
            "frontend": [],
            "system": []
        }
    
    def print_header(self, title):
        """Print a formatted header"""
        logger.info("\n" + "=" * 80)
        logger.info(f" {title} ".center(80, "="))
        logger.info("=" * 80)
    
    def run_command(self, command, cwd=None, capture_output=True):
        """Run a shell command and return the result"""
        logger.info(f"Running: {command}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or self.project_root,
                capture_output=capture_output,
                text=True
            )
            if capture_output:
                if result.stdout:
                    logger.debug(f"STDOUT: {result.stdout[:500]}")
                if result.stderr:
                    logger.debug(f"STDERR: {result.stderr[:500]}")
            return result
        except Exception as e:
            logger.error(f"Error running command: {str(e)}")
            return None
    
    def check_backend_imports(self):
        """Check for import errors in the backend"""
        self.print_header("CHECKING BACKEND IMPORTS")
        
        # Critical modules to check
        critical_modules = [
            "agents.agent_coordinator",
            "agents.specialized_agents.design_agent",
            "agents.specialized_agents.development_agent",
            "routes.coordination_api",
            "services.coordination.agent_interface"
        ]
        
        for module in critical_modules:
            logger.info(f"Checking import for: {module}")
            
            # Create a simple script to import the module
            temp_script = self.project_root / "temp_import_check.py"
            with open(temp_script, "w") as f:
                f.write(f"""
import sys
sys.path.insert(0, '{str(self.backend_dir)}')
try:
    import {module}
    print(f"SUCCESS: Module {module} imported successfully")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {str(e)}")
""")
            
            # Run the script
            result = self.run_command(f"python {temp_script}")
            
            if result and result.returncode == 0:
                if "ERROR:" in result.stdout:
                    error = result.stdout.strip()
                    logger.error(error)
                    self.errors["backend"].append({
                        "module": module,
                        "error": error,
                        "type": "import",
                        "priority": "high" if "agent" in module else "medium"
                    })
                else:
                    logger.info(f"✓ Module {module} imported successfully")
            else:
                logger.error(f"Failed to check import for {module}")
            
            # Clean up temp script
            if temp_script.exists():
                temp_script.unlink()
    
    def check_backend_api(self):
        """Check if backend API endpoints are accessible"""
        self.print_header("CHECKING BACKEND API")
        
        # Check if server is running
        result = self.run_command("netstat -ano | findstr :8000")
        if not result or "LISTENING" not in result.stdout:
            logger.warning("Backend server is not running on port 8000")
            self.errors["system"].append({
                "component": "backend_server",
                "error": "Backend server is not running on port 8000",
                "type": "server",
                "priority": "high"
            })
            return
        
        # Test endpoints
        endpoints = [
            {"url": "http://localhost:8000/health", "priority": "medium"},
            {"url": "http://localhost:8000/api/coordination/status", "priority": "high"}
        ]
        
        # Create a simple script to test endpoints
        temp_script = self.project_root / "temp_api_check.py"
        with open(temp_script, "w") as f:
            f.write("""
import sys
import requests

def check_endpoint(url):
    try:
        response = requests.get(url, timeout=5)
        return {
            "status_code": response.status_code,
            "content": response.text,
            "error": None
        }
    except Exception as e:
        return {
            "status_code": None,
            "content": None,
            "error": f"{type(e).__name__}: {str(e)}"
        }

if __name__ == "__main__":
    url = sys.argv[1]
    result = check_endpoint(url)
    print(f"STATUS_CODE: {result['status_code']}")
    if result["error"]:
        print(f"ERROR: {result['error']}")
    else:
        print(f"CONTENT: {result['content'][:100]}")
""")
        
        for endpoint in endpoints:
            logger.info(f"Testing endpoint: {endpoint['url']}")
            
            result = self.run_command(f"python {temp_script} {endpoint['url']}")
            
            if result and result.returncode == 0:
                if "ERROR:" in result.stdout:
                    error = re.search(r"ERROR: (.*)", result.stdout).group(1)
                    logger.error(f"Failed to access {endpoint['url']}: {error}")
                    self.errors["backend"].append({
                        "endpoint": endpoint['url'],
                        "error": error,
                        "type": "api",
                        "priority": endpoint['priority']
                    })
                else:
                    status_code = re.search(r"STATUS_CODE: (.*)", result.stdout).group(1)
                    if status_code == "200":
                        logger.info(f"✓ Endpoint {endpoint['url']} is accessible")
                    else:
                        logger.error(f"Endpoint {endpoint['url']} returned status {status_code}")
                        self.errors["backend"].append({
                            "endpoint": endpoint['url'],
                            "error": f"Unexpected status code: {status_code}",
                            "type": "api",
                            "priority": endpoint['priority']
                        })
            else:
                logger.error(f"Failed to test endpoint {endpoint['url']}")
        
        # Clean up temp script
        if temp_script.exists():
            temp_script.unlink()
    
    def check_frontend_dependencies(self):
        """Check for missing frontend dependencies"""
        self.print_header("CHECKING FRONTEND DEPENDENCIES")
        
        # Critical dependencies to check
        critical_dependencies = [
            "react-syntax-highlighter",
            "react-markdown",
            "@types/react-syntax-highlighter",
            "axios"
        ]
        
        for dep in critical_dependencies:
            logger.info(f"Checking dependency: {dep}")
            
            result = self.run_command(f"npm list {dep}", cwd=self.frontend_dir)
            
            if result and result.returncode != 0:
                logger.error(f"Missing dependency: {dep}")
                self.errors["frontend"].append({
                    "dependency": dep,
                    "error": f"Missing dependency: {dep}",
                    "type": "dependency",
                    "priority": "high"
                })
            else:
                logger.info(f"✓ Dependency {dep} is installed")
    
    def check_frontend_typescript(self):
        """Check for TypeScript errors in frontend"""
        self.print_header("CHECKING FRONTEND TYPESCRIPT")
        
        result = self.run_command("npx tsc --noEmit", cwd=self.frontend_dir)
        
        if result and result.returncode != 0:
            # Parse TypeScript errors
            error_pattern = r"(.*?)\((\d+),(\d+)\): error (TS\d+): (.*)"
            matches = re.finditer(error_pattern, result.stdout)
            
            for match in matches:
                file, line, column, code, message = match.groups()
                error = {
                    "file": file,
                    "line": line,
                    "column": column,
                    "code": code,
                    "message": message,
                    "type": "typescript",
                    "priority": "high" if "agent" in file.lower() else "medium"
                }
                logger.error(f"TypeScript error in {file}:{line} - {code}: {message}")
                self.errors["frontend"].append(error)
        else:
            logger.info("✓ No TypeScript errors found")
    
    def check_coordination_system(self):
        """Check the coordination system specifically"""
        self.print_header("CHECKING COORDINATION SYSTEM")
        
        # Key files for coordination system
        key_files = [
            "backend/agents/agent_coordinator.py",
            "backend/routes/coordination_api.py",
            "backend/services/coordination/agent_interface.py",
            "frontend/src/components/agents/CoordinationSystem.tsx"
        ]
        
        for file_path in key_files:
            full_path = self.project_root / file_path
            
            if not full_path.exists():
                logger.error(f"Missing critical file: {file_path}")
                self.errors["system"].append({
                    "file": file_path,
                    "error": f"Missing critical file: {file_path}",
                    "type": "file",
                    "priority": "high"
                })
            else:
                logger.info(f"✓ Found critical file: {file_path}")
    
    def generate_report(self):
        """Generate a report of all errors"""
        self.print_header("ERROR REPORT")
        
        # Count errors by category and priority
        counts = {
            "backend": {"high": 0, "medium": 0, "low": 0},
            "frontend": {"high": 0, "medium": 0, "low": 0},
            "system": {"high": 0, "medium": 0, "low": 0}
        }
        
        for category, errors in self.errors.items():
            for error in errors:
                priority = error.get("priority", "medium")
                counts[category][priority] += 1
        
        # Print summary
        logger.info("\nError Summary:")
        for category, priorities in counts.items():
            total = sum(priorities.values())
            if total > 0:
                logger.info(f"- {category.upper()}: {total} errors " +
                          f"(High: {priorities['high']}, Medium: {priorities['medium']}, Low: {priorities['low']})")
            else:
                logger.info(f"- {category.upper()}: No errors")
        
        # Print high priority errors
        if any(counts[cat]["high"] > 0 for cat in counts):
            logger.info("\nHigh Priority Errors:")
            for category, errors in self.errors.items():
                high_errors = [e for e in errors if e.get("priority", "medium") == "high"]
                for i, error in enumerate(high_errors):
                    logger.info(f"[{category.upper()}] {i+1}. {error.get('error', 'Unknown error')}")
        
        # Write detailed report to file
        report_file = self.project_root / "error_report.json"
        with open(report_file, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": counts,
                "errors": self.errors
            }, f, indent=2)
        
        logger.info(f"\nDetailed error report written to: {report_file}")
    
    def run_all_checks(self):
        """Run all error checks"""
        self.print_header("RUNNING ALL ERROR CHECKS")
        
        self.check_backend_imports()
        self.check_backend_api()
        self.check_frontend_dependencies()
        self.check_frontend_typescript()
        self.check_coordination_system()
        
        self.generate_report()
        
        # Provide recommendations
        self.print_header("RECOMMENDATIONS")
        
        high_backend = sum(1 for e in self.errors["backend"] if e.get("priority", "medium") == "high")
        high_frontend = sum(1 for e in self.errors["frontend"] if e.get("priority", "medium") == "high")
        high_system = sum(1 for e in self.errors["system"] if e.get("priority", "medium") == "high")
        
        if high_backend + high_frontend + high_system == 0:
            logger.info("✓ No high priority errors found. You're on the right track!")
        else:
            if high_backend > 0:
                logger.info("1. Fix backend import errors to ensure the Agent Coordination System can initialize.")
            if high_system > 0:
                logger.info("2. Address missing critical files for the coordination system.")
            if high_frontend > 0:
                logger.info("3. Resolve frontend TypeScript errors, especially in agent-related components.")
        
        logger.info("\nTo start working with the system:")
        logger.info("1. Run the backend server: python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000")
        logger.info("2. Run the frontend: cd frontend && npm start")

def main():
    """Main function"""
    tracker = ErrorTracker()
    tracker.run_all_checks()

if __name__ == "__main__":
    main()
