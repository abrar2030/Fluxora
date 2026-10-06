import numpy as np
import pytest
from ml_core.training.evaluation import (
    interval_level,
    regression_metrics,
    residual_bounds,
)


def test_perfect_prediction_has_zero_error():
    values = np.array([1.0, 2.0, 3.0, 4.0])
    metrics = regression_metrics(values, values)
    assert metrics["mean_squared_error"] == 0.0
    assert metrics["root_mean_squared_error"] == 0.0
    assert metrics["mean_absolute_error"] == 0.0
    assert metrics["r2_score"] == 1.0


def test_rmse_is_square_root_of_mse():
    metrics = regression_metrics([0.0, 0.0], [3.0, 4.0])
    assert metrics["root_mean_squared_error"] ** 2 == pytest.approx(
        metrics["mean_squared_error"]
    )


def test_residual_bounds_are_ordered():
    rng = np.random.default_rng(0)
    lower, upper = residual_bounds(rng.normal(0, 1, 1000))
    assert lower < 0 < upper


def test_interval_level_matches_quantiles():
    assert abs(interval_level() - 0.9) < 1e-9
