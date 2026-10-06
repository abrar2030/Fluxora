import functools
import logging
import random
import time
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


def retry(
    max_attempts: int = 3,
    retry_exceptions: type[Exception] | tuple[type[Exception], ...] = (Exception,),
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
) -> Any:

    exceptions: tuple[type[Exception], ...] = (
        retry_exceptions if isinstance(retry_exceptions, tuple) else (retry_exceptions,)
    )

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Exception | None = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        sleep_time = min(
                            base_delay * (backoff_factor**attempt), max_delay
                        )
                        if jitter:
                            sleep_time = sleep_time * (0.5 + random.random())
                        logger.debug(
                            f"Retry {attempt + 1}/{max_attempts} for {func.__name__} "
                            f"after {sleep_time:.2f}s (error: {e})"
                        )
                        time.sleep(sleep_time)
            if last_exception is not None:
                raise last_exception
            raise RuntimeError("retry: exhausted attempts without exception")

        return wrapper

    return decorator


class RetryableError(Exception):
    pass


class NonRetryableError(Exception):
    pass
