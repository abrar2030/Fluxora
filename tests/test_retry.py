import unittest
import sys
import os
import time
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.retry import retry, RetryableError, NonRetryableError

class TestRetry(unittest.TestCase):
    def test_successful_call(self):
        """Test that a successful call returns the correct result"""
        @retry(max_attempts=3)
        def success_func():
            return "success"
        
        result = success_func()
        self.assertEqual(result, "success")
    
    def test_retry_on_exception(self):
        """Test that the function is retried on exception"""
        mock = MagicMock()
        
        @retry(max_attempts=3)
        def fail_then_succeed():
            if mock.call_count < 2:
                mock()
                raise Exception("Temporary failure")
            return "success"
        
        result = fail_then_succeed()
        self.assertEqual(result, "success")
        self.assertEqual(mock.call_count, 2)
    
    def test_max_attempts_reached(self):
        """Test that the function fails after max attempts"""
        mock = MagicMock()
        
        @retry(max_attempts=3)
        def always_fail():
            mock()
            raise Exception("Always fails")
        
        with self.assertRaises(Exception):
            always_fail()
        
        self.assertEqual(mock.call_count, 3)
    
    def test_retry_specific_exceptions(self):
        """Test that only specified exceptions trigger retry"""
        mock_retry = MagicMock()
        mock_no_retry = MagicMock()
        
        @retry(max_attempts=3, retry_exceptions=RetryableError)
        def selective_retry():
            if mock_retry.call_count < 1:
                mock_retry()
                raise RetryableError("Should retry")
            elif mock_no_retry.call_count < 1:
                mock_no_retry()
                raise NonRetryableError("Should not retry")
            return "success"
        
        with self.assertRaises(NonRetryableError):
            selective_retry()
        
        self.assertEqual(mock_retry.call_count, 1)
        self.assertEqual(mock_no_retry.call_count, 1)
    
    def test_exponential_backoff(self):
        """Test that exponential backoff increases delay between retries"""
        mock = MagicMock()
        start_time = time.time()
        
        @retry(max_attempts=3, base_delay=0.1, backoff_factor=2, jitter=False)
        def always_fail():
            mock()
            raise Exception("Always fails")
        
        with self.assertRaises(Exception):
            always_fail()
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Expected delay: 0 + 0.1 + 0.2 = 0.3 seconds minimum
        self.assertGreaterEqual(elapsed_time, 0.3)
        self.assertEqual(mock.call_count, 3)
    
    def test_max_delay(self):
        """Test that delay is capped at max_delay"""
        mock = MagicMock()
        start_time = time.time()
        
        @retry(max_attempts=3, base_delay=0.1, backoff_factor=10, max_delay=0.2, jitter=False)
        def always_fail():
            mock()
            raise Exception("Always fails")
        
        with self.assertRaises(Exception):
            always_fail()
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Expected delay: 0 + 0.1 + 0.2 = 0.3 seconds minimum
        # Without max_delay it would be 0 + 0.1 + 1.0 = 1.1 seconds
        self.assertGreaterEqual(elapsed_time, 0.3)
        self.assertLess(elapsed_time, 1.0)  # Should be less than what it would be without max_delay
        self.assertEqual(mock.call_count, 3)

if __name__ == '__main__':
    unittest.main()
