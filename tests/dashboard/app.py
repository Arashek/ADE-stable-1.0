from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
from typing import Dict, Any

from .results_collector import ResultsCollector

app = Flask(__name__)
collector = ResultsCollector()

@app.route('/')
def index():
    """Render the main dashboard page"""
    days = int(request.args.get('days', 7))
    
    # Load results
    collector.load_results()
    
    # Get dashboard data
    summary = collector.get_summary(days)
    trends = collector.get_trends(days)
    failures = collector.get_failures(days)
    performance = collector.get_performance_metrics(days)
    
    return render_template(
        'index.html',
        summary=summary,
        trends=trends,
        failures=failures,
        performance=performance,
        days=days
    )

@app.route('/api/summary')
def get_summary():
    """Get summary statistics"""
    days = int(request.args.get('days', 7))
    collector.load_results()
    return jsonify(collector.get_summary(days))

@app.route('/api/trends')
def get_trends():
    """Get test result trends"""
    days = int(request.args.get('days', 7))
    collector.load_results()
    return jsonify(collector.get_trends(days))

@app.route('/api/failures')
def get_failures():
    """Get test failure details"""
    days = int(request.args.get('days', 7))
    collector.load_results()
    return jsonify(collector.get_failures(days))

@app.route('/api/performance')
def get_performance():
    """Get performance metrics"""
    days = int(request.args.get('days', 7))
    collector.load_results()
    return jsonify(collector.get_performance_metrics(days))

if __name__ == '__main__':
    app.run(debug=True) 