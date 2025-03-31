"""
Tests for metrics collection and monitoring capabilities.
"""

import unittest
import time
from datetime import datetime
from typing import Dict, Any
from ..metrics_collection import (
    MetricType, Metric, MetricsCollector,
    MetricsAnalyzer, MetricsMonitor
)

class TestMetricsCollector(unittest.TestCase):
    """Test cases for the MetricsCollector class."""
    
    def setUp(self):
        self.collector = MetricsCollector()
        
    def test_performance_metrics_collection(self):
        """Test collection of performance metrics."""
        metrics = self.collector.collect_performance_metrics()
        
        # Check CPU metrics
        cpu_metrics = [m for m in metrics if m.name == "cpu_usage"]
        self.assertTrue(len(cpu_metrics) > 0)
        self.assertEqual(cpu_metrics[0].type, MetricType.PERFORMANCE)
        self.assertIsInstance(cpu_metrics[0].value, float)
        
        # Check memory metrics
        memory_metrics = [m for m in metrics if m.name == "memory_usage"]
        self.assertTrue(len(memory_metrics) > 0)
        self.assertEqual(memory_metrics[0].type, MetricType.PERFORMANCE)
        self.assertIsInstance(memory_metrics[0].value, float)
        
        # Check disk metrics
        disk_metrics = [m for m in metrics if m.name == "disk_usage"]
        self.assertTrue(len(disk_metrics) > 0)
        self.assertEqual(disk_metrics[0].type, MetricType.PERFORMANCE)
        self.assertIsInstance(disk_metrics[0].value, float)
        
    def test_usage_metrics_collection(self):
        """Test collection of usage metrics."""
        metrics = self.collector.collect_usage_metrics()
        
        # Check process metrics
        process_metrics = [m for m in metrics if m.name == "process_usage"]
        self.assertTrue(len(process_metrics) > 0)
        self.assertEqual(process_metrics[0].type, MetricType.USAGE)
        self.assertIsInstance(process_metrics[0].value, dict)
        
        # Check network metrics
        network_metrics = [m for m in metrics if m.name == "network_usage"]
        self.assertTrue(len(network_metrics) > 0)
        self.assertEqual(network_metrics[0].type, MetricType.USAGE)
        self.assertIsInstance(network_metrics[0].value, dict)
        
    def test_health_metrics_collection(self):
        """Test collection of health metrics."""
        metrics = self.collector.collect_health_metrics()
        
        # Check system load metrics
        load_metrics = [m for m in metrics if m.name == "system_load"]
        self.assertTrue(len(load_metrics) > 0)
        self.assertEqual(load_metrics[0].type, MetricType.HEALTH)
        self.assertIsInstance(load_metrics[0].value, tuple)
        
        # Check process count metrics
        count_metrics = [m for m in metrics if m.name == "process_count"]
        self.assertTrue(len(count_metrics) > 0)
        self.assertEqual(count_metrics[0].type, MetricType.HEALTH)
        self.assertIsInstance(count_metrics[0].value, int)
        
        # Check uptime metrics
        uptime_metrics = [m for m in metrics if m.name == "system_uptime"]
        self.assertTrue(len(uptime_metrics) > 0)
        self.assertEqual(uptime_metrics[0].type, MetricType.HEALTH)
        self.assertIsInstance(uptime_metrics[0].value, float)
        
    def test_custom_metrics_collection(self):
        """Test collection of custom metrics."""
        metric = self.collector.collect_custom_metrics(
            "test_metric",
            42,
            {"tag": "value"},
            {"meta": "data"}
        )
        
        self.assertEqual(metric.name, "test_metric")
        self.assertEqual(metric.type, MetricType.CUSTOM)
        self.assertEqual(metric.value, 42)
        self.assertEqual(metric.tags, {"tag": "value"})
        self.assertEqual(metric.metadata, {"meta": "data"})
        
    def test_metrics_filtering(self):
        """Test filtering of metrics by type."""
        # Collect some metrics
        self.collector.collect_performance_metrics()
        self.collector.collect_usage_metrics()
        self.collector.collect_health_metrics()
        
        # Test filtering
        performance_metrics = self.collector.get_metrics(MetricType.PERFORMANCE)
        self.assertTrue(all(m.type == MetricType.PERFORMANCE for m in performance_metrics))
        
        usage_metrics = self.collector.get_metrics(MetricType.USAGE)
        self.assertTrue(all(m.type == MetricType.USAGE for m in usage_metrics))
        
        health_metrics = self.collector.get_metrics(MetricType.HEALTH)
        self.assertTrue(all(m.type == MetricType.HEALTH for m in health_metrics))

