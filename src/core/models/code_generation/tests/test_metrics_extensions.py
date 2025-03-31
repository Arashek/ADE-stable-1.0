"""
Tests for extended metrics collection capabilities.
"""

import unittest
from datetime import datetime, timedelta
from typing import Dict, List, Any
from ..metrics_extensions import (
    ExtendedMetricType, ApplicationMetric, ExtendedMetricsCollector,
    PredictiveAnalyzer, AdvancedAlertManager, MetricsVisualizer
)

class TestExtendedMetricsCollector(unittest.TestCase):
    """Test cases for the ExtendedMetricsCollector class."""
    
    def setUp(self):
        self.collector = ExtendedMetricsCollector()
        
    def test_application_metrics_collection(self):
        """Test collection of application-specific metrics."""
        metrics = self.collector.collect_application_metrics()
        
        # Check response time metrics
        response_metrics = [m for m in metrics if m.name == "response_time"]
        self.assertTrue(len(response_metrics) > 0)
        self.assertEqual(response_metrics[0].type, ExtendedMetricType.APPLICATION)
        self.assertIsInstance(response_metrics[0].value, float)
        
        # Check error rate metrics
        error_metrics = [m for m in metrics if m.name == "error_rate"]
        self.assertTrue(len(error_metrics) > 0)
        self.assertEqual(error_metrics[0].type, ExtendedMetricType.APPLICATION)
        self.assertIsInstance(error_metrics[0].value, float)
        
        # Check cache hit rate metrics
        cache_metrics = [m for m in metrics if m.name == "cache_hit_rate"]
        self.assertTrue(len(cache_metrics) > 0)
        self.assertEqual(cache_metrics[0].type, ExtendedMetricType.APPLICATION)
        self.assertIsInstance(cache_metrics[0].value, float)
        
    def test_business_metrics_collection(self):
        """Test collection of business metrics."""
        metrics = self.collector.collect_business_metrics()
        
        # Check user engagement metrics
        engagement_metrics = [m for m in metrics if m.name == "user_engagement"]
        self.assertTrue(len(engagement_metrics) > 0)
        self.assertEqual(engagement_metrics[0].type, ExtendedMetricType.BUSINESS)
        self.assertIsInstance(engagement_metrics[0].value, float)
        
        # Check revenue metrics
        revenue_metrics = [m for m in metrics if m.name == "revenue"]
        self.assertTrue(len(revenue_metrics) > 0)
        self.assertEqual(revenue_metrics[0].type, ExtendedMetricType.BUSINESS)
        self.assertIsInstance(revenue_metrics[0].value, float)
        
        # Check customer satisfaction metrics
        satisfaction_metrics = [m for m in metrics if m.name == "customer_satisfaction"]
        self.assertTrue(len(satisfaction_metrics) > 0)
        self.assertEqual(satisfaction_metrics[0].type, ExtendedMetricType.BUSINESS)
        self.assertIsInstance(satisfaction_metrics[0].value, float)
        
    def test_user_metrics_collection(self):
        """Test collection of user metrics."""
        metrics = self.collector.collect_user_metrics()
        
        # Check active users metrics
        active_metrics = [m for m in metrics if m.name == "active_users"]
        self.assertTrue(len(active_metrics) > 0)
        self.assertEqual(active_metrics[0].type, ExtendedMetricType.USER)
        self.assertIsInstance(active_metrics[0].value, int)
        
        # Check user retention metrics
        retention_metrics = [m for m in metrics if m.name == "user_retention"]
        self.assertTrue(len(retention_metrics) > 0)
        self.assertEqual(retention_metrics[0].type, ExtendedMetricType.USER)
        self.assertIsInstance(retention_metrics[0].value, float)
        
        # Check session duration metrics
        session_metrics = [m for m in metrics if m.name == "session_duration"]
        self.assertTrue(len(session_metrics) > 0)
        self.assertEqual(session_metrics[0].type, ExtendedMetricType.USER)
        self.assertIsInstance(session_metrics[0].value, float)
        
    def test_security_metrics_collection(self):
        """Test collection of security metrics."""
        metrics = self.collector.collect_security_metrics()
        
        # Check failed logins metrics
        login_metrics = [m for m in metrics if m.name == "failed_logins"]
        self.assertTrue(len(login_metrics) > 0)
        self.assertEqual(login_metrics[0].type, ExtendedMetricType.SECURITY)
        self.assertIsInstance(login_metrics[0].value, int)
        
        # Check security incidents metrics
        incident_metrics = [m for m in metrics if m.name == "security_incidents"]
        self.assertTrue(len(incident_metrics) > 0)
        self.assertEqual(incident_metrics[0].type, ExtendedMetricType.SECURITY)
        self.assertIsInstance(incident_metrics[0].value, int)
        
        # Check API abuse metrics
        abuse_metrics = [m for m in metrics if m.name == "api_abuse"]
        self.assertTrue(len(abuse_metrics) > 0)
        self.assertEqual(abuse_metrics[0].type, ExtendedMetricType.SECURITY)
        self.assertIsInstance(abuse_metrics[0].value, int)

