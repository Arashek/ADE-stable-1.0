from typing import Dict, List, Optional, Any
import logging
import os
import re
from pathlib import Path
import tempfile
import subprocess
import json

logger = logging.getLogger(__name__)

class SecurityVulnerability:
    """Represents a security vulnerability found in code"""
    def __init__(
        self,
        id: str,
        file: str,
        line: int,
        severity: str,
        description: str,
        code_snippet: Optional[str] = None,
        cwe_id: Optional[str] = None,
        fix_recommendation: Optional[str] = None
    ):
        self.id = id
        self.file = file
        self.line = line
        self.severity = severity
        self.description = description
        self.code_snippet = code_snippet
        self.cwe_id = cwe_id
        self.fix_recommendation = fix_recommendation
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "file": self.file,
            "line": self.line,
            "severity": self.severity,
            "description": self.description,
            "code_snippet": self.code_snippet,
            "cwe_id": self.cwe_id,
            "fix_recommendation": self.fix_recommendation
        }

class SecurityScanner:
    """Utility class for scanning code for security vulnerabilities"""
    
    SEVERITY_LEVELS = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Severity threshold - only report issues at or above this level
        self.severity_threshold = self.config.get("severity_threshold", "LOW")
        
        # Security patterns for different languages
        self._load_security_patterns()
    
    def scan_project(self, project_path: str) -> Dict[str, Any]:
        """Scan an entire project for security vulnerabilities
        
        Args:
            project_path: Path to the project root
            
        Returns:
            Dictionary with security scan results
        """
        self.logger.info(f"Scanning project for security vulnerabilities: {project_path}")
        
        if not os.path.exists(project_path):
            self.logger.error(f"Project path does not exist: {project_path}")
            return {"error": "Project path does not exist"}
            
        result = {
            "path": project_path,
            "vulnerabilities": [],
            "summary": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0,
                "total": 0
            }
        }
        
        try:
            # Walk through project directory
            for root, _, files in os.walk(project_path):
                # Skip hidden directories and common excludes
                if any(exclude in root for exclude in ['.git', 'node_modules', 'venv', '.venv', '__pycache__']):
                    continue
                
                for file in files:
                    if self._is_scannable_file(file):
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, project_path)
                        
                        # Scan individual file
                        file_results = self.scan_file(file_path)
                        
                        # Add file vulnerabilities to project results
                        for vuln in file_results.get("vulnerabilities", []):
                            # Update file path to be relative to project
                            vuln["file"] = rel_path
                            result["vulnerabilities"].append(vuln)
                            
                            # Update summary counts
                            sev = vuln["severity"].upper()
                            if sev in result["summary"]:
                                result["summary"][sev.lower()] += 1
                                result["summary"]["total"] += 1
            
            # Try to use specialized scanners if available
            bandit_results = self._run_bandit_scan(project_path)
            if bandit_results and "vulnerabilities" in bandit_results:
                for vuln in bandit_results["vulnerabilities"]:
                    if not self._is_duplicate_vulnerability(vuln, result["vulnerabilities"]):
                        result["vulnerabilities"].append(vuln)
                        
                        # Update summary counts
                        sev = vuln["severity"].upper()
                        if sev in result["summary"]:
                            result["summary"][sev.lower()] += 1
                            result["summary"]["total"] += 1
            
            # Sort vulnerabilities by severity
            result["vulnerabilities"] = sorted(
                result["vulnerabilities"],
                key=lambda v: self.SEVERITY_LEVELS.index(v["severity"].upper())
            )
            
            # Generate recommendations
            if result["summary"]["total"] > 0:
                result["recommendations"] = self._generate_recommendations(result["vulnerabilities"])
                    
        except Exception as e:
            self.logger.error(f"Error scanning project: {str(e)}")
            result["error"] = str(e)
            
        return result
    
    def scan_file(self, file_path: str) -> Dict[str, Any]:
        """Scan a single file for security vulnerabilities
        
        Args:
            file_path: Path to the file to scan
            
        Returns:
            Dictionary with scan results
        """
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return {"error": "File does not exist"}
            
        result = {
            "file": file_path,
            "vulnerabilities": []
        }
        
        try:
            # Determine file type
            _, ext = os.path.splitext(file_path)
            file_type = ext.lstrip('.').lower()
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
            # Apply pattern matching based on file type
            patterns = self._get_patterns_for_file_type(file_type)
            
            for pattern_name, pattern_info in patterns.items():
                regex = pattern_info["regex"]
                severity = pattern_info["severity"]
                
                # Skip if below threshold
                if self.SEVERITY_LEVELS.index(severity.upper()) > self.SEVERITY_LEVELS.index(self.severity_threshold.upper()):
                    continue
                
                # Search for matches
                for i, line in enumerate(lines):
                    if re.search(regex, line):
                        # Get code snippet for context (3 lines before and after)
                        start_line = max(0, i - 3)
                        end_line = min(len(lines) - 1, i + 3)
                        snippet = "\n".join(lines[start_line:end_line + 1])
                        
                        # Create vulnerability entry
                        vuln_id = f"PATTERN-{pattern_name}-{i}"
                        vuln = SecurityVulnerability(
                            id=vuln_id,
                            file=file_path,
                            line=i + 1,  # 1-based line numbers
                            severity=severity,
                            description=pattern_info["description"],
                            code_snippet=snippet,
                            cwe_id=pattern_info.get("cwe_id"),
                            fix_recommendation=pattern_info.get("fix")
                        )
                        
                        result["vulnerabilities"].append(vuln.to_dict())
                        
        except Exception as e:
            self.logger.error(f"Error scanning file {file_path}: {str(e)}")
            result["error"] = str(e)
            
        return result
    
    def _is_scannable_file(self, filename: str) -> bool:
        """Check if a file should be scanned based on its extension"""
        scannable_extensions = {
            # Code files
            'py', 'js', 'ts', 'jsx', 'tsx', 'java', 'c', 'cpp', 'cs', 
            'go', 'rb', 'php', 'swift', 'kt', 'rs',
            # Web files
            'html', 'htm', 'css', 'xml',
            # Config files
            'json', 'yaml', 'yml', 'toml', 'ini', 'conf',
            # Shell scripts
            'sh', 'bash', 'ps1'
        }
        
        _, ext = os.path.splitext(filename)
        return ext.lstrip('.').lower() in scannable_extensions
    
    def _load_security_patterns(self):
        """Load security patterns from config or use defaults"""
        # Default patterns by language
        self.patterns = {
            # Python security patterns
            "py": {
                "sql_injection": {
                    "regex": r'execute\s*\(\s*.*\%.*\)',
                    "severity": "HIGH",
                    "description": "Potential SQL injection vulnerability - string formatting in SQL query",
                    "cwe_id": "CWE-89",
                    "fix": "Use parameterized queries or ORM instead of string formatting"
                },
                "command_injection": {
                    "regex": r'os\.system\(|subprocess\.call\(|eval\(|exec\(',
                    "severity": "CRITICAL",
                    "description": "Potential command injection vulnerability",
                    "cwe_id": "CWE-78",
                    "fix": "Avoid using os.system or subprocess with shell=True. Use subprocess.run with shell=False and a list of arguments."
                },
                "hardcoded_password": {
                    "regex": r'password\s*=\s*["\'](?!.*\$\{).*["\']|api_key\s*=\s*["\'](?!.*\$\{).*["\']',
                    "severity": "HIGH",
                    "description": "Hardcoded credential detected",
                    "cwe_id": "CWE-798",
                    "fix": "Store sensitive values in environment variables or a secure configuration system"
                },
                "debug_flag": {
                    "regex": r'DEBUG\s*=\s*True',
                    "severity": "MEDIUM",
                    "description": "Debug flag enabled in code",
                    "cwe_id": "CWE-489",
                    "fix": "Disable debug mode in production environments"
                },
                "insecure_hash": {
                    "regex": r'hashlib\.md5\(|hashlib\.sha1\(',
                    "severity": "MEDIUM",
                    "description": "Use of weak cryptographic hash function",
                    "cwe_id": "CWE-327",
                    "fix": "Use stronger hash algorithms like SHA-256 or better"
                }
            },
            
            # JavaScript security patterns
            "js": {
                "eval_usage": {
                    "regex": r'eval\(|new Function\(',
                    "severity": "HIGH",
                    "description": "Use of eval() or new Function() can lead to code injection",
                    "cwe_id": "CWE-94",
                    "fix": "Avoid using eval() or new Function(). Use safer alternatives."
                },
                "innerHTML": {
                    "regex": r'\.innerHTML\s*=',
                    "severity": "MEDIUM",
                    "description": "Direct assignment to innerHTML can lead to XSS",
                    "cwe_id": "CWE-79",
                    "fix": "Use textContent or DOM methods instead, or sanitize inputs before using innerHTML"
                },
                "hardcoded_secrets": {
                    "regex": r'const\s+(?:apiKey|secret|password|token)\s*=\s*["\'](?!.*\$\{).*["\']',
                    "severity": "HIGH",
                    "description": "Hardcoded credential detected",
                    "cwe_id": "CWE-798",
                    "fix": "Store sensitive values in environment variables and load them using process.env"
                },
                "non_https_url": {
                    "regex": r'http://(?!localhost)',
                    "severity": "MEDIUM",
                    "description": "Non-HTTPS URL detected",
                    "cwe_id": "CWE-319",
                    "fix": "Use HTTPS URLs for all external resources"
                }
            },
            
            # General patterns for all languages
            "general": {
                "todo_security": {
                    "regex": r'TODO.*security|FIXME.*security',
                    "severity": "INFO",
                    "description": "Security-related TODO comment found",
                    "fix": "Address the security TODO item"
                },
                "sensitive_info_comment": {
                    "regex": r'(?:password|secret|key).*comment',
                    "severity": "LOW",
                    "description": "Potentially sensitive information in comment",
                    "fix": "Remove sensitive information from comments"
                }
            }
        }
        
        # Add custom patterns from config if provided
        if "security_patterns" in self.config:
            for lang, patterns in self.config["security_patterns"].items():
                if lang not in self.patterns:
                    self.patterns[lang] = {}
                    
                for pattern_name, pattern_info in patterns.items():
                    self.patterns[lang][pattern_name] = pattern_info
    
    def _get_patterns_for_file_type(self, file_type: str) -> Dict[str, Dict[str, Any]]:
        """Get security patterns applicable for a specific file type"""
        # Start with general patterns
        result = self.patterns.get("general", {}).copy()
        
        # Add language-specific patterns
        if file_type in self.patterns:
            result.update(self.patterns[file_type])
            
        # Map related file types
        if file_type in ["jsx", "tsx"]:
            # Add JavaScript patterns for JSX/TSX
            result.update(self.patterns.get("js", {}))
            
        if file_type == "ts" or file_type == "tsx":
            # Add TypeScript specific patterns if available
            result.update(self.patterns.get("ts", {}))
            
        return result
    
    def _run_bandit_scan(self, project_path: str) -> Optional[Dict[str, Any]]:
        """Run Bandit scanner for Python projects if available"""
        try:
            # Check if Bandit is installed
            check_cmd = [sys.executable, "-m", "pip", "list"]
            process = subprocess.run(check_cmd, capture_output=True, text=True)
            if "bandit" not in process.stdout:
                return None
                
            # Create temp file for JSON output
            with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
                temp_path = temp_file.name
                
            # Run Bandit
            cmd = [sys.executable, "-m", "bandit", "-r", project_path, "-f", "json", "-o", temp_path]
            subprocess.run(cmd, capture_output=True)
            
            # Read results
            with open(temp_path, 'r') as f:
                bandit_data = json.load(f)
                
            # Process results
            results = {
                "vulnerabilities": []
            }
            
            for result in bandit_data.get("results", []):
                severity = result.get("issue_severity", "LOW").upper()
                if self.SEVERITY_LEVELS.index(severity) > self.SEVERITY_LEVELS.index(self.severity_threshold.upper()):
                    continue
                    
                vuln = {
                    "id": f"BANDIT-{result.get('test_id')}",
                    "file": result.get("filename"),
                    "line": result.get("line_number"),
                    "severity": severity,
                    "description": result.get("issue_text"),
                    "code_snippet": result.get("code"),
                    "cwe_id": result.get("cwe"),
                    "fix_recommendation": None  # Bandit doesn't provide fix recommendations
                }
                
                results["vulnerabilities"].append(vuln)
                
            # Clean up
            os.unlink(temp_path)
            
            return results
            
        except Exception as e:
            self.logger.warning(f"Error running Bandit scan: {str(e)}")
            return None
    
    def _is_duplicate_vulnerability(self, vuln: Dict[str, Any], existing_vulns: List[Dict[str, Any]]) -> bool:
        """Check if a vulnerability is a duplicate of an existing one"""
        for existing in existing_vulns:
            if (existing["file"] == vuln["file"] and 
                existing["line"] == vuln["line"] and
                existing["description"] == vuln["description"]):
                return True
        return False
    
    def _generate_recommendations(self, vulnerabilities: List[Dict[str, Any]]) -> List[str]:
        """Generate overall security recommendations based on found vulnerabilities"""
        recommendations = []
        
        # Count vulnerabilities by type
        vuln_types = {}
        for vuln in vulnerabilities:
            desc = vuln["description"]
            vuln_types[desc] = vuln_types.get(desc, 0) + 1
            
        # Add recommendations for most common issues
        common_issues = sorted(vuln_types.items(), key=lambda x: x[1], reverse=True)
        for issue, count in common_issues[:5]:
            for vuln in vulnerabilities:
                if vuln["description"] == issue and vuln["fix_recommendation"]:
                    recommendations.append(f"Fix {count} instances of '{issue}': {vuln['fix_recommendation']}")
                    break
        
        # Add general recommendations
        if any(v["severity"].upper() == "CRITICAL" for v in vulnerabilities):
            recommendations.append("CRITICAL security issues detected! Address these issues immediately before deployment.")
            
        if any("hardcoded" in v["description"].lower() for v in vulnerabilities):
            recommendations.append("Use environment variables or a secure configuration management system for all secrets and credentials.")
            
        if any("injection" in v["description"].lower() for v in vulnerabilities):
            recommendations.append("Implement proper input validation and sanitization for all user inputs.")
            
        return recommendations
