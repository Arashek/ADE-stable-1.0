"""
Tests for extended metrics collection capabilities with additional metric types,
enhanced ML models, more visualization types, and advanced alert conditions.
"""

import unittest
from datetime import datetime, timedelta
from typing import Dict, List, Any
from ..metrics_extensions_2 import (
    ExtendedMetricType2, DatabaseMetric, ExtendedMetricsCollector2,
    EnhancedPredictiveAnalyzer, AdvancedAlertManager2, MetricsVisualizer2
)

class TestExtendedMetricsCollector2(unittest.TestCase):
    """Test cases for the ExtendedMetricsCollector2 class."""
    
    def setUp(self):
        self.collector = ExtendedMetricsCollector2()
        
    def test_database_metrics_collection(self):
        """Test collection of database-specific metrics."""
        metrics = self.collector.collect_database_metrics()
        
        # Check query execution time metrics
        query_metrics = [m for m in metrics if m.name == "query_execution_time"]
        self.assertTrue(len(query_metrics) > 0)
        self.assertEqual(query_metrics[0].type, ExtendedMetricType2.DATABASE)
        self.assertIsInstance(query_metrics[0].value, float)
        
        # Check connection pool metrics
        pool_metrics = [m for m in metrics if m.name == "connection_pool_usage"]
        self.assertTrue(len(pool_metrics) > 0)
        self.assertEqual(pool_metrics[0].type, ExtendedMetricType2.DATABASE)
        self.assertIsInstance(pool_metrics[0].value, float)
        
        # Check transaction metrics
        transaction_metrics = [m for m in metrics if m.name == "transaction_count"]
        self.assertTrue(len(transaction_metrics) > 0)
        self.assertEqual(transaction_metrics[0].type, ExtendedMetricType2.DATABASE)
        self.assertIsInstance(transaction_metrics[0].value, int)
        
    def test_network_metrics_collection(self):
        """Test collection of network metrics."""
        metrics = self.collector.collect_network_metrics()
        
        # Check network latency metrics
        latency_metrics = [m for m in metrics if m.name == "network_latency"]
        self.assertTrue(len(latency_metrics) > 0)
        self.assertEqual(latency_metrics[0].type, ExtendedMetricType2.NETWORK)
        self.assertIsInstance(latency_metrics[0].value, float)
        
        # Check bandwidth metrics
        bandwidth_metrics = [m for m in metrics if m.name == "bandwidth_usage"]
        self.assertTrue(len(bandwidth_metrics) > 0)
        self.assertEqual(bandwidth_metrics[0].type, ExtendedMetricType2.NETWORK)
        self.assertIsInstance(bandwidth_metrics[0].value, float)
        
        # Check connection metrics
        connection_metrics = [m for m in metrics if m.name == "active_connections"]
        self.assertTrue(len(connection_metrics) > 0)
        self.assertEqual(connection_metrics[0].type, ExtendedMetricType2.NETWORK)
        self.assertIsInstance(connection_metrics[0].value, int)
        
    def test_infrastructure_metrics_collection(self):
        """Test collection of infrastructure metrics."""
        metrics = self.collector.collect_infrastructure_metrics()
        
        # Check container metrics
        container_metrics = [m for m in metrics if m.name == "container_cpu_usage"]
        self.assertTrue(len(container_metrics) > 0)
        self.assertEqual(container_metrics[0].type, ExtendedMetricType2.INFRASTRUCTURE)
        self.assertIsInstance(container_metrics[0].value, float)
        
        # Check Kubernetes metrics
        k8s_metrics = [m for m in metrics if m.name == "pod_count"]
        self.assertTrue(len(k8s_metrics) > 0)
        self.assertEqual(k8s_metrics[0].type, ExtendedMetricType2.INFRASTRUCTURE)
        self.assertIsInstance(k8s_metrics[0].value, int)
        
        # Check storage metrics
        storage_metrics = [m for m in metrics if m.name == "disk_usage"]
        self.assertTrue(len(storage_metrics) > 0)
        self.assertEqual(storage_metrics[0].type, ExtendedMetricType2.INFRASTRUCTURE)
        self.assertIsInstance(storage_metrics[0].value, float)

