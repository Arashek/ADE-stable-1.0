import os
import sys
import argparse
from pathlib import Path
import json
from datetime import datetime
import shutil
from typing import Optional

from .setup import SelfImprovementSetup
from .analyzer import CodeAnalyzer
from .executor import ImprovementExecutor
from .reporter import ImprovementReporter

def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(description='ADE Self-Improvement System')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Initialize command
    init_parser = subparsers.add_parser('init', help='Initialize self-improvement project')
    init_parser.add_argument('--source-dir', type=str, required=True, help='Source codebase directory')
    init_parser.add_argument('--target-dir', type=str, required=True, help='Target directory for the copy')
    init_parser.add_argument('--isolation-level', type=str, choices=['strict', 'moderate', 'minimal'],
                           default='strict', help='Isolation level for the project')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze codebase for improvements')
    analyze_parser.add_argument('--project-dir', type=str, required=True, help='Project directory')
    analyze_parser.add_argument('--output', type=str, help='Output file for analysis results')
    
    # Improve command
    improve_parser = subparsers.add_parser('improve', help='Execute improvements')
    improve_parser.add_argument('--project-dir', type=str, required=True, help='Project directory')
    improve_parser.add_argument('--suggestions-file', type=str, help='File containing improvement suggestions')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate improvement report')
    report_parser.add_argument('--project-dir', type=str, required=True, help='Project directory')
    report_parser.add_argument('--output', type=str, help='Output directory for reports')
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify improvements')
    verify_parser.add_argument('--project-dir', type=str, required=True, help='Project directory')
    verify_parser.add_argument('--output', type=str, help='Output file for verification results')
    
    return parser

def init_project(args: argparse.Namespace) -> None:
    """Initialize a new self-improvement project"""
    print(f"Initializing self-improvement project...")
    print(f"Source directory: {args.source_dir}")
    print(f"Target directory: {args.target_dir}")
    print(f"Isolation level: {args.isolation_level}")
    
    setup = SelfImprovementSetup(args.source_dir, args.target_dir, args.isolation_level)
    setup.initialize()
    
    print("\nProject initialized successfully!")
    print(f"Project directory: {args.target_dir}")
    print(f"Current version: {setup.current_version}")
    print(f"Codebase hash: {setup.codebase_hash}")

def analyze_codebase(args: argparse.Namespace) -> None:
    """Analyze codebase for improvements"""
    print(f"Analyzing codebase in {args.project_dir}...")
    
    analyzer = CodeAnalyzer(args.project_dir)
    analysis_results = analyzer.analyze_codebase()
    suggestions = analyzer.generate_improvement_suggestions(analysis_results)
    
    if args.output:
        output_file = Path(args.output)
        with open(output_file, 'w') as f:
            json.dump({
                'analysis_results': analysis_results,
                'suggestions': [vars(s) for s in suggestions]
            }, f, indent=2)
        print(f"\nAnalysis results saved to: {output_file}")
    else:
        print("\nAnalysis Results:")
        print(f"Total files analyzed: {len(analysis_results.get('files', []))}")
        print(f"Total suggestions generated: {len(suggestions)}")
        print("\nTop suggestions:")
        for s in sorted(suggestions, key=lambda x: x.priority, reverse=True)[:5]:
            print(f"- {s.description} (Priority: {s.priority})")

def execute_improvements(args: argparse.Namespace) -> None:
    """Execute improvements"""
    print(f"Executing improvements in {args.project_dir}...")
    
    executor = ImprovementExecutor(args.project_dir)
    
    if args.suggestions_file:
        with open(args.suggestions_file) as f:
            suggestions_data = json.load(f)
            suggestions = [ImprovementSuggestion(**data) for data in suggestions_data]
    else:
        analyzer = CodeAnalyzer(args.project_dir)
        analysis_results = analyzer.analyze_codebase()
        suggestions = analyzer.generate_improvement_suggestions(analysis_results)
    
    results = executor.execute_improvements(suggestions)
    
    print("\nImprovement Results:")
    successful = len([r for r in results if r.success])
    print(f"Total improvements: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(results) - successful}")
    
    if not all(r.success for r in results):
        print("\nFailed improvements:")
        for r in results:
            if not r.success:
                print(f"- {r.suggestion.description}")
                print(f"  Errors: {', '.join(r.errors)}")

