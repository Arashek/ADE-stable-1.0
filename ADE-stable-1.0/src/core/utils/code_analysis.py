from typing import Dict, Any, List, Optional
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class CodeAnalyzer:
    """Utility class for analyzing and processing code analysis results."""

    @staticmethod
    def merge_analyses(analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge multiple code analysis results."""
        merged = {
            "insights": [],
            "suggestions": [],
            "warnings": [],
            "metrics": {},
            "diagnostics": [],
            "style_issues": [],
            "security_issues": [],
            "performance_issues": [],
            "dependencies": [],
            "complexity": {},
            "coverage": {},
            "maintainability": {},
            "reliability": {},
            "security": {},
            "performance": {}
        }

        # Track unique issues by their hash
        seen_issues = set()

        for analysis in analyses:
            # Merge insights
            for insight in analysis.get("insights", []):
                if insight not in merged["insights"]:
                    merged["insights"].append(insight)

            # Merge suggestions
            for suggestion in analysis.get("suggestions", []):
                if suggestion not in merged["suggestions"]:
                    merged["suggestions"].append(suggestion)

            # Merge warnings
            for warning in analysis.get("warnings", []):
                if warning not in merged["warnings"]:
                    merged["warnings"].append(warning)

            # Merge metrics
            for metric, value in analysis.get("metrics", {}).items():
                if metric not in merged["metrics"]:
                    merged["metrics"][metric] = value
                else:
                    # Average numeric metrics
                    if isinstance(value, (int, float)) and isinstance(merged["metrics"][metric], (int, float)):
                        merged["metrics"][metric] = (merged["metrics"][metric] + value) / 2

            # Merge diagnostics
            for diagnostic in analysis.get("diagnostics", []):
                issue_hash = CodeAnalyzer._hash_issue(diagnostic)
                if issue_hash not in seen_issues:
                    merged["diagnostics"].append(diagnostic)
                    seen_issues.add(issue_hash)

            # Merge style issues
            for issue in analysis.get("style_issues", []):
                issue_hash = CodeAnalyzer._hash_issue(issue)
                if issue_hash not in seen_issues:
                    merged["style_issues"].append(issue)
                    seen_issues.add(issue_hash)

            # Merge security issues
            for issue in analysis.get("security_issues", []):
                issue_hash = CodeAnalyzer._hash_issue(issue)
                if issue_hash not in seen_issues:
                    merged["security_issues"].append(issue)
                    seen_issues.add(issue_hash)

            # Merge performance issues
            for issue in analysis.get("performance_issues", []):
                issue_hash = CodeAnalyzer._hash_issue(issue)
                if issue_hash not in seen_issues:
                    merged["performance_issues"].append(issue)
                    seen_issues.add(issue_hash)

            # Merge dependencies
            for dep in analysis.get("dependencies", []):
                if dep not in merged["dependencies"]:
                    merged["dependencies"].append(dep)

            # Merge complexity metrics
            for metric, value in analysis.get("complexity", {}).items():
                if metric not in merged["complexity"]:
                    merged["complexity"][metric] = value
                else:
                    merged["complexity"][metric] = max(merged["complexity"][metric], value)

            # Merge coverage metrics
            for metric, value in analysis.get("coverage", {}).items():
                if metric not in merged["coverage"]:
                    merged["coverage"][metric] = value
                else:
                    merged["coverage"][metric] = min(merged["coverage"][metric], value)

            # Merge maintainability metrics
            for metric, value in analysis.get("maintainability", {}).items():
                if metric not in merged["maintainability"]:
                    merged["maintainability"][metric] = value
                else:
                    merged["maintainability"][metric] = min(merged["maintainability"][metric], value)

            # Merge reliability metrics
            for metric, value in analysis.get("reliability", {}).items():
                if metric not in merged["reliability"]:
                    merged["reliability"][metric] = value
                else:
                    merged["reliability"][metric] = min(merged["reliability"][metric], value)

            # Merge security metrics
            for metric, value in analysis.get("security", {}).items():
                if metric not in merged["security"]:
                    merged["security"][metric] = value
                else:
                    merged["security"][metric] = min(merged["security"][metric], value)

            # Merge performance metrics
            for metric, value in analysis.get("performance", {}).items():
                if metric not in merged["performance"]:
                    merged["performance"][metric] = value
                else:
                    merged["performance"][metric] = min(merged["performance"][metric], value)

        return merged

    @staticmethod
    def _hash_issue(issue: Dict[str, Any]) -> str:
        """Create a unique hash for an issue to prevent duplicates."""
        # Create a string representation of the issue
        issue_str = f"{issue.get('type', '')}:{issue.get('message', '')}:{issue.get('line', '')}:{issue.get('column', '')}"
        return hash(issue_str)

    @staticmethod
    def analyze_complexity(code: str) -> Dict[str, Any]:
        """Analyze code complexity metrics."""
        # This would be implemented with actual complexity analysis
        return {
            "cyclomatic_complexity": 0,
            "cognitive_complexity": 0,
            "maintainability_index": 0,
            "lines_of_code": len(code.splitlines()),
            "comment_lines": 0,
            "blank_lines": 0,
            "code_lines": 0
        }

    @staticmethod
    def analyze_dependencies(code: str, language: str) -> List[Dict[str, Any]]:
        """Analyze code dependencies."""
        # This would be implemented with actual dependency analysis
        return []

    @staticmethod
    def analyze_security(code: str, language: str) -> Dict[str, Any]:
        """Analyze code security."""
        # This would be implemented with actual security analysis
        return {
            "vulnerabilities": [],
            "security_score": 0,
            "risk_level": "low",
            "recommendations": []
        }

    @staticmethod
    def analyze_performance(code: str, language: str) -> Dict[str, Any]:
        """Analyze code performance."""
        # This would be implemented with actual performance analysis
        return {
            "performance_score": 0,
            "bottlenecks": [],
            "optimization_opportunities": [],
            "resource_usage": {}
        }

    @staticmethod
    def analyze_maintainability(code: str, language: str) -> Dict[str, Any]:
        """Analyze code maintainability."""
        # This would be implemented with actual maintainability analysis
        return {
            "maintainability_score": 0,
            "technical_debt": 0,
            "code_smells": [],
            "refactoring_opportunities": []
        }

    @staticmethod
    def analyze_reliability(code: str, language: str) -> Dict[str, Any]:
        """Analyze code reliability."""
        # This would be implemented with actual reliability analysis
        return {
            "reliability_score": 0,
            "potential_bugs": [],
            "error_handling": [],
            "test_coverage": 0
        }

    @staticmethod
    def generate_report(analysis: Dict[str, Any]) -> str:
        """Generate a human-readable report from analysis results."""
        report = []
        report.append("Code Analysis Report")
        report.append("=" * 50)

        # Add insights
        if analysis.get("insights"):
            report.append("\nInsights:")
            for insight in analysis["insights"]:
                report.append(f"- {insight}")

        # Add warnings
        if analysis.get("warnings"):
            report.append("\nWarnings:")
            for warning in analysis["warnings"]:
                report.append(f"- {warning}")

        # Add suggestions
        if analysis.get("suggestions"):
            report.append("\nSuggestions:")
            for suggestion in analysis["suggestions"]:
                report.append(f"- {suggestion}")

        # Add metrics
        if analysis.get("metrics"):
            report.append("\nMetrics:")
            for metric, value in analysis["metrics"].items():
                report.append(f"- {metric}: {value}")

        # Add issues
        for issue_type in ["diagnostics", "style_issues", "security_issues", "performance_issues"]:
            if analysis.get(issue_type):
                report.append(f"\n{issue_type.replace('_', ' ').title()}:")
                for issue in analysis[issue_type]:
                    report.append(f"- {issue.get('message', '')}")

        return "\n".join(report) 