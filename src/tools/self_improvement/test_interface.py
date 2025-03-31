import os
import sys
from pathlib import Path
import json
from typing import List, Dict, Any
import time
from datetime import datetime

from .analyzer import CodeAnalyzer, ImprovementSuggestion
from .executor import ImprovementExecutor
from .reporter import ImprovementReporter

class ADETestInterface:
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.analyzer = CodeAnalyzer(project_dir)
        self.executor = ImprovementExecutor(project_dir)
        self.reporter = ImprovementReporter(project_dir)
        self.current_analysis = None
        self.current_suggestions = None
        self.improvement_results = None

    def analyze_codebase(self) -> None:
        """Analyze the codebase and display results"""
        print("\nAnalyzing codebase...")
        self.current_analysis = self.analyzer.analyze_codebase()
        
        print("\nAnalysis Results:")
        print(f"Total files analyzed: {len(self.current_analysis.get('files', []))}")
        print("\nCode Quality Metrics:")
        print(f"Average complexity: {self.current_analysis['complexity']['average']:.2f}")
        print(f"Documentation coverage: {self.current_analysis['documentation']['coverage']:.1f}%")
        print(f"Average execution time: {self.current_analysis['performance']['avg_execution_time']:.2f}s")
        
        print("\nTop Issues Found:")
        for issue in self.current_analysis.get('issues', [])[:5]:
            print(f"- {issue['description']} (Priority: {issue['priority']})")

    def generate_suggestions(self) -> None:
        """Generate improvement suggestions"""
        if not self.current_analysis:
            print("\nPlease analyze the codebase first.")
            return
        
        print("\nGenerating improvement suggestions...")
        self.current_suggestions = self.analyzer.generate_improvement_suggestions(self.current_analysis)
        
        print("\nImprovement Suggestions:")
        for i, suggestion in enumerate(self.current_suggestions, 1):
            print(f"\n{i}. {suggestion.description}")
            print(f"   Priority: {suggestion.priority}")
            print(f"   Type: {suggestion.type}")
            print(f"   Impact: {suggestion.impact}")

    def apply_improvement(self, suggestion_index: int) -> None:
        """Apply a specific improvement"""
        if not self.current_suggestions:
            print("\nNo suggestions available. Please generate suggestions first.")
            return
        
        if not 1 <= suggestion_index <= len(self.current_suggestions):
            print("\nInvalid suggestion index.")
            return
        
        suggestion = self.current_suggestions[suggestion_index - 1]
        print(f"\nApplying improvement: {suggestion.description}")
        
        result = self.executor._execute_single_improvement(suggestion)
        if result.success:
            print("Improvement applied successfully!")
            print("\nChanges made:")
            for change in result.changes_made:
                print(f"- {change}")
        else:
            print("Failed to apply improvement:")
            for error in result.errors:
                print(f"- {error}")

    def view_metrics(self) -> None:
        """View current metrics and improvements"""
        if not self.improvement_results:
            print("\nNo improvement results available.")
            return
        
        print("\nCurrent Metrics:")
        for metric in self.improvement_results['metrics']:
            print(f"\n{metric['name']}:")
            print(f"Before: {metric['before']:.2f}")
            print(f"After: {metric['after']:.2f}")
            print(f"Improvement: {metric['improvement']:.1f}%")

    def generate_report(self) -> None:
        """Generate and display improvement report"""
        if not self.current_analysis or not self.improvement_results:
            print("\nPlease analyze the codebase and apply improvements first.")
            return
        
        print("\nGenerating improvement report...")
        report = self.reporter.generate_report(self.current_analysis, self.improvement_results)
        
        print("\nImprovement Report:")
        print(f"Total files analyzed: {report.total_files_analyzed}")
        print(f"Total files improved: {report.total_files_improved}")
        print(f"Total changes made: {report.total_changes_made}")
        
        print("\nKey Metrics:")
        for metric in report.metrics:
            print(f"\n{metric.metric_name}:")
            print(f"Before: {metric.before_value:.2f}")
            print(f"After: {metric.after_value:.2f}")
            print(f"Improvement: {metric.improvement_percentage:.1f}%")
        
        print("\nRecommendations:")
        for rec in report.recommendations[:5]:
            print(f"- {rec}")

def main():
    """Main entry point for the test interface"""
    # Get project directory from environment or use default
    project_dir = os.getenv("ADE_PROJECT_DIR", "D:/ade-platform-improved")
    
    interface = ADETestInterface(project_dir)
    
    while True:
        print("\nADE Self-Improvement Test Interface")
        print("1. Analyze codebase")
        print("2. Generate improvement suggestions")
        print("3. Apply improvement")
        print("4. View metrics")
        print("5. Generate report")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ")
        
        if choice == "1":
            interface.analyze_codebase()
        elif choice == "2":
            interface.generate_suggestions()
        elif choice == "3":
            if interface.current_suggestions:
                suggestion_index = int(input("Enter suggestion number to apply: "))
                interface.apply_improvement(suggestion_index)
            else:
                print("\nNo suggestions available. Please generate suggestions first.")
        elif choice == "4":
            interface.view_metrics()
        elif choice == "5":
            interface.generate_report()
        elif choice == "6":
            print("\nExiting...")
            break
        else:
            print("\nInvalid choice. Please try again.")
        
        time.sleep(1)  # Add a small delay for better readability

if __name__ == "__main__":
    main() 