class TestMetricsAnalyzer(unittest.TestCase):
    """Test cases for the MetricsAnalyzer class."""
    
    def setUp(self):
        self.collector = MetricsCollector()
        self.analyzer = MetricsAnalyzer(self.collector)
        
    def test_performance_analysis(self):
        """Test performance metrics analysis."""
        # Collect some performance metrics
        self.collector.collect_performance_metrics()
        self.collector.collect_performance_metrics()  # Collect twice for trend analysis
        
        analysis = self.analyzer.analyze_performance()
        
        # Check CPU analysis
        self.assertIn("cpu_usage", analysis)
        cpu_analysis = analysis["cpu_usage"]
        self.assertIn("current", cpu_analysis)
        self.assertIn("average", cpu_analysis)
        self.assertIn("max", cpu_analysis)
        self.assertIn("min", cpu_analysis)
        self.assertIn("trend", cpu_analysis)
        
        # Check memory analysis
        self.assertIn("memory_usage", analysis)
        memory_analysis = analysis["memory_usage"]
        self.assertIn("current", memory_analysis)
        self.assertIn("average", memory_analysis)
        self.assertIn("max", memory_analysis)
        self.assertIn("min", memory_analysis)
        self.assertIn("trend", memory_analysis)
        
        # Check disk analysis
        self.assertIn("disk_usage", analysis)
        disk_analysis = analysis["disk_usage"]
        self.assertIn("current", disk_analysis)
        self.assertIn("average", disk_analysis)
        self.assertIn("max", disk_analysis)
        self.assertIn("min", disk_analysis)
        self.assertIn("trend", disk_analysis)
        
    def test_usage_analysis(self):
        """Test usage metrics analysis."""
        # Collect some usage metrics
        self.collector.collect_usage_metrics()
        self.collector.collect_usage_metrics()  # Collect twice for averaging
        
        analysis = self.analyzer.analyze_usage()
        
        # Check process usage analysis
        self.assertIn("process_usage", analysis)
        process_analysis = analysis["process_usage"]
        self.assertIn("current", process_analysis)
        self.assertIn("average", process_analysis)
        self.assertIn("cpu_percent", process_analysis["average"])
        self.assertIn("memory_percent", process_analysis["average"])
        self.assertIn("num_threads", process_analysis["average"])
        
        # Check network usage analysis
        self.assertIn("network_usage", analysis)
        network_analysis = analysis["network_usage"]
        self.assertIn("current", network_analysis)
        self.assertIn("total_bytes_sent", network_analysis)
        self.assertIn("total_bytes_recv", network_analysis)
        self.assertIn("total_packets_sent", network_analysis)
        self.assertIn("total_packets_recv", network_analysis)
        
    def test_health_analysis(self):
        """Test health metrics analysis."""
        # Collect some health metrics
        self.collector.collect_health_metrics()
        self.collector.collect_health_metrics()  # Collect twice for averaging
        
        analysis = self.analyzer.analyze_health()
        
        # Check system load analysis
        self.assertIn("system_load", analysis)
        load_analysis = analysis["system_load"]
        self.assertIn("current", load_analysis)
        self.assertIn("average", load_analysis)
        self.assertEqual(len(load_analysis["average"]), 3)
        
        # Check process count analysis
        self.assertIn("process_count", analysis)
        count_analysis = analysis["process_count"]
        self.assertIn("current", count_analysis)
        self.assertIn("average", count_analysis)
        self.assertIn("max", count_analysis)
        self.assertIn("min", count_analysis)
        
        # Check uptime analysis
        self.assertIn("system_uptime", analysis)
        uptime_analysis = analysis["system_uptime"]
        self.assertIn("current", uptime_analysis)
        self.assertIn("start_time", uptime_analysis)
        self.assertIsInstance(uptime_analysis["start_time"], datetime)

class TestMetricsMonitor(unittest.TestCase):
    """Test cases for the MetricsMonitor class."""
    
    def setUp(self):
        self.collector = MetricsCollector()
        self.analyzer = MetricsAnalyzer(self.collector)
        self.monitor = MetricsMonitor(self.collector, self.analyzer)
        
    def test_alert_creation(self):
        """Test creation of alerts."""
        # Create a high CPU usage alert
        self.monitor._create_alert(
            "high_cpu_usage",
            "CPU usage is above 90%",
            {"current": 95, "average": 85}
        )
        
        alerts = self.monitor.get_alerts()
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["type"], "high_cpu_usage")
        self.assertEqual(alerts[0]["message"], "CPU usage is above 90%")
        self.assertEqual(alerts[0]["details"]["current"], 95)
        self.assertEqual(alerts[0]["details"]["average"], 85)
        self.assertIsInstance(alerts[0]["timestamp"], datetime)
        
    def test_alert_clearing(self):
        """Test clearing of alerts."""
        # Create some alerts
        self.monitor._create_alert("test_alert", "Test message", {})
        self.monitor._create_alert("test_alert2", "Test message 2", {})
        
        alerts = self.monitor.get_alerts()
        self.assertEqual(len(alerts), 2)
        
        # Clear alerts
        self.monitor.clear_alerts()
        alerts = self.monitor.get_alerts()
        self.assertEqual(len(alerts), 0)
        
    def test_alert_conditions(self):
        """Test alert condition checking."""
        # Create test data that would trigger alerts
        performance = {
            "cpu_usage": {"current": 95},
            "memory_usage": {"current": 95},
            "disk_usage": {"current": 95}
        }
        usage = {}
        health = {
            "process_count": {"current": 1500},
            "system_load": {"current": [15, 12, 10]}
        }
        
        # Check alerts
        self.monitor._check_alerts(performance, usage, health)
        alerts = self.monitor.get_alerts()
        
        # Verify all expected alerts were created
        alert_types = {alert["type"] for alert in alerts}
        self.assertIn("high_cpu_usage", alert_types)
        self.assertIn("high_memory_usage", alert_types)
        self.assertIn("high_disk_usage", alert_types)
        self.assertIn("high_process_count", alert_types)
        self.assertIn("high_system_load", alert_types)

if __name__ == '__main__':
    unittest.main() 