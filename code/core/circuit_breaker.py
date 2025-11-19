import functools
import threading
import time
from enum import Enum
from typing import Any, Callable, Dict, Optional


class CircuitState(Enum):
    CLOSED = "CLOSED"  # Circuit is closed, requests flow through
    OPEN = "OPEN"  # Circuit is open, requests are blocked
    HALF_OPEN = "HALF_OPEN"  # Circuit is testing if it can be closed


class CircuitBreakerError(Exception):
    """
    Exception raised when a circuit breaker is open
    """


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        fallback_function: Optional[Callable] = None,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.fallback_function = fallback_function
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.lock = threading.RLock()

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)

        return wrapper

    def call(self, func: Callable, *args, **kwargs) -> Any:
        with self.lock:
            if self.state == CircuitState.OPEN:
                # Check if recovery timeout has elapsed
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    # Recovery timeout elapsed, try to close the circuit
                    self.state = CircuitState.HALF_OPEN
                else:
                    # Circuit is open, use fallback if available
                    if self.fallback_function:
                        return self.fallback_function(*args, **kwargs)
                    raise CircuitBreakerError("Circuit is open")

            try:
                result = func(*args, **kwargs)

                # If the call succeeded and the circuit was half-open, close it
                if self.state == CircuitState.HALF_OPEN:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0

                return result

            except CircuitBreakerError:
                # Re-raise CircuitBreakerError without modifying circuit state
                raise
            except Exception:
                # Record the failure
                self.failure_count += 1
                self.last_failure_time = time.time()

                # If we've reached the failure threshold, open the circuit
                if (
                    self.state == CircuitState.CLOSED
                    and self.failure_count >= self.failure_threshold
                ):
                    self.state = CircuitState.OPEN

                # If the circuit is half-open and we failed, open it again
                if self.state == CircuitState.HALF_OPEN:
                    self.state = CircuitState.OPEN

                # Use fallback if available, otherwise re-raise the exception
                if self.fallback_function:
                    return self.fallback_function(*args, **kwargs)
                raise

    def reset(self):
        """
        Reset the circuit breaker to its initial state
        """
        with self.lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.last_failure_time = 0

    def get_state(self) -> Dict:
        """
        Get the current state of the circuit breaker
        """
        with self.lock:
            return {
                "state": self.state.value,
                "failure_count": self.failure_count,
                "last_failure_time": self.last_failure_time,
            }
