from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from sklearn.ensemble import RandomForestRegressor

from .flat_forest import FlatForest


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class ModelBundle:
    model: RandomForestRegressor
    feature_columns: list[str]
    lags: list[int]
    windows: list[int]
    target_col: str
    history_hours: int
    metrics: dict[str, Any]
    residual_lower: float  # one-step-ahead bound, equal to interval_lower[0]
    residual_upper: float  # one-step-ahead bound, equal to interval_upper[0]
    interval_level: float
    interval_edges: list[int]
    interval_lower: list[float]
    interval_upper: list[float]
    holiday_country: str
    trained_at: str
    _flat: FlatForest | None = field(default=None, repr=False, compare=False)

    @property
    def flat(self) -> FlatForest:
        if self._flat is None:
            self._flat = FlatForest(self.model)
        return self._flat

    def warm(self) -> None:
        _ = self.flat

    def describe(self) -> dict[str, Any]:
        return {
            "available": True,
            "trained_at": self.trained_at,
            "feature_count": len(self.feature_columns),
            "history_hours": self.history_hours,
            "interval_level": self.interval_level,
            "interval_horizon_hours": list(self.interval_edges),
            "holiday_country": self.holiday_country,
            "metrics": dict(self.metrics),
        }
