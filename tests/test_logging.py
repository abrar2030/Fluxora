import json
import logging
import os
import sys
import unittest
from io import StringIO
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fluxora.core.logging_framework import (
    JsonFormatter,
    clear_request_context,
    get_correlation_id,
    get_request_id,
    set_request_context,
    setup_logging,
)


class TestLoggingFramework(unittest.TestCase):

    def setUp(self) -> Any:
        clear_request_context()
        for logger in [logging.getLogger(), logging.getLogger("test_service")]:
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)

    def test_json_formatter(self) -> Any:
        """Test that JsonFormatter formats log records as JSON"""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test_file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        formatted = formatter.format(record)
        log_data = json.loads(formatted)
        self.assertEqual(log_data["level"], "INFO")
        self.assertEqual(log_data["message"], "Test message")
        self.assertEqual(log_data["logger"], "test_logger")
        self.assertEqual(log_data["path"], "test_file.py")
        self.assertEqual(log_data["line"], 42)

    def test_json_formatter_with_exception(self) -> Any:
        """Test that JsonFormatter includes exception information"""
        formatter = JsonFormatter()
        try:
            raise ValueError("Test exception")
        except ValueError:
            exc_info = sys.exc_info()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="test_file.py",
            lineno=42,
            msg="Exception occurred",
            args=(),
            exc_info=exc_info,
        )
        formatted = formatter.format(record)
        log_data = json.loads(formatted)
        self.assertIn("exception", log_data)
        self.assertEqual(log_data["exception"]["type"], "ValueError")
        self.assertEqual(log_data["exception"]["message"], "Test exception")
        self.assertIsInstance(log_data["exception"]["traceback"], list)

    def test_json_formatter_with_extra(self) -> Any:
        """Test that JsonFormatter includes extra fields"""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test_file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.user_id = "user123"
        record.request_method = "GET"
        formatted = formatter.format(record)
        log_data = json.loads(formatted)
        self.assertEqual(log_data["user_id"], "user123")
        self.assertEqual(log_data["request_method"], "GET")

    @patch("sys.stdout", new_callable=StringIO)
    def test_setup_logging(self, mock_stdout: Any) -> Any:
        """Test that setup_logging creates a logger with the correct configuration"""
        for handler in logging.getLogger().handlers[:]:
            logging.getLogger().removeHandler(handler)
        logger = setup_logging(service_name="test_service", log_level=logging.INFO)
        self.assertEqual(logger.name, "test_service")
        self.assertEqual(logger.level, logging.INFO)
        self.assertEqual(len(logger.handlers), 1)
        handler = logger.handlers[0]
        self.assertIsInstance(handler, logging.StreamHandler)
        self.assertEqual(handler.level, logging.INFO)
        self.assertIsInstance(handler.formatter, JsonFormatter)
        logger.info("Test log message")
        output = mock_stdout.getvalue()
        log_data = json.loads(output)
        self.assertEqual(log_data["level"], "INFO")
        self.assertEqual(log_data["message"], "Test log message")
        self.assertEqual(log_data["logger"], "test_service")

    def test_request_context(self) -> Any:
        """Test setting and getting request context"""
        set_request_context(
            request_id="req123", user_id="user456", correlation_id="corr789"
        )
        request_id = get_request_id()
        correlation_id = get_correlation_id()
        self.assertEqual(request_id, "req123")
        self.assertEqual(correlation_id, "corr789")
        clear_request_context()
        self.assertIsNone(get_request_id())
        self.assertIsNone(get_correlation_id())

    def test_auto_generated_request_id(self) -> Any:
        """Test that request_id is auto-generated if not provided"""
        set_request_context(user_id="user456")
        request_id = get_request_id()
        correlation_id = get_correlation_id()
        self.assertIsNotNone(request_id)
        self.assertIsInstance(request_id, str)
        self.assertEqual(correlation_id, request_id)

    @patch("sys.stdout", new_callable=StringIO)
    def test_logging_with_request_context(self, mock_stdout: Any) -> Any:
        """Test that request context is included in log messages"""
        logger = setup_logging(service_name="test_service")
        set_request_context(
            request_id="req123", user_id="user456", correlation_id="corr789"
        )
        logger.info("Test message with context")
        output = mock_stdout.getvalue()
        log_data = json.loads(output)
        self.assertEqual(log_data["request_id"], "req123")
        self.assertEqual(log_data["user_id"], "user456")
        self.assertEqual(log_data["correlation_id"], "corr789")


if __name__ == "__main__":
    unittest.main()