class TestPredictiveAnalyzer(unittest.TestCase):
    """Test cases for the PredictiveAnalyzer class."""
    
    def setUp(self):
        self.collector = ExtendedMetricsCollector()
        self.analyzer = PredictiveAnalyzer(self.collector)
        
    def test_trend_prediction(self):
        """Test trend prediction functionality."""
        prediction = self.analyzer.predict_trends(
            "response_time",
            time_window=timedelta(days=7)
        )
        
        self.assertIn("trend", prediction)
        self.assertIn("confidence", prediction)
        self.assertIn("predictions", prediction)
        self.assertIn("historical_data", prediction)
        
        self.assertIsInstance(prediction["trend"], str)
        self.assertIsInstance(prediction["confidence"], float)
        self.assertIsInstance(prediction["predictions"], list)
        self.assertIsInstance(prediction["historical_data"], list)
        
    def test_anomaly_detection(self):
        """Test anomaly detection functionality."""
        anomalies = self.analyzer.detect_anomalies(
            "response_time",
            time_window=timedelta(days=7)
        )
        
        self.assertIsInstance(anomalies, list)
        if anomalies:
            anomaly = anomalies[0]
            self.assertIn("timestamp", anomaly)
            self.assertIn("value", anomaly)
            self.assertIn("severity", anomaly)
            
            self.assertIsInstance(anomaly["timestamp"], datetime)
            self.assertIsInstance(anomaly["value"], float)
            self.assertIsInstance(anomaly["severity"], str)
            self.assertIn(anomaly["severity"], ["low", "medium", "high"])

class TestAdvancedAlertManager(unittest.TestCase):
    """Test cases for the AdvancedAlertManager class."""
    
    def setUp(self):
        self.alert_manager = AdvancedAlertManager()
        
    def test_rate_of_change_alert(self):
        """Test rate of change alert functionality."""
        self.alert_manager.add_rate_of_change_alert(
            "response_time",
            threshold=0.5,
            time_window=timedelta(hours=1)
        )
        
        self.assertEqual(len(self.alert_manager.alert_rules), 1)
        rule = self.alert_manager.alert_rules[0]
        self.assertEqual(rule["type"], "rate_of_change")
        self.assertEqual(rule["metric"], "response_time")
        self.assertEqual(rule["threshold"], 0.5)
        self.assertEqual(rule["time_window"], timedelta(hours=1))
        
    def test_composite_alert(self):
        """Test composite alert functionality."""
        conditions = [
            {"metric": "cpu_usage", "threshold": 90, "comparison": ">"},
            {"metric": "memory_usage", "threshold": 90, "comparison": ">"}
        ]
        
        self.alert_manager.add_composite_alert(conditions, operator="AND")
        
        self.assertEqual(len(self.alert_manager.alert_rules), 1)
        rule = self.alert_manager.alert_rules[0]
        self.assertEqual(rule["type"], "composite")
        self.assertEqual(rule["conditions"], conditions)
        self.assertEqual(rule["operator"], "AND")
        
    def test_threshold_alert(self):
        """Test threshold alert functionality."""
        self.alert_manager.add_threshold_alert(
            "error_rate",
            threshold=0.1,
            comparison=">"
        )
        
        self.assertEqual(len(self.alert_manager.alert_rules), 1)
        rule = self.alert_manager.alert_rules[0]
        self.assertEqual(rule["type"], "threshold")
        self.assertEqual(rule["metric"], "error_rate")
        self.assertEqual(rule["threshold"], 0.1)
        self.assertEqual(rule["comparison"], ">")

class TestMetricsVisualizer(unittest.TestCase):
    """Test cases for the MetricsVisualizer class."""
    
    def setUp(self):
        self.visualizer = MetricsVisualizer()
        
    def test_time_series_plot(self):
        """Test time series plot creation."""
        data = [
            {"timestamp": datetime.now(), "value": 1.0},
            {"timestamp": datetime.now(), "value": 2.0},
            {"timestamp": datetime.now(), "value": 3.0}
        ]
        
        fig = self.visualizer.create_time_series_plot(data, "test_metric")
        
        self.assertIsNotNone(fig)
        self.assertEqual(len(fig.data), 1)
        self.assertEqual(fig.data[0].name, "test_metric")
        
    def test_heatmap(self):
        """Test heatmap creation."""
        data = [
            {"metric1": 1.0, "metric2": 2.0},
            {"metric1": 2.0, "metric2": 3.0},
            {"metric1": 3.0, "metric2": 4.0}
        ]
        
        fig = self.visualizer.create_heatmap(data, "metric1", "metric2")
        
        self.assertIsNotNone(fig)
        self.assertEqual(len(fig.data), 1)
        self.assertEqual(fig.data[0].type, "heatmap")
        
    def test_dashboard(self):
        """Test dashboard creation."""
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
        
        dashboard = self.visualizer.create_dashboard(metrics)
        
        self.assertIsNotNone(dashboard)
        self.assertEqual(len(dashboard.data), 8)  # 4 plots * 2 metrics
        self.assertEqual(dashboard.layout.grid.rows, 2)
        self.assertEqual(dashboard.layout.grid.columns, 2)
        
    def test_plot_export(self):
        """Test plot export functionality."""
        data = [
            {"timestamp": datetime.now(), "value": 1.0},
            {"timestamp": datetime.now(), "value": 2.0}
        ]
        
        fig = self.visualizer.create_time_series_plot(data, "test_metric")
        
        # Test HTML export
        self.visualizer.save_plot(fig, "test_plot.html")
        
        # Test dashboard export
        metrics = {"test_metric": data}
        dashboard = self.visualizer.create_dashboard(metrics)
        self.visualizer.export_dashboard(dashboard, "test_dashboard.html")
        self.visualizer.export_dashboard(dashboard, "test_dashboard.json", format="json")

if __name__ == '__main__':
    unittest.main() 