class TestEnhancedPredictiveAnalyzer(unittest.TestCase):
    """Test cases for the EnhancedPredictiveAnalyzer class."""
    
    def setUp(self):
        self.collector = ExtendedMetricsCollector2()
        self.analyzer = EnhancedPredictiveAnalyzer(self.collector)
        
    def test_advanced_trend_prediction(self):
        """Test advanced trend prediction functionality."""
        prediction = self.analyzer.predict_trends_advanced(
            "query_execution_time",
            time_window=timedelta(days=7)
        )
        
        self.assertIn("trend", prediction)
        self.assertIn("confidence", prediction)
        self.assertIn("predictions", prediction)
        self.assertIn("historical_data", prediction)
        self.assertIn("clusters", prediction)
        self.assertIn("pca_components", prediction)
        
        self.assertIsInstance(prediction["trend"], str)
        self.assertIsInstance(prediction["confidence"], float)
        self.assertIsInstance(prediction["predictions"], list)
        self.assertIsInstance(prediction["historical_data"], list)
        self.assertIsInstance(prediction["clusters"], list)
        self.assertIsInstance(prediction["pca_components"], list)
        
    def test_advanced_anomaly_detection(self):
        """Test advanced anomaly detection functionality."""
        anomalies = self.analyzer.detect_anomalies_advanced(
            "query_execution_time",
            time_window=timedelta(days=7)
        )
        
        self.assertIsInstance(anomalies, list)
        if anomalies:
            anomaly = anomalies[0]
            self.assertIn("timestamp", anomaly)
            self.assertIn("value", anomaly)
            self.assertIn("severity", anomaly)
            self.assertIn("detection_method", anomaly)
            self.assertIn("cluster", anomaly)
            
            self.assertIsInstance(anomaly["timestamp"], datetime)
            self.assertIsInstance(anomaly["value"], float)
            self.assertIsInstance(anomaly["severity"], str)
            self.assertIsInstance(anomaly["detection_method"], str)
            self.assertIsInstance(anomaly["cluster"], int)
            self.assertIn(anomaly["severity"], ["low", "medium", "high"])
            self.assertIn(anomaly["detection_method"], ["isolation_forest", "dbscan"])

class TestAdvancedAlertManager2(unittest.TestCase):
    """Test cases for the AdvancedAlertManager2 class."""
    
    def setUp(self):
        self.alert_manager = AdvancedAlertManager2()
        
    def test_pattern_matching_alert(self):
        """Test pattern matching alert functionality."""
        self.alert_manager.add_pattern_matching_alert(
            "query_execution_time",
            pattern="spike",
            time_window=timedelta(hours=1)
        )
        
        self.assertEqual(len(self.alert_manager.alert_rules), 1)
        rule = self.alert_manager.alert_rules[0]
        self.assertEqual(rule["type"], "pattern_matching")
        self.assertEqual(rule["metric"], "query_execution_time")
        self.assertEqual(rule["pattern"], "spike")
        self.assertEqual(rule["time_window"], timedelta(hours=1))
        
    def test_statistical_alert(self):
        """Test statistical alert functionality."""
        self.alert_manager.add_statistical_alert(
            "network_latency",
            threshold=2.0,
            method="zscore"
        )
        
        self.assertEqual(len(self.alert_manager.alert_rules), 1)
        rule = self.alert_manager.alert_rules[0]
        self.assertEqual(rule["type"], "statistical")
        self.assertEqual(rule["metric"], "network_latency")
        self.assertEqual(rule["threshold"], 2.0)
        self.assertEqual(rule["method"], "zscore")
        
    def test_correlation_alert(self):
        """Test correlation alert functionality."""
        self.alert_manager.add_correlation_alert(
            "query_execution_time",
            "network_latency",
            threshold=0.8
        )
        
        self.assertEqual(len(self.alert_manager.alert_rules), 1)
        rule = self.alert_manager.alert_rules[0]
        self.assertEqual(rule["type"], "correlation")
        self.assertEqual(rule["metric1"], "query_execution_time")
        self.assertEqual(rule["metric2"], "network_latency")
        self.assertEqual(rule["threshold"], 0.8)

