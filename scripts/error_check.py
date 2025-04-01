#!/usr/bin/env python
"""
Comprehensive Error Checking Script for ADE Platform

This script performs systematic checks on both frontend and backend components
to identify and report issues that need to be fixed for local testing and
cloud deployment preparation.

Usage:
    python error_check.py [--frontend] [--backend] [--api-test]
"""

import os
import sys
import json
import argparse
import subprocess
import requests
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import time

# Constants
BACKEND_DIR = Path(__file__).parent.parent / "backend"
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
REPORT_DIR = Path(__file__).parent.parent / "diagnostics"
BACKEND_PORT = 8001
FRONTEND_PORT = 3001

# Ensure report directory exists
REPORT_DIR.mkdir(exist_ok=True)

# Setup logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(REPORT_DIR / "error_check.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("error_check")

class ErrorCheck:
    """Main error checking class"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        
    def run_all_checks(self, frontend: bool = True, backend: bool = True, api_test: bool = True) -> bool:
        """Run all error checks and return True if all checks pass"""
        success = True
        
        if backend:
            logger.info("Running backend checks...")
            if not self.check_backend_imports():
                success = False
            
            if not self.check_backend_dependencies():
                success = False
                
            if not self.check_backend_running():
                success = False
                logger.warning("Backend is not running - skipping API tests")
                api_test = False
        
        if frontend:
            logger.info("Running frontend checks...")
            if not self.check_frontend_typescript():
                success = False
                
            if not self.check_frontend_dependencies():
                success = False
                
            if not self.check_frontend_running():
                success = False
                logger.warning("Frontend is not running - skipping UI tests")
        
        if api_test and backend:
            logger.info("Running API tests...")
            if not self.test_backend_api_health():
                success = False
                
            if not self.test_owner_panel_endpoints():
                success = False
        
        # Generate report
        self.generate_report()
        
        return success
    
    def check_backend_imports(self) -> bool:
        """Check for import errors in backend Python code"""
        logger.info("Checking backend imports...")
        success = True
        
        # List of modules to check (add more as needed)
        modules_to_check = [
            "routes.owner_panel_routes",
            "routes.coordination_api",
            "services.owner_panel_service",
            "agents.specialized_agents.design_agent",
            "agents.specialized_agents.development_agent",
            "agents.agent_coordinator",
        ]
        
        for module in modules_to_check:
            cmd = f"cd {BACKEND_DIR} && python -c \"import {module}\""
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                error_msg = f"Import error in {module}: {result.stderr.strip()}"
                self.errors.append(("backend_import", error_msg))
                logger.error(error_msg)
                success = False
            else:
                self.info.append(("backend_import", f"Module {module} imports successfully"))
        
        return success
    
    def check_backend_dependencies(self) -> bool:
        """Check backend dependencies"""
        logger.info("Checking backend dependencies...")
        success = True
        
        # Check for required packages
        required_packages = [
            "fastapi",
            "uvicorn",
            "pydantic<2.0.0",  # Specific version needed
            "sqlalchemy",
            "pyjwt",
            "passlib",
        ]
        
        for package in required_packages:
            cmd = f"pip show {package.split('<')[0]}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                error_msg = f"Missing required package: {package}"
                self.errors.append(("backend_dependency", error_msg))
                logger.error(error_msg)
                success = False
            else:
                # Check version constraints if specified
                if "<" in package or ">" in package:
                    import re
                    package_name = package.split("<")[0].split(">")[0]
                    version_line = [line for line in result.stdout.split("\n") if line.startswith("Version: ")][0]
                    version = version_line.replace("Version: ", "").strip()
                    
                    # Simple version check - can be enhanced for more complex version specs
                    if "<" in package:
                        req_version = package.split("<")[1]
                        if version >= req_version:
                            error_msg = f"Package {package_name} version {version} does not satisfy {package}"
                            self.errors.append(("backend_dependency", error_msg))
                            logger.error(error_msg)
                            success = False
                
                self.info.append(("backend_dependency", f"Package {package.split('<')[0]} is installed"))
        
        return success
    
    def check_backend_running(self) -> bool:
        """Check if backend server is running"""
        logger.info(f"Checking if backend is running on port {BACKEND_PORT}...")
        
        try:
            response = requests.get(f"http://localhost:{BACKEND_PORT}/health", timeout=2)
            if response.status_code == 200:
                self.info.append(("backend_status", "Backend server is running"))
                return True
            else:
                error_msg = f"Backend server returned status code {response.status_code}"
                self.errors.append(("backend_status", error_msg))
                logger.error(error_msg)
                return False
        except requests.exceptions.ConnectionError:
            error_msg = f"Backend server is not running on port {BACKEND_PORT}"
            self.errors.append(("backend_status", error_msg))
            logger.error(error_msg)
            return False
        except Exception as e:
            error_msg = f"Error checking backend server: {str(e)}"
            self.errors.append(("backend_status", error_msg))
            logger.error(error_msg)
            return False
    
    def check_frontend_typescript(self) -> bool:
        """Check for TypeScript errors in frontend code"""
        logger.info("Checking frontend TypeScript...")
        success = True
        
        cmd = f"cd {FRONTEND_DIR} && npx tsc --noEmit"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            # Process and categorize TypeScript errors
            error_lines = result.stdout.strip().split("\n")
            ts_errors = []
            
            for line in error_lines:
                if "error TS" in line:
                    ts_errors.append(line.strip())
            
            if ts_errors:
                self.errors.append(("frontend_typescript", f"Found {len(ts_errors)} TypeScript errors"))
                logger.error(f"TypeScript check failed with {len(ts_errors)} errors")
                
                # Log first 10 errors for visibility
                for i, err in enumerate(ts_errors[:10]):
                    logger.error(f"TS Error {i+1}: {err}")
                
                success = False
            else:
                self.info.append(("frontend_typescript", "TypeScript check passed"))
        else:
            self.info.append(("frontend_typescript", "TypeScript check passed"))
        
        return success
    
    def check_frontend_dependencies(self) -> bool:
        """Check frontend dependencies"""
        logger.info("Checking frontend dependencies...")
        success = True
        
        # Check if node_modules exists
        node_modules_path = FRONTEND_DIR / "node_modules"
        if not node_modules_path.exists():
            error_msg = "Frontend dependencies not installed (node_modules missing)"
            self.errors.append(("frontend_dependency", error_msg))
            logger.error(error_msg)
            return False
        
        # Check package.json vs node_modules
        package_json_path = FRONTEND_DIR / "package.json"
        if not package_json_path.exists():
            error_msg = "package.json not found"
            self.errors.append(("frontend_dependency", error_msg))
            logger.error(error_msg)
            return False
        
        with open(package_json_path, 'r') as f:
            package_data = json.load(f)
            
        # Check for critical dependencies
        critical_deps = ["react", "react-dom", "typescript", "axios", "@mui/material"]
        for dep in critical_deps:
            dep_path = node_modules_path / dep
            if not dep_path.exists():
                error_msg = f"Critical dependency not installed: {dep}"
                self.errors.append(("frontend_dependency", error_msg))
                logger.error(error_msg)
                success = False
            else:
                self.info.append(("frontend_dependency", f"Dependency installed: {dep}"))
        
        return success
    
    def check_frontend_running(self) -> bool:
        """Check if frontend server is running"""
        logger.info(f"Checking if frontend is running on port {FRONTEND_PORT}...")
        
        try:
            response = requests.get(f"http://localhost:{FRONTEND_PORT}", timeout=2)
            if response.status_code == 200:
                self.info.append(("frontend_status", "Frontend server is running"))
                return True
            else:
                error_msg = f"Frontend server returned status code {response.status_code}"
                self.warnings.append(("frontend_status", error_msg))
                logger.warning(error_msg)
                return False
        except requests.exceptions.ConnectionError:
            error_msg = f"Frontend server is not running on port {FRONTEND_PORT}"
            self.warnings.append(("frontend_status", error_msg))
            logger.warning(error_msg)
            return False
        except Exception as e:
            error_msg = f"Error checking frontend server: {str(e)}"
            self.warnings.append(("frontend_status", error_msg))
            logger.warning(error_msg)
            return False
    
    def test_backend_api_health(self) -> bool:
        """Test backend API health endpoint"""
        logger.info("Testing backend API health endpoint...")
        
        try:
            response = requests.get(f"http://localhost:{BACKEND_PORT}/health", timeout=2)
            if response.status_code == 200:
                self.info.append(("api_health", "API health check passed"))
                return True
            else:
                error_msg = f"API health check failed with status code {response.status_code}"
                self.errors.append(("api_health", error_msg))
                logger.error(error_msg)
                return False
        except Exception as e:
            error_msg = f"API health check failed: {str(e)}"
            self.errors.append(("api_health", error_msg))
            logger.error(error_msg)
            return False
    
    def test_owner_panel_endpoints(self) -> bool:
        """Test Owner Panel API endpoints"""
        logger.info("Testing Owner Panel API endpoints...")
        success = True
        
        # Test endpoints - add authorization if needed
        endpoints = [
            "/api/owner-panel/health",
            "/api/owner-panel/metrics/summary",
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"http://localhost:{BACKEND_PORT}{endpoint}", timeout=2)
                
                # For now, we consider 401/403 as "working" since they require auth
                if response.status_code in [200, 401, 403]:
                    self.info.append(("owner_panel_api", f"Endpoint {endpoint} is accessible"))
                else:
                    error_msg = f"Endpoint {endpoint} returned unexpected status code {response.status_code}"
                    self.errors.append(("owner_panel_api", error_msg))
                    logger.error(error_msg)
                    success = False
            except Exception as e:
                error_msg = f"Error testing endpoint {endpoint}: {str(e)}"
                self.errors.append(("owner_panel_api", error_msg))
                logger.error(error_msg)
                success = False
        
        return success
    
    def generate_report(self) -> None:
        """Generate an error report file"""
        logger.info("Generating error report...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "summary": {
                "error_count": len(self.errors),
                "warning_count": len(self.warnings),
                "info_count": len(self.info),
                "status": "pass" if not self.errors else "fail"
            }
        }
        
        report_path = REPORT_DIR / f"error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Error report generated: {report_path}")
        
        # Generate HTML report for better readability
        html_report_path = report_path.with_suffix('.html')
        self._generate_html_report(report, html_report_path)
        
        logger.info(f"HTML report generated: {html_report_path}")
    
    def _generate_html_report(self, report: Dict[str, Any], output_path: Path) -> None:
        """Generate an HTML version of the error report"""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ADE Error Check Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }}
                h1, h2, h3 {{ color: #333; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .summary {{ display: flex; justify-content: space-between; background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .summary-item {{ text-align: center; }}
                .errors {{ background-color: #fff5f5; padding: 10px; border-left: 5px solid #dc3545; margin-bottom: 20px; }}
                .warnings {{ background-color: #fff3cd; padding: 10px; border-left: 5px solid #ffc107; margin-bottom: 20px; }}
                .info {{ background-color: #e9f5ff; padding: 10px; border-left: 5px solid #0d6efd; margin-bottom: 20px; }}
                .item {{ margin-bottom: 10px; padding: 10px; background-color: rgba(255, 255, 255, 0.7); border-radius: 3px; }}
                .timestamp {{ color: #6c757d; font-size: 0.9em; margin-bottom: 20px; }}
                .status-pass {{ color: #28a745; }}
                .status-fail {{ color: #dc3545; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>ADE Error Check Report</h1>
                <div class="timestamp">Generated on: {report['timestamp']}</div>
                
                <div class="summary">
                    <div class="summary-item">
                        <h3>Status</h3>
                        <p class="status-{report['summary']['status']}">
                            {report['summary']['status'].upper()}
                        </p>
                    </div>
                    <div class="summary-item">
                        <h3>Errors</h3>
                        <p>{report['summary']['error_count']}</p>
                    </div>
                    <div class="summary-item">
                        <h3>Warnings</h3>
                        <p>{report['summary']['warning_count']}</p>
                    </div>
                    <div class="summary-item">
                        <h3>Info</h3>
                        <p>{report['summary']['info_count']}</p>
                    </div>
                </div>
        """
        
        if report['errors']:
            html_content += """
                <div class="errors">
                    <h2>Errors</h2>
            """
            
            for category, message in report['errors']:
                html_content += f"""
                    <div class="item">
                        <strong>{category}:</strong> {message}
                    </div>
                """
            
            html_content += """
                </div>
            """
        
        if report['warnings']:
            html_content += """
                <div class="warnings">
                    <h2>Warnings</h2>
            """
            
            for category, message in report['warnings']:
                html_content += f"""
                    <div class="item">
                        <strong>{category}:</strong> {message}
                    </div>
                """
            
            html_content += """
                </div>
            """
        
        if report['info']:
            html_content += """
                <div class="info">
                    <h2>Information</h2>
            """
            
            for category, message in report['info']:
                html_content += f"""
                    <div class="item">
                        <strong>{category}:</strong> {message}
                    </div>
                """
            
            html_content += """
                </div>
            """
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        with open(output_path, 'w') as f:
            f.write(html_content)

def main():
    parser = argparse.ArgumentParser(description="ADE Platform Error Checking Script")
    parser.add_argument("--frontend", action="store_true", help="Run frontend checks only")
    parser.add_argument("--backend", action="store_true", help="Run backend checks only")
    parser.add_argument("--api-test", action="store_true", help="Run API tests")
    args = parser.parse_args()
    
    # Default: run all checks if no specific flags are provided
    run_frontend = args.frontend or not (args.frontend or args.backend or args.api_test)
    run_backend = args.backend or not (args.frontend or args.backend or args.api_test)
    run_api_test = args.api_test or not (args.frontend or args.backend or args.api_test)
    
    checker = ErrorCheck()
    success = checker.run_all_checks(
        frontend=run_frontend,
        backend=run_backend,
        api_test=run_api_test
    )
    
    if success:
        logger.info("All checks passed successfully!")
        return 0
    else:
        logger.error("Checks completed with errors. See report for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
