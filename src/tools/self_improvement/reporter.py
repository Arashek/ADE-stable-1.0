import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import numpy as np

@dataclass
class ImprovementMetric:
    """Metrics for measuring improvements"""
    metric_name: str
    before_value: float
    after_value: float
    unit: str
    improvement_percentage: float

@dataclass
class ImprovementReport:
    """Detailed report of improvements made"""
    timestamp: str
    total_files_analyzed: int
    total_files_improved: int
    total_changes_made: int
    metrics: List[ImprovementMetric]
    changes_by_category: Dict[str, int]
    changes_by_file: Dict[str, List[str]]
    performance_impact: Dict[str, float]
    code_quality_impact: Dict[str, float]
    documentation_impact: Dict[str, float]
    recommendations: List[str]

class ImprovementReporter:
    """Generates detailed reports about code improvements"""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.reports_dir = project_dir / "reports"
        self.reports_dir.mkdir(exist_ok=True)
    
    def generate_report(self, analysis_results: Dict[str, Any], improvement_results: Dict[str, Any]) -> ImprovementReport:
        """Generate a comprehensive improvement report"""
        # Calculate metrics
        metrics = self._calculate_metrics(analysis_results, improvement_results)
        
        # Categorize changes
        changes_by_category = self._categorize_changes(improvement_results)
        changes_by_file = self._group_changes_by_file(improvement_results)
        
        # Calculate impact
        performance_impact = self._calculate_performance_impact(improvement_results)
        code_quality_impact = self._calculate_code_quality_impact(improvement_results)
        documentation_impact = self._calculate_documentation_impact(improvement_results)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(improvement_results)
        
        # Create report
        report = ImprovementReport(
            timestamp=datetime.now().isoformat(),
            total_files_analyzed=len(analysis_results.get('files', [])),
            total_files_improved=len(improvement_results.get('improved_files', [])),
            total_changes_made=sum(len(changes) for changes in changes_by_file.values()),
            metrics=metrics,
            changes_by_category=changes_by_category,
            changes_by_file=changes_by_file,
            performance_impact=performance_impact,
            code_quality_impact=code_quality_impact,
            documentation_impact=documentation_impact,
            recommendations=recommendations
        )
        
        # Save report
        self._save_report(report)
        
        # Generate visualizations
        self._generate_visualizations(report)
        
        return report
    
    def _calculate_metrics(self, analysis_results: Dict[str, Any], improvement_results: Dict[str, Any]) -> List[ImprovementMetric]:
        """Calculate improvement metrics"""
        metrics = []
        
        # Code complexity metrics
        if 'complexity' in analysis_results and 'complexity' in improvement_results:
            metrics.append(ImprovementMetric(
                metric_name="Average Cyclomatic Complexity",
                before_value=analysis_results['complexity']['average'],
                after_value=improvement_results['complexity']['average'],
                unit="points",
                improvement_percentage=self._calculate_improvement_percentage(
                    analysis_results['complexity']['average'],
                    improvement_results['complexity']['average']
                )
            ))
        
        # Documentation metrics
        if 'documentation' in analysis_results and 'documentation' in improvement_results:
            metrics.append(ImprovementMetric(
                metric_name="Documentation Coverage",
                before_value=analysis_results['documentation']['coverage'],
                after_value=improvement_results['documentation']['coverage'],
                unit="%",
                improvement_percentage=self._calculate_improvement_percentage(
                    analysis_results['documentation']['coverage'],
                    improvement_results['documentation']['coverage']
                )
            ))
        
        # Performance metrics
        if 'performance' in analysis_results and 'performance' in improvement_results:
            metrics.append(ImprovementMetric(
                metric_name="Average Function Execution Time",
                before_value=analysis_results['performance']['avg_execution_time'],
                after_value=improvement_results['performance']['avg_execution_time'],
                unit="ms",
                improvement_percentage=self._calculate_improvement_percentage(
                    analysis_results['performance']['avg_execution_time'],
                    improvement_results['performance']['avg_execution_time'],
                    lower_is_better=True
                )
            ))
        
        return metrics
    
    def _categorize_changes(self, improvement_results: Dict[str, Any]) -> Dict[str, int]:
        """Categorize changes by type"""
        categories = defaultdict(int)
        
        for file_changes in improvement_results.get('changes', []):
            for change in file_changes:
                category = change.get('category', 'other')
                categories[category] += 1
        
        return dict(categories)
    
    def _group_changes_by_file(self, improvement_results: Dict[str, Any]) -> Dict[str, List[str]]:
        """Group changes by file"""
        changes_by_file = defaultdict(list)
        
        for file_changes in improvement_results.get('changes', []):
            file_path = file_changes.get('file_path')
            if file_path:
                for change in file_changes.get('changes', []):
                    changes_by_file[file_path].append(change.get('description', ''))
        
        return dict(changes_by_file)
    
    def _calculate_performance_impact(self, improvement_results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate performance impact of improvements"""
        impact = {
            'execution_time_reduction': 0.0,
            'memory_usage_reduction': 0.0,
            'cpu_usage_reduction': 0.0
        }
        
        if 'performance' in improvement_results:
            perf_data = improvement_results['performance']
            impact['execution_time_reduction'] = perf_data.get('execution_time_reduction', 0.0)
            impact['memory_usage_reduction'] = perf_data.get('memory_usage_reduction', 0.0)
            impact['cpu_usage_reduction'] = perf_data.get('cpu_usage_reduction', 0.0)
        
        return impact
    
    def _calculate_code_quality_impact(self, improvement_results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate code quality impact of improvements"""
        impact = {
            'complexity_reduction': 0.0,
            'duplication_reduction': 0.0,
            'maintainability_improvement': 0.0
        }
        
        if 'code_quality' in improvement_results:
            quality_data = improvement_results['code_quality']
            impact['complexity_reduction'] = quality_data.get('complexity_reduction', 0.0)
            impact['duplication_reduction'] = quality_data.get('duplication_reduction', 0.0)
            impact['maintainability_improvement'] = quality_data.get('maintainability_improvement', 0.0)
        
        return impact
    
    def _calculate_documentation_impact(self, improvement_results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate documentation impact of improvements"""
        impact = {
            'coverage_improvement': 0.0,
            'clarity_improvement': 0.0,
            'completeness_improvement': 0.0
        }
        
        if 'documentation' in improvement_results:
            doc_data = improvement_results['documentation']
            impact['coverage_improvement'] = doc_data.get('coverage_improvement', 0.0)
            impact['clarity_improvement'] = doc_data.get('clarity_improvement', 0.0)
            impact['completeness_improvement'] = doc_data.get('completeness_improvement', 0.0)
        
        return impact
    
    def _generate_recommendations(self, improvement_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations for further improvements"""
        recommendations = []
        
        # Performance recommendations
        if 'performance' in improvement_results:
            perf_data = improvement_results['performance']
            if perf_data.get('execution_time_reduction', 0) < 20:
                recommendations.append("Consider further performance optimizations for critical paths")
            if perf_data.get('memory_usage_reduction', 0) < 15:
                recommendations.append("Investigate memory usage patterns for potential optimizations")
        
        # Code quality recommendations
        if 'code_quality' in improvement_results:
            quality_data = improvement_results['code_quality']
            if quality_data.get('complexity_reduction', 0) < 25:
                recommendations.append("Further refactoring may be needed to reduce code complexity")
            if quality_data.get('duplication_reduction', 0) < 30:
                recommendations.append("Consider extracting more common patterns into shared utilities")
        
        # Documentation recommendations
        if 'documentation' in improvement_results:
            doc_data = improvement_results['documentation']
            if doc_data.get('coverage_improvement', 0) < 40:
                recommendations.append("Expand documentation coverage for better maintainability")
            if doc_data.get('clarity_improvement', 0) < 35:
                recommendations.append("Review and improve documentation clarity")
        
        return recommendations
    
    def _save_report(self, report: ImprovementReport):
        """Save the report to a JSON file"""
        report_data = {
            'timestamp': report.timestamp,
            'total_files_analyzed': report.total_files_analyzed,
            'total_files_improved': report.total_files_improved,
            'total_changes_made': report.total_changes_made,
            'metrics': [
                {
                    'metric_name': m.metric_name,
                    'before_value': m.before_value,
                    'after_value': m.after_value,
                    'unit': m.unit,
                    'improvement_percentage': m.improvement_percentage
                }
                for m in report.metrics
            ],
            'changes_by_category': report.changes_by_category,
            'changes_by_file': report.changes_by_file,
            'performance_impact': report.performance_impact,
            'code_quality_impact': report.code_quality_impact,
            'documentation_impact': report.documentation_impact,
            'recommendations': report.recommendations
        }
        
        report_file = self.reports_dir / f"improvement_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
    
    def _generate_visualizations(self, report: ImprovementReport):
        """Generate visualizations for the report"""
        # Set style
        plt.style.use('seaborn')
        
        # Create visualizations directory
        viz_dir = self.reports_dir / "visualizations"
        viz_dir.mkdir(exist_ok=True)
        
        # 1. Changes by Category
        plt.figure(figsize=(10, 6))
        categories = list(report.changes_by_category.keys())
        values = list(report.changes_by_category.values())
        plt.bar(categories, values)
        plt.title('Changes by Category')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(viz_dir / 'changes_by_category.png')
        plt.close()
        
        # 2. Improvement Metrics
        plt.figure(figsize=(12, 6))
        metrics = [m.metric_name for m in report.metrics]
        improvements = [m.improvement_percentage for m in report.metrics]
        plt.bar(metrics, improvements)
        plt.title('Improvement Metrics')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(viz_dir / 'improvement_metrics.png')
        plt.close()
        
        # 3. Impact Analysis
        plt.figure(figsize=(10, 6))
        impacts = {
            'Performance': report.performance_impact,
            'Code Quality': report.code_quality_impact,
            'Documentation': report.documentation_impact
        }
        
        x = np.arange(len(impacts))
        width = 0.25
        
        for i, (category, impact) in enumerate(impacts.items()):
            values = list(impact.values())
            plt.bar(x + i*width, values, width, label=category)
        
        plt.title('Impact Analysis')
        plt.xticks(x + width, list(impacts['Performance'].keys()), rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.savefig(viz_dir / 'impact_analysis.png')
        plt.close()
    
    def _calculate_improvement_percentage(self, before: float, after: float, lower_is_better: bool = False) -> float:
        """Calculate improvement percentage"""
        if lower_is_better:
            return ((before - after) / before) * 100
        return ((after - before) / before) * 100 