import json
import os
import sys
import unittest
from unittest.mock import MagicMock, Mock, patch

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, Response
from fastapi.testclient import TestClient
from fluxora.core.health_check import (DependencyStatus, HealthCheck,
                                       HealthStatus,
                                       add_health_check_endpoints)


class TestHealthCheck(unittest.TestCase):
    def test_dependency_status(self):
        """Test that DependencyStatus correctly represents dependency status"""
        # Create a healthy dependency status
        healthy_status = DependencyStatus(
            name="database", status=HealthStatus.HEALTHY, details={"latency_ms": 10}
        )

        # Verify properties
        self.assertEqual(healthy_status.name, "database")
        self.assertEqual(healthy_status.status, HealthStatus.HEALTHY)
        self.assertEqual(healthy_status.details, {"latency_ms": 10})

        # Verify dictionary representation
        status_dict = healthy_status.to_dict()
        self.assertEqual(status_dict["name"], "database")
        self.assertEqual(status_dict["status"], HealthStatus.HEALTHY)
        self.assertEqual(status_dict["details"], {"latency_ms": 10})

        # Create an unhealthy dependency status
        unhealthy_status = DependencyStatus(
            name="redis",
            status=HealthStatus.UNHEALTHY,
            details={"error": "Connection refused"},
        )

        # Verify properties
        self.assertEqual(unhealthy_status.name, "redis")
        self.assertEqual(unhealthy_status.status, HealthStatus.UNHEALTHY)
        self.assertEqual(unhealthy_status.details, {"error": "Connection refused"})

    @patch("src.utils.health_check.psutil.cpu_percent")
    @patch("src.utils.health_check.psutil.virtual_memory")
    @patch("src.utils.health_check.psutil.disk_usage")
    def test_health_check_healthy(
        self, mock_disk_usage, mock_virtual_memory, mock_cpu_percent
    ):
        """Test that HealthCheck returns healthy status when all checks pass"""
        # Mock system metrics
        mock_cpu_percent.return_value = 50.0
        mock_virtual_memory.return_value = Mock(percent=60.0)
        mock_disk_usage.return_value = Mock(percent=70.0)

        # Create health check
        health_check = HealthCheck(service_name="test_service")

        # Add a healthy dependency check
        def check_database():
            return DependencyStatus(
                name="database", status=HealthStatus.HEALTHY, details={"latency_ms": 10}
            )

        health_check.add_dependency_check(check_database)

        # Check health
        health_status = health_check.check_health()

        # Verify overall status
        self.assertEqual(health_status["status"], HealthStatus.HEALTHY)
        self.assertEqual(health_status["service"], "test_service")

        # Verify system metrics
        self.assertEqual(health_status["system"]["status"], HealthStatus.HEALTHY)
        self.assertEqual(health_status["system"]["cpu_percent"], 50.0)
        self.assertEqual(health_status["system"]["memory_percent"], 60.0)
        self.assertEqual(health_status["system"]["disk_percent"], 70.0)

        # Verify dependencies
        self.assertEqual(health_status["dependencies"]["status"], HealthStatus.HEALTHY)
        self.assertEqual(len(health_status["dependencies"]["items"]), 1)
        self.assertEqual(health_status["dependencies"]["items"][0]["name"], "database")
        self.assertEqual(
            health_status["dependencies"]["items"][0]["status"], HealthStatus.HEALTHY
        )

    @patch("src.utils.health_check.psutil.cpu_percent")
    @patch("src.utils.health_check.psutil.virtual_memory")
    @patch("src.utils.health_check.psutil.disk_usage")
    def test_health_check_degraded_system(
        self, mock_disk_usage, mock_virtual_memory, mock_cpu_percent
    ):
        """Test that HealthCheck returns degraded status when system metrics exceed thresholds"""
        # Mock system metrics (CPU above threshold)
        mock_cpu_percent.return_value = 95.0
        mock_virtual_memory.return_value = Mock(percent=60.0)
        mock_disk_usage.return_value = Mock(percent=70.0)

        # Create health check
        health_check = HealthCheck(service_name="test_service")

        # Add a healthy dependency check
        def check_database():
            return DependencyStatus(
                name="database", status=HealthStatus.HEALTHY, details={"latency_ms": 10}
            )

        health_check.add_dependency_check(check_database)

        # Check health
        health_status = health_check.check_health()

        # Verify overall status
        self.assertEqual(health_status["status"], HealthStatus.DEGRADED)

        # Verify system metrics
        self.assertEqual(health_status["system"]["status"], HealthStatus.DEGRADED)

        # Verify dependencies
        self.assertEqual(health_status["dependencies"]["status"], HealthStatus.HEALTHY)

    @patch("src.utils.health_check.psutil.cpu_percent")
    @patch("src.utils.health_check.psutil.virtual_memory")
    @patch("src.utils.health_check.psutil.disk_usage")
    def test_health_check_degraded_dependency(
        self, mock_disk_usage, mock_virtual_memory, mock_cpu_percent
    ):
        """Test that HealthCheck returns degraded status when a dependency is degraded"""
        # Mock system metrics
        mock_cpu_percent.return_value = 50.0
        mock_virtual_memory.return_value = Mock(percent=60.0)
        mock_disk_usage.return_value = Mock(percent=70.0)

        # Create health check
        health_check = HealthCheck(service_name="test_service")

        # Add a degraded dependency check
        def check_database():
            return DependencyStatus(
                name="database",
                status=HealthStatus.DEGRADED,
                details={"latency_ms": 500},
            )

        health_check.add_dependency_check(check_database)

        # Check health
        health_status = health_check.check_health()

        # Verify overall status
        self.assertEqual(health_status["status"], HealthStatus.DEGRADED)

        # Verify system metrics
        self.assertEqual(health_status["system"]["status"], HealthStatus.HEALTHY)

        # Verify dependencies
        self.assertEqual(health_status["dependencies"]["status"], HealthStatus.DEGRADED)
        self.assertEqual(
            health_status["dependencies"]["items"][0]["status"], HealthStatus.DEGRADED
        )

    @patch("src.utils.health_check.psutil.cpu_percent")
    @patch("src.utils.health_check.psutil.virtual_memory")
    @patch("src.utils.health_check.psutil.disk_usage")
    def test_health_check_unhealthy_dependency(
        self, mock_disk_usage, mock_virtual_memory, mock_cpu_percent
    ):
        """Test that HealthCheck returns unhealthy status when a dependency is unhealthy"""
        # Mock system metrics
        mock_cpu_percent.return_value = 50.0
        mock_virtual_memory.return_value = Mock(percent=60.0)
        mock_disk_usage.return_value = Mock(percent=70.0)

        # Create health check
        health_check = HealthCheck(service_name="test_service")

        # Add an unhealthy dependency check
        def check_database():
            return DependencyStatus(
                name="database",
                status=HealthStatus.UNHEALTHY,
                details={"error": "Connection refused"},
            )

        health_check.add_dependency_check(check_database)

        # Check health
        health_status = health_check.check_health()

        # Verify overall status
        self.assertEqual(health_status["status"], HealthStatus.UNHEALTHY)

        # Verify system metrics
        self.assertEqual(health_status["system"]["status"], HealthStatus.HEALTHY)

        # Verify dependencies
        self.assertEqual(
            health_status["dependencies"]["status"], HealthStatus.UNHEALTHY
        )
        self.assertEqual(
            health_status["dependencies"]["items"][0]["status"], HealthStatus.UNHEALTHY
        )

    @patch("src.utils.health_check.psutil.cpu_percent")
    @patch("src.utils.health_check.psutil.virtual_memory")
    @patch("src.utils.health_check.psutil.disk_usage")
    def test_health_check_dependency_exception(
        self, mock_disk_usage, mock_virtual_memory, mock_cpu_percent
    ):
        """Test that HealthCheck handles exceptions in dependency checks"""
        # Mock system metrics
        mock_cpu_percent.return_value = 50.0
        mock_virtual_memory.return_value = Mock(percent=60.0)
        mock_disk_usage.return_value = Mock(percent=70.0)

        # Create health check
        health_check = HealthCheck(service_name="test_service")

        # Add a dependency check that raises an exception
        def check_database():
            raise Exception("Unexpected error")

        health_check.add_dependency_check(check_database)

        # Check health
        health_status = health_check.check_health()

        # Verify overall status
        self.assertEqual(health_status["status"], HealthStatus.UNHEALTHY)

        # Verify dependencies
        self.assertEqual(
            health_status["dependencies"]["status"], HealthStatus.UNHEALTHY
        )
        self.assertEqual(health_status["dependencies"]["items"][0]["name"], "unknown")
        self.assertEqual(
            health_status["dependencies"]["items"][0]["status"], HealthStatus.UNHEALTHY
        )
        self.assertEqual(
            health_status["dependencies"]["items"][0]["details"]["error"],
            "Unexpected error",
        )

    def test_add_health_check_endpoints(self):
        """Test that add_health_check_endpoints adds the correct endpoints to a FastAPI app"""
        # Create a FastAPI app
        app = FastAPI()

        # Create a health check
        health_check = HealthCheck(service_name="test_service")

        # Add health check endpoints
        add_health_check_endpoints(app, health_check)

        # Create a test client
        client = TestClient(app)

        # Test basic health endpoint
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})

        # Test liveness endpoint
        response = client.get("/health/liveness")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})

        # Mock health_check.check_health to return a healthy status
        health_check.check_health = Mock(return_value={"status": HealthStatus.HEALTHY})

        # Test readiness endpoint
        response = client.get("/health/readiness")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": HealthStatus.HEALTHY})

        # Test detailed health endpoint
        response = client.get("/health/detailed")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": HealthStatus.HEALTHY})

        # Mock health_check.check_health to return an unhealthy status
        health_check.check_health = Mock(
            return_value={"status": HealthStatus.UNHEALTHY}
        )

        # Test readiness endpoint with unhealthy status
        response = client.get("/health/readiness")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"status": HealthStatus.UNHEALTHY})

        # Test detailed health endpoint with unhealthy status
        response = client.get("/health/detailed")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"status": HealthStatus.UNHEALTHY})


if __name__ == "__main__":
    unittest.main()
