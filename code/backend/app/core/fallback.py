import functools
from collections.abc import Callable
from typing import Any


class FallbackStrategy:

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("Fallback strategy must implement execute method")


class CachedDataFallback(FallbackStrategy):

    def __init__(self, cache_provider: Callable[[], Any]) -> None:
        self.cache_provider = cache_provider

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        return self.cache_provider()


class DefaultValueFallback(FallbackStrategy):

    def __init__(self, default_value: Any) -> None:
        self.default_value = default_value

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        return self.default_value


class ChainedFallback(FallbackStrategy):

    def __init__(self, strategies: list[FallbackStrategy]) -> None:
        self.strategies = strategies

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        last_exception: Exception | None = None
        for strategy in self.strategies:
            try:
                return strategy.execute(*args, **kwargs)
            except Exception as e:
                last_exception = e
        if last_exception is not None:
            raise last_exception
        raise RuntimeError("All fallback strategies failed")


def with_fallback(fallback_strategy: FallbackStrategy) -> Any:

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception:
                return fallback_strategy.execute(*args, **kwargs)

        return wrapper

    return decorator
