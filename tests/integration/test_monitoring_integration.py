import unittest
import sys
import os
import time
import threading
from unittest.mock import patch, MagicMock, Mock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.metrics import MetricsCollector
from src.utils.logging_framework import setup_logging, set_request_context, clear_request_context
from src.utils.health_check import HealthCheck, HealthStatus, DependencyStatus
from src.utils.tracing import TracingManager

class TestMonitoringIntegration(unittest.TestCase):
    """
    Integration tests for monitoring and observability components working together
    """
    
    @patch('src.utils.metrics.start_http_server')
    @patch('src.utils.metrics.Counter')
    @patch('src.utils.metrics.Histogram')
    def test_metrics_with_logging(self, mock_histogram, mock_counter, mock_start_http_server):
        """Test that metrics and logging work together"""
        # Setup mocks
        mock_counter_instance = Mock()
        mock_counter.return_value = mock_counter_instance
        mock_counter_instance.labels.return_value = mock_counter_instance
        
        mock_histogram_instance = Mock()
        mock_histogram.return_value = mock_histogram_instance
        mock_histogram_instance.labels.return_value = mock_histogram_instance
        
        # Create metrics collector
        metrics = MetricsCollector(service_name="test_service")
        
        # Setup logging with a string buffer
        logger = setup_logging(service_name="test_service")
        
        # Set request context
        set_request_context(request_id="req123", user_id="user456")
        
        # Define a test function with metrics and logging
        @metrics.request_timer(method="GET", endpoint="/test")
        def test_function():
            logger.info("Processing request", extra={"endpoint": "/test"})
            return "success"
        
        # Call the function
        result = test_function()
        
        # Verify the result
        self.assertEqual(result, "success")
        
        # Verify metrics were recorded
        mock_counter_instance.labels.assert_called_with(method="GET", endpoint="/test", status=200)
        mock_counter_instance.inc.assert_called_once()
        
        mock_histogram_instance.labels.assert_called_with(method="GET", endpoint="/test")
        mock_histogram_instance.observe.assert_called_once()
        
        # Clear request context
        clear_request_context()
    
    @patch('src.utils.health_check.psutil.cpu_percent')
    @patch('src.utils.health_check.psutil.virtual_memory')
    @patch('src.utils.health_check.psutil.disk_usage')
    def test_health_check_with_metrics(self, mock_disk_usage, mock_virtual_memory, mock_cpu_percent):
        """Test that health checks and metrics work together"""
        # Mock system metrics
        mock_cpu_percent.return_value = 50.0
        mock_virtual_memory.return_value = Mock(percent=60.0)
        mock_disk_usage.return_value = Mock(percent=70.0)
        
        # Create health check
        health_check = HealthCheck(service_name="test_service")
        
        # Create metrics collector
        metrics = MetricsCollector(service_name="test_service")
        
        # Add a dependency check that uses metrics
        def check_database():
            # Record metrics for the database check
            metrics.set_resource_usage("database", "latency_ms", 15.0)
            return DependencyStatus(
                name="database",
                status=HealthStatus.HEALTHY,
                details={"latency_ms": 15.0}
            )
        
        health_check.add_dependency_check(check_database)
        
        # Check health
        health_status = health_check.check_health()
        
        # Verify health status
        self.assertEqual(health_status["status"], HealthStatus.HEALTHY)
        self.assertEqual(health_status["dependencies"]["items"][0]["name"], "database")
        self.assertEqual(health_status["dependencies"]["items"][0]["status"], HealthStatus.HEALTHY)
    
    @patch('src.utils.tracing.trace')
    def test_tracing_with_metrics_and_logging(self, mock_trace):
        """Test that tracing, metrics, and logging work together"""
        # Setup mocks
        mock_tracer_provider = Mock()
        mock_trace.get_tracer_provider.return_value = mock_tracer_provider
        
        mock_tracer = Mock()
        mock_trace.get_tracer.return_value = mock_tracer
        
        mock_span = Mock()
        mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span
        
        # Create tracing manager
        tracing = TracingManager(service_name="test_service")
        
        # Create metrics collector
        metrics = MetricsCollector(service_name="test_service")
        
        # Setup logging
        logger = setup_logging(service_name="test_service")
        
        # Set request context
        set_request_context(request_id="req123", user_id="user456")
        
        # Define a test function with tracing, metrics, and logging
        @tracing.trace_function(name="test_operation")
        @metrics.request_timer(method="GET", endpoint="/test")
        def test_function(param1, param2="default"):
            logger.info("Processing request", extra={
                "endpoint": "/test",
                "param1": param1,
                "param2": param2
            })
            return f"{param1}-{param2}"
        
        # Call the function
        result = test_function("value1", param2="value2")
        
        # Verify the result
        self.assertEqual(result, "value1-value2")
        
        # Verify tracing was used
        mock_tracer.start_as_current_span.assert_called_with("test_operation")
        
        # Verify span attributes were set
        mock_span.set_attribute.assert_any_call("arg_0", "value1")
        mock_span.set_attribute.assert_any_call("kwarg_param2", "value2")
        
        # Clear request context
        clear_request_context()

if __name__ == '__main__':
    unittest.main()