def generate_report(args: argparse.Namespace) -> None:
    """Generate improvement report"""
    print(f"Generating report for {args.project_dir}...")
    
    reporter = ImprovementReporter(args.project_dir)
    
    # Load analysis and improvement results
    analysis_file = Path(args.project_dir) / "analysis" / "latest" / "analysis_results.json"
    improvements_file = Path(args.project_dir) / "improvements" / "latest" / "improvement_results.json"
    
    with open(analysis_file) as f:
        analysis_results = json.load(f)
    with open(improvements_file) as f:
        improvement_results = json.load(f)
    
    report = reporter.generate_report(analysis_results, improvement_results)
    
    if args.output:
        output_dir = Path(args.output)
        output_dir.mkdir(exist_ok=True)
        print(f"\nReport saved to: {output_dir}")
    else:
        print("\nReport Summary:")
        print(f"Total files analyzed: {report.total_files_analyzed}")
        print(f"Total files improved: {report.total_files_improved}")
        print(f"Total changes made: {report.total_changes_made}")
        print("\nKey metrics:")
        for metric in report.metrics:
            print(f"- {metric.metric_name}: {metric.improvement_percentage:.1f}% improvement")
        print("\nTop recommendations:")
        for rec in report.recommendations[:5]:
            print(f"- {rec}")

def verify_improvements(args: argparse.Namespace) -> None:
    """Verify improvements"""
    print(f"Verifying improvements in {args.project_dir}...")
    
    # Run tests on the improved codebase
    import pytest
    test_dir = Path(args.project_dir) / "tests"
    pytest.main([str(test_dir)])
    
    # Compare metrics before and after
    analysis_file = Path(args.project_dir) / "analysis" / "latest" / "analysis_results.json"
    improvements_file = Path(args.project_dir) / "improvements" / "latest" / "improvement_results.json"
    
    with open(analysis_file) as f:
        analysis_results = json.load(f)
    with open(improvements_file) as f:
        improvement_results = json.load(f)
    
    verification_results = {
        'timestamp': datetime.now().isoformat(),
        'metrics_comparison': {
            'complexity': {
                'before': analysis_results['complexity']['average'],
                'after': improvement_results['complexity']['average'],
                'improvement': ((analysis_results['complexity']['average'] - improvement_results['complexity']['average']) 
                              / analysis_results['complexity']['average'] * 100)
            },
            'documentation': {
                'before': analysis_results['documentation']['coverage'],
                'after': improvement_results['documentation']['coverage'],
                'improvement': ((improvement_results['documentation']['coverage'] - analysis_results['documentation']['coverage'])
                              / analysis_results['documentation']['coverage'] * 100)
            },
            'performance': {
                'before': analysis_results['performance']['avg_execution_time'],
                'after': improvement_results['performance']['avg_execution_time'],
                'improvement': ((analysis_results['performance']['avg_execution_time'] - improvement_results['performance']['avg_execution_time'])
                              / analysis_results['performance']['avg_execution_time'] * 100)
            }
        }
    }
    
    if args.output:
        output_file = Path(args.output)
        with open(output_file, 'w') as f:
            json.dump(verification_results, f, indent=2)
        print(f"\nVerification results saved to: {output_file}")
    else:
        print("\nVerification Results:")
        for metric, data in verification_results['metrics_comparison'].items():
            print(f"\n{metric.title()}:")
            print(f"Before: {data['before']:.2f}")
            print(f"After: {data['after']:.2f}")
            print(f"Improvement: {data['improvement']:.1f}%")

def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'init':
            init_project(args)
        elif args.command == 'analyze':
            analyze_codebase(args)
        elif args.command == 'improve':
            execute_improvements(args)
        elif args.command == 'report':
            generate_report(args)
        elif args.command == 'verify':
            verify_improvements(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main() 