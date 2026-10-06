import numpy as np
from numpy.typing import ArrayLike
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from ..config import INTERVAL_LOWER_QUANTILE, INTERVAL_UPPER_QUANTILE


def regression_metrics(y_true: ArrayLike, y_pred: ArrayLike) -> dict[str, float]:
    mse = float(mean_squared_error(y_true, y_pred))
    return {
        "mean_squared_error": mse,
        "root_mean_squared_error": float(np.sqrt(mse)),
        "mean_absolute_error": float(mean_absolute_error(y_true, y_pred)),
        "r2_score": float(r2_score(y_true, y_pred)),
    }


def residual_bounds(residuals: ArrayLike) -> tuple[float, float]:
    values = np.asarray(residuals, dtype=np.float64)
    return (
        float(np.quantile(values, INTERVAL_LOWER_QUANTILE)),
        float(np.quantile(values, INTERVAL_UPPER_QUANTILE)),
    )


def interval_level() -> float:
    return INTERVAL_UPPER_QUANTILE - INTERVAL_LOWER_QUANTILE