class TestMetricsVisualizer2(unittest.TestCase):
    """Test cases for the MetricsVisualizer2 class."""
    
    def setUp(self):
        self.visualizer = MetricsVisualizer2()
        
    def test_pie_chart(self):
        """Test pie chart creation."""
        data = [
            {"value": 1.0, "label": "A"},
            {"value": 2.0, "label": "B"},
            {"value": 3.0, "label": "C"}
        ]
        
        fig = self.visualizer.create_pie_chart(data, "test_metric")
        
        self.assertIsNotNone(fig)
        self.assertEqual(len(fig.data), 1)
        self.assertEqual(fig.data[0].type, "pie")
        self.assertEqual(len(fig.data[0].values), 3)
        self.assertEqual(len(fig.data[0].labels), 3)
        
    def test_scatter_plot(self):
        """Test scatter plot creation."""
        data = [
            {"metric1": 1.0, "metric2": 2.0},
            {"metric1": 2.0, "metric2": 3.0},
            {"metric1": 3.0, "metric2": 4.0}
        ]
        
        fig = self.visualizer.create_scatter_plot(data, "metric1", "metric2")
        
        self.assertIsNotNone(fig)
        self.assertEqual(len(fig.data), 1)
        self.assertEqual(fig.data[0].mode, "markers")
        self.assertEqual(len(fig.data[0].x), 3)
        self.assertEqual(len(fig.data[0].y), 3)
        
    def test_network_graph(self):
        """Test network graph creation."""
        data = [
            {"name": "A", "value": 1.0, "connections": ["B"]},
            {"name": "B", "value": 2.0, "connections": ["A", "C"]},
            {"name": "C", "value": 3.0, "connections": ["B"]}
        ]
        
        fig = self.visualizer.create_network_graph(data)
        
        self.assertIsNotNone(fig)
        self.assertEqual(len(fig.data), 2)  # Nodes and edges
        self.assertEqual(fig.data[0].mode, "markers+text")
        self.assertEqual(fig.data[1].mode, "lines")
        
    def test_advanced_dashboard(self):
        """Test advanced dashboard creation."""
        metrics = {
            "metric1": [
                {"timestamp": datetime.now(), "value": 1.0},
                {"timestamp": datetime.now(), "value": 2.0}
            ],
            "metric2": [
                {"timestamp": datetime.now(), "value": 3.0},
                {"timestamp": datetime.now(), "value": 4.0}
            ]
        }
        
        dashboard = self.visualizer.create_advanced_dashboard(metrics)
        
        self.assertIsNotNone(dashboard)
        self.assertEqual(dashboard.layout.grid.rows, 2)
        self.assertEqual(dashboard.layout.grid.columns, 2)
        self.assertEqual(len(dashboard.data), 4)  # Time series, scatter, pie, network
        
    def test_plot_export(self):
        """Test plot export functionality."""
        data = [
            {"timestamp": datetime.now(), "value": 1.0},
            {"timestamp": datetime.now(), "value": 2.0}
        ]
        
        fig = self.visualizer.create_pie_chart(data, "test_metric")
        
        # Test HTML export
        self.visualizer.save_plot(fig, "test_plot.html")
        
        # Test dashboard export
        metrics = {"test_metric": data}
        dashboard = self.visualizer.create_advanced_dashboard(metrics)
        self.visualizer.export_dashboard(dashboard, "test_dashboard.html")
        self.visualizer.export_dashboard(dashboard, "test_dashboard.json", format="json")

if __name__ == '__main__':
    unittest.main() 