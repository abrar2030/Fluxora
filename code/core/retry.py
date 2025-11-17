import functools
import random
import time
from typing import Any, Callable, List, Optional, Type, Union


def retry(
    max_attempts: int = 3,
    retry_exceptions: Union[Type[Exception], List[Type[Exception]]] = Exception,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
):
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
                except retry_exceptions as e:
                    last_exception = e

                    # Don't sleep on the last attempt
                    if attempt < max_attempts - 1:
                        # Calculate sleep time with exponential backoff
                        sleep_time = min(delay * (backoff_factor**attempt), max_delay)

                        # Add jitter if enabled
                        if jitter:
                            sleep_time = sleep_time * (0.5 + random.random())

                        # Sleep before next attempt
                        time.sleep(sleep_time)

            # If we get here, all attempts failed
            raise last_exception

        return wrapper

    return decorator


class RetryableError(Exception):
    """
    Base class for errors that should be retried
    """

    pass


class NonRetryableError(Exception):
    """
    Base class for errors that should not be retried
    """

    pass
