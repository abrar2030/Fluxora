import functools
from typing import Any, Callable, Dict, List, Optional


class FallbackStrategy:
    """
    Base class for fallback strategies
    """

    def execute(self, *args, **kwargs) -> Any:
        """
        Execute the fallback strategy
        """
        raise NotImplementedError("Fallback strategy must implement execute method")


class CachedDataFallback(FallbackStrategy):
    """
    Fallback strategy that returns cached data
    """

    def __init__(self, cache_provider: Callable[[], Any]):
        self.cache_provider = cache_provider

    def execute(self, *args, **kwargs) -> Any:
        """
        Return cached data from the cache provider
        """
        return self.cache_provider()


class DefaultValueFallback(FallbackStrategy):
    """
    Fallback strategy that returns a default value
    """

    def __init__(self, default_value: Any):
        self.default_value = default_value

    def execute(self, *args, **kwargs) -> Any:
        """
        Return the default value
        """
        return self.default_value


class ChainedFallback(FallbackStrategy):
    """
    Fallback strategy that tries multiple strategies in sequence
    """

    def __init__(self, strategies: List[FallbackStrategy]):
        self.strategies = strategies

    def execute(self, *args, **kwargs) -> Any:
        """
        Try each strategy in sequence until one succeeds
        """
        last_exception = None

        for strategy in self.strategies:
            try:
                return strategy.execute(*args, **kwargs)
            except Exception as e:
                last_exception = e

        # If we get here, all strategies failed
        if last_exception:
            raise last_exception
        raise Exception("All fallback strategies failed")


def with_fallback(fallback_strategy: FallbackStrategy):
    """
    Decorator that applies a fallback strategy to a function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception:
                return fallback_strategy.execute(*args, **kwargs)

        return wrapper

    return decorator
