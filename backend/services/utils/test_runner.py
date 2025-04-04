from typing import Dict, List, Optional, Any
import logging
import os
import subprocess
import sys
import tempfile
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class TestRunner:
    """Utility class for running tests on generated code"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.results_history = []
    
    async def run_tests(self, project_path: str, test_path: Optional[str] = None) -> Dict[str, Any]:
        """Run tests for a project and return results
        
        Args:
            project_path: Path to the project root
            test_path: Optional specific test path to run
            
        Returns:
            Dictionary with test results
        """
        self.logger.info(f"Running tests for project at: {project_path}")
        
        if not os.path.exists(project_path):
            self.logger.error(f"Project path does not exist: {project_path}")
            return {"success": False, "error": "Project path does not exist"}
        
        result = {
            "success": False,
            "framework": "unknown",
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0,
            "test_files_run": [],
            "failures": [],
            "execution_time_ms": 0,
            "output": ""
        }
        
        try:
            # Detect test framework
            framework = self._detect_test_framework(project_path)
            result["framework"] = framework
            
            # Run appropriate test command
            if framework == "pytest":
                test_result = self._run_pytest(project_path, test_path)
            elif framework == "jest":
                test_result = self._run_jest(project_path, test_path)
            elif framework == "unittest":
                test_result = self._run_unittest(project_path, test_path)
            else:
                self.logger.warning(f"Unsupported test framework: {framework}")
                return {"success": False, "error": f"Unsupported test framework: {framework}"}
            
            # Update result with test output
            result.update(test_result)
            
            # Store in history
            self.results_history.append(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error running tests: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _detect_test_framework(self, project_path: str) -> str:
        """Detect which test framework is used in the project"""
        # Check for pytest
        if os.path.exists(os.path.join(project_path, "pytest.ini")) or \
           os.path.exists(os.path.join(project_path, "conftest.py")):
            return "pytest"
            
        # Check for Jest (Node.js)
        package_json = os.path.join(project_path, "package.json")
        if os.path.exists(package_json):
            try:
                import json
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                    if "jest" in deps:
                        return "jest"
            except Exception:
                pass
                
        # Look for Python unittest files
        test_files = []
        for root, _, files in os.walk(project_path):
            for file in files:
                if file.startswith("test_") and file.endswith(".py"):
                    test_files.append(os.path.join(root, file))
                    
        if test_files:
            # Check if files use unittest or pytest
            for file in test_files[:3]:  # Check just a few files
                try:
                    with open(file, 'r') as f:
                        content = f.read()
                        if "unittest" in content and "TestCase" in content:
                            return "unittest"
                        if "pytest" in content or "fixture" in content:
                            return "pytest"
                except Exception:
                    pass
            
            # Default to pytest if Python test files exist
            return "pytest"
            
        # Default
        return "unknown"
    
    def _run_pytest(self, project_path: str, test_path: Optional[str] = None) -> Dict[str, Any]:
        """Run tests using pytest"""
        cmd = [sys.executable, "-m", "pytest"]
        
        # Add JSON output
        json_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        json_file.close()
        cmd.extend(["--json-report", "--json-report-file", json_file.name])
        
        # Add verbosity
        cmd.append("-v")
        
        # Add specific test path if provided
        if test_path:
            cmd.append(test_path)
        
        # Run the command
        start_time = __import__('time').time()
        process = subprocess.run(
            cmd, 
            cwd=project_path,
            capture_output=True,
            text=True
        )
        end_time = __import__('time').time()
        
        # Process output
        output = process.stdout + process.stderr
        execution_time_ms = int((end_time - start_time) * 1000)
        
        # Parse JSON report if available
        result = {
            "success": process.returncode == 0,
            "execution_time_ms": execution_time_ms,
            "output": output
        }
        
        try:
            with open(json_file.name, 'r') as f:
                report = json.load(f)
                
            result.update({
                "total_tests": report.get("summary", {}).get("total", 0),
                "passed_tests": report.get("summary", {}).get("passed", 0),
                "failed_tests": report.get("summary", {}).get("failed", 0),
                "skipped_tests": report.get("summary", {}).get("skipped", 0),
                "test_files_run": list(report.get("collectors", [])),
                "failures": [
                    {
                        "file": test.get("nodeid", "").split("::")[0],
                        "test": test.get("nodeid", "").split("::")[-1],
                        "message": test.get("call", {}).get("longrepr", "")
                    }
                    for test in report.get("tests", []) 
                    if test.get("outcome") == "failed"
                ]
            })
        except Exception as e:
            self.logger.warning(f"Error parsing pytest JSON report: {str(e)}")
            # Basic parsing of console output
            result.update(self._parse_pytest_output(output))
            
        # Clean up temp file
        try:
            os.unlink(json_file.name)
        except:
            pass
            
        return result
    
    def _parse_pytest_output(self, output: str) -> Dict[str, Any]:
        """Parse pytest console output when JSON report isn't available"""
        result = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0,
            "test_files_run": [],
            "failures": []
        }
        
        # Very simple parsing - not comprehensive
        if "collected " in output:
            try:
                collected_part = output.split("collected ")[1].split(" ")[0]
                result["total_tests"] = int(collected_part)
            except:
                pass
                
        result["failed_tests"] = output.count("FAILED")
        result["passed_tests"] = result["total_tests"] - result["failed_tests"] - result["skipped_tests"]
        
        return result
    
    def _run_unittest(self, project_path: str, test_path: Optional[str] = None) -> Dict[str, Any]:
        """Run tests using Python's unittest"""
        if test_path:
            # For specific test file
            module_path = os.path.relpath(test_path, project_path)
            module_name = module_path.replace(os.path.sep, ".").replace(".py", "")
            cmd = [sys.executable, "-m", "unittest", module_name]
        else:
            # Discover all tests
            cmd = [sys.executable, "-m", "unittest", "discover"]
            
        # Run the command
        start_time = __import__('time').time()
        process = subprocess.run(
            cmd, 
            cwd=project_path,
            capture_output=True,
            text=True
        )
        end_time = __import__('time').time()
        
        # Process output
        output = process.stdout + process.stderr
        execution_time_ms = int((end_time - start_time) * 1000)
        
        # Parse unittest output
        result = {
            "success": process.returncode == 0,
            "execution_time_ms": execution_time_ms,
            "output": output
        }
        
        # Basic parsing of unittest output
        result.update(self._parse_unittest_output(output))
            
        return result
    
    def _parse_unittest_output(self, output: str) -> Dict[str, Any]:
        """Parse unittest console output"""
        result = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0,
            "test_files_run": [],
            "failures": []
        }
        
        # Try to find the summary line like "Ran 42 tests in 0.005s"
        if "Ran " in output and " tests in " in output:
            try:
                ran_part = output.split("Ran ")[1].split(" tests in ")[0]
                result["total_tests"] = int(ran_part)
            except:
                pass
        
        # Count failures
        if "FAILED (failures=" in output:
            try:
                failures_part = output.split("FAILED (failures=")[1].split(")")[0]
                result["failed_tests"] = int(failures_part)
            except:
                pass
                
        # Count errors
        if "FAILED (errors=" in output:
            try:
                errors_part = output.split("FAILED (errors=")[1].split(")")[0]
                result["failed_tests"] += int(errors_part)
            except:
                pass
                
        # Calculate passed tests
        result["passed_tests"] = result["total_tests"] - result["failed_tests"] - result["skipped_tests"]
        
        return result
    
    def _run_jest(self, project_path: str, test_path: Optional[str] = None) -> Dict[str, Any]:
        """Run tests using Jest for JavaScript/TypeScript"""
        # Check if npx is available
        cmd = ["npx", "jest", "--json"]
        
        # Add specific test path if provided
        if test_path:
            cmd.append(test_path)
        
        # Run the command
        start_time = __import__('time').time()
        process = subprocess.run(
            cmd, 
            cwd=project_path,
            capture_output=True,
            text=True
        )
        end_time = __import__('time').time()
        
        # Process output
        output = process.stdout
        execution_time_ms = int((end_time - start_time) * 1000)
        
        # Parse Jest JSON output
        result = {
            "success": process.returncode == 0,
            "execution_time_ms": execution_time_ms,
            "output": output + process.stderr
        }
        
        try:
            # Jest outputs JSON so we can parse it directly
            jest_result = json.loads(output)
            
            result.update({
                "total_tests": jest_result.get("numTotalTests", 0),
                "passed_tests": jest_result.get("numPassedTests", 0),
                "failed_tests": jest_result.get("numFailedTests", 0),
                "skipped_tests": jest_result.get("numPendingTests", 0),
                "test_files_run": [t.get("name", "") for t in jest_result.get("testResults", [])],
                "failures": [
                    {
                        "file": test.get("name", ""),
                        "test": failure.get("title", ""),
                        "message": failure.get("failureMessages", [""])[0]
                    }
                    for test in jest_result.get("testResults", [])
                    for failure in test.get("assertionResults", [])
                    if failure.get("status") == "failed"
                ]
            })
        except json.JSONDecodeError:
            self.logger.warning("Error parsing Jest JSON output")
            # If JSON parsing fails, provide basic info
            result.update({
                "success": process.returncode == 0,
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0 if process.returncode == 0 else 1,
                "skipped_tests": 0
            })
            
        return result
        
    def get_test_coverage(self, project_path: str) -> Dict[str, Any]:
        """Get test coverage information for a project
        
        Args:
            project_path: Path to the project root
            
        Returns:
            Dictionary with coverage information
        """
        framework = self._detect_test_framework(project_path)
        
        if framework == "pytest":
            return self._get_pytest_coverage(project_path)
        elif framework == "jest":
            return self._get_jest_coverage(project_path)
        else:
            return {"success": False, "error": f"Coverage not supported for {framework}"}
    
    def _get_pytest_coverage(self, project_path: str) -> Dict[str, Any]:
        """Get coverage information using pytest-cov"""
        coverage_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        coverage_file.close()
        
        cmd = [
            sys.executable, "-m", "pytest", 
            "--cov", ".", 
            "--cov-report", f"json:{coverage_file.name}"
        ]
        
        process = subprocess.run(
            cmd, 
            cwd=project_path,
            capture_output=True,
            text=True
        )
        
        result = {
            "success": process.returncode == 0,
            "output": process.stdout + process.stderr
        }
        
        try:
            with open(coverage_file.name, 'r') as f:
                coverage_data = json.load(f)
                
            # Process coverage data
            total_statements = 0
            total_covered = 0
            files_coverage = []
            
            for file_path, data in coverage_data.get("files", {}).items():
                statements = data.get("summary", {}).get("num_statements", 0)
                covered = data.get("summary", {}).get("covered_statements", 0)
                
                total_statements += statements
                total_covered += covered
                
                if statements > 0:
                    files_coverage.append({
                        "file": file_path,
                        "statements": statements,
                        "covered": covered,
                        "percent": round(covered / statements * 100, 2) if statements > 0 else 0
                    })
            
            # Calculate overall percentage
            total_percent = round(total_covered / total_statements * 100, 2) if total_statements > 0 else 0
            
            result.update({
                "total_percent": total_percent,
                "total_statements": total_statements,
                "total_covered": total_covered,
                "files": files_coverage
            })
            
        except Exception as e:
            self.logger.error(f"Error processing coverage data: {str(e)}")
            result["error"] = f"Error processing coverage data: {str(e)}"
            
        # Clean up
        try:
            os.unlink(coverage_file.name)
        except:
            pass
            
        return result
    
    def _get_jest_coverage(self, project_path: str) -> Dict[str, Any]:
        """Get coverage information using Jest"""
        coverage_dir = tempfile.mkdtemp()
        
        cmd = [
            "npx", "jest", 
            "--coverage",
            "--coverageDirectory", coverage_dir,
            "--coverageReporters", "json-summary"
        ]
        
        process = subprocess.run(
            cmd, 
            cwd=project_path,
            capture_output=True,
            text=True
        )
        
        result = {
            "success": process.returncode == 0,
            "output": process.stdout + process.stderr
        }
        
        try:
            coverage_file = os.path.join(coverage_dir, "coverage-summary.json")
            with open(coverage_file, 'r') as f:
                coverage_data = json.load(f)
                
            # Process coverage data
            total = coverage_data.get("total", {})
            
            result.update({
                "total_percent": total.get("statements", {}).get("pct", 0),
                "total_statements": total.get("statements", {}).get("total", 0),
                "total_covered": total.get("statements", {}).get("covered", 0),
                "files": [
                    {
                        "file": file_path,
                        "statements": data.get("statements", {}).get("total", 0),
                        "covered": data.get("statements", {}).get("covered", 0),
                        "percent": data.get("statements", {}).get("pct", 0)
                    }
                    for file_path, data in coverage_data.items()
                    if file_path != "total"
                ]
            })
            
        except Exception as e:
            self.logger.error(f"Error processing Jest coverage data: {str(e)}")
            result["error"] = f"Error processing Jest coverage data: {str(e)}"
            
        # Clean up
        try:
            import shutil
            shutil.rmtree(coverage_dir)
        except:
            pass
            
        return result
