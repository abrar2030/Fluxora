import functools
import random
import time
from typing import Any, Callable, Tuple, Type, Union


def retry(
    max_attempts: int = 3,
    retry_exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = (
        Exception,
    ),
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
) -> Any:
    """
    Retry decorator with exponential backoff
    """

    def decorator(func: Callable) -> Callable:

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            delay = base_delay
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except retry_exceptions as e:  # type: ignore[misc]
                    last_exception = e
                    if attempt < max_attempts - 1:
                        sleep_time = min(delay * backoff_factor**attempt, max_delay)
                        if jitter:
                            sleep_time = sleep_time * (0.5 + random.random())
                        time.sleep(sleep_time)
            if last_exception:
                raise last_exception

        return wrapper

    return decorator


class RetryableError(Exception):
    """
    Base class for errors that should be retried
    """


class NonRetryableError(Exception):
    """
    Base class for errors that should not be retried
    """
