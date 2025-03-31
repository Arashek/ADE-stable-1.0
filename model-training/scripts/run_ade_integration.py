#!/usr/bin/env python3

import subprocess
import time
import sys
from pathlib import Path
import logging
import json
from typing import Dict, List
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ade_integration_run.log'),
        logging.StreamHandler()
    ]
)

def check_services():
    """Check if required services are running."""
    try:
        # Check backend service
        response = requests.get("http://localhost:5000/health")
        if response.status_code != 200:
            logging.error("Backend service is not healthy")
            return False
        
        # Check frontend service
        response = requests.get("http://localhost:3000")
        if response.status_code != 200:
            logging.error("Frontend service is not healthy")
            return False
        
        # Check model training service
        response = requests.get("http://localhost:5001/health")
        if response.status_code != 200:
            logging.error("Model training service is not healthy")
            return False
        
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to check services: {e}")
        return False

def run_integration_tests():
    """Run the integration tests."""
    logging.info("Starting integration tests...")
    
    # Run pytest with coverage
    result = subprocess.run([
        "pytest",
        "tests/test_ade_integration.py",
        "-v",
        "--cov=src",
        "--cov-report=html"
    ], capture_output=True, text=True)
    
    # Log test results
    logging.info(result.stdout)
    if result.stderr:
        logging.error(result.stderr)
    
    return result.returncode == 0

def analyze_test_results(report_path: Path) -> Dict:
    """Analyze the test results from the report."""
    with open(report_path, 'r') as f:
        report = f.read()
    
    # Parse the report
    results = []
    current_result = {}
    
    for line in report.split('\n'):
        if line.startswith('## '):
            if current_result:
                results.append(current_result)
            current_result = {'type': line[3:].strip()}
        elif line.startswith('- Expected Operations:'):
            current_result['expected'] = line[22:].strip().split(', ')
        elif line.startswith('- Actual Operations:'):
            current_result['actual'] = line[20:].strip().split(', ')
        elif line.startswith('- Missing Operations:'):
            current_result['missing'] = line[22:].strip().split(', ')
        elif line.startswith('- Extra Operations:'):
            current_result['extra'] = line[19:].strip().split(', ')
        elif line.startswith('- Sequence Match:'):
            current_result['sequence_match'] = line[17:].strip() == 'Yes'
        elif line.startswith('- Has Errors:'):
            current_result['has_errors'] = line[13:].strip() == 'Yes'
    
    if current_result:
        results.append(current_result)
    
    return results

def generate_analysis_plots(results: List[Dict], output_dir: Path):
    """Generate analysis plots from test results."""
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Plot 1: Operation Coverage
    plt.figure(figsize=(10, 6))
    coverage_data = []
    for _, row in df.iterrows():
        expected = len(row['expected'])
        actual = len(row['actual'])
        coverage_data.append({
            'type': row['type'],
            'coverage': actual / expected * 100
        })
    
    coverage_df = pd.DataFrame(coverage_data)
    sns.barplot(data=coverage_df, x='type', y='coverage')
    plt.title('Operation Coverage by Test Type')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_dir / 'operation_coverage.png')
    plt.close()
    
    # Plot 2: Error Distribution
    plt.figure(figsize=(10, 6))
    error_data = df['has_errors'].value_counts()
    plt.pie(error_data, labels=['No Errors', 'Has Errors'], autopct='%1.1f%%')
    plt.title('Error Distribution')
    plt.savefig(output_dir / 'error_distribution.png')
    plt.close()
    
    # Plot 3: Sequence Match Rate
    plt.figure(figsize=(10, 6))
    sequence_data = df['sequence_match'].value_counts()
    plt.pie(sequence_data, labels=['Matches', 'Mismatches'], autopct='%1.1f%%')
    plt.title('Operation Sequence Match Rate')
    plt.savefig(output_dir / 'sequence_match.png')
    plt.close()

def generate_summary_report(results: List[Dict], output_dir: Path):
    """Generate a summary report of the test results."""
    summary = {
        'total_tests': len(results),
        'successful_tests': sum(1 for r in results if not r['has_errors'] and r['sequence_match']),
        'failed_tests': sum(1 for r in results if r['has_errors'] or not r['sequence_match']),
        'operation_coverage': {
            r['type']: len(r['actual']) / len(r['expected']) * 100
            for r in results
        },
        'missing_operations': {
            r['type']: len(r['missing'])
            for r in results
        },
        'extra_operations': {
            r['type']: len(r['extra'])
            for r in results
        }
    }
    
    # Save summary as JSON
    with open(output_dir / 'summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Generate markdown report
    report = [
        "# ADE Integration Test Summary",
        f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
        f"## Overview",
        f"- Total Tests: {summary['total_tests']}",
        f"- Successful Tests: {summary['successful_tests']}",
        f"- Failed Tests: {summary['failed_tests']}",
        f"- Success Rate: {(summary['successful_tests'] / summary['total_tests'] * 100):.1f}%\n",
        "## Operation Coverage",
        "| Test Type | Coverage |",
        "|-----------|----------|"
    ]
    
    for test_type, coverage in summary['operation_coverage'].items():
        report.append(f"| {test_type} | {coverage:.1f}% |")
    
    report.extend([
        "\n## Missing Operations",
        "| Test Type | Count |",
        "|-----------|-------|"
    ])
    
    for test_type, count in summary['missing_operations'].items():
        report.append(f"| {test_type} | {count} |")
    
    report.extend([
        "\n## Extra Operations",
        "| Test Type | Count |",
        "|-----------|-------|"
    ])
    
    for test_type, count in summary['extra_operations'].items():
        report.append(f"| {test_type} | {count} |")
    
    # Save markdown report
    with open(output_dir / 'summary.md', 'w') as f:
        f.write('\n'.join(report))

def main():
    """Main function to run integration tests and generate analysis."""
    # Create output directory
    output_dir = Path("integration_results")
    output_dir.mkdir(exist_ok=True)
    
    # Check services
    if not check_services():
        logging.error("Required services are not running")
        sys.exit(1)
    
    # Run tests
    if not run_integration_tests():
        logging.error("Integration tests failed")
        sys.exit(1)
    
    # Analyze results
    report_path = Path("ade_integration_report.md")
    if not report_path.exists():
        logging.error("Test report not found")
        sys.exit(1)
    
    results = analyze_test_results(report_path)
    
    # Generate analysis
    generate_analysis_plots(results, output_dir)
    generate_summary_report(results, output_dir)
    
    logging.info(f"Analysis complete. Results saved to {output_dir}")

if __name__ == "__main__":
    main() 