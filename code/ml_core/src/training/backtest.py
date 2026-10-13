import logging
from datetime import datetime

import numpy as np
import pandas as pd

from ..config import (
    BACKTEST_MAX_GROUPS,
    BACKTEST_ORIGINS_PER_GROUP,
    DEFAULT_GROUP_COL,
    DEFAULT_TARGET_COL,
    DEFAULT_TIME_COL,
    INTERVAL_HORIZON_EDGES,
    MIN_BUCKET_RESIDUALS,
)
from ..exceptions import InsufficientHistoryError
from ..inference.forecaster import forecast
from ..models.bundle import ModelBundle
from .evaluation import residual_bounds

logger = logging.getLogger(__name__)


def _spread(values: list, count: int) -> list:
    if len(values) <= count:
        return list(values)
    positions = np.linspace(0, len(values) - 1, count).round().astype(int)
    return [values[i] for i in sorted(set(positions.tolist()))]


def collect_horizon_residuals(
    bundle: ModelBundle,
    hourly: pd.DataFrame,
    holdout_start: pd.Timestamp,
    max_horizon: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Run recursive forecasts from several holdout origins.

    Returns ``(horizons, residuals)`` where ``residuals = actual - predicted`` and
    ``horizons`` counts hours ahead of the forecast origin. These are the errors
    the API really produces: every step after the first feeds on earlier
    predictions, so the error grows with the horizon.
    """
    use_group = DEFAULT_GROUP_COL in hourly.columns
    observed = hourly.dropna(subset=[DEFAULT_TARGET_COL])
    groups = (
        _spread(sorted(observed[DEFAULT_GROUP_COL].unique()), BACKTEST_MAX_GROUPS)
        if use_group
        else [None]
    )

    horizons: list[np.ndarray] = []
    residuals: list[np.ndarray] = []
    for group in groups:
        frame = (
            observed[observed[DEFAULT_GROUP_COL] == group] if use_group else observed
        )
        frame = frame[[DEFAULT_TIME_COL, DEFAULT_TARGET_COL]]
        actual = frame.set_index(DEFAULT_TIME_COL)[DEFAULT_TARGET_COL]
        candidates = list(
            frame.loc[frame[DEFAULT_TIME_COL] >= holdout_start, DEFAULT_TIME_COL]
        )
        for origin in _spread(candidates, BACKTEST_ORIGINS_PER_GROUP):
            history = frame[frame[DEFAULT_TIME_COL] <= origin]
            try:
                predicted = forecast(
                    bundle, history, max_horizon, now=_as_datetime(origin)
                )
            except InsufficientHistoryError:
                continue
            predicted = predicted.set_index(DEFAULT_TIME_COL)["predicted_consumption"]
            common = predicted.index.intersection(actual.index)
            if common.empty:
                continue
            steps = ((common - origin) / pd.Timedelta(hours=1)).to_numpy()
            horizons.append(steps.astype(int))
            residuals.append((actual.loc[common] - predicted.loc[common]).to_numpy())

    if not horizons:
        return np.array([], dtype=int), np.array([], dtype=float)
    return np.concatenate(horizons), np.concatenate(residuals)


def _as_datetime(stamp: pd.Timestamp) -> datetime:
    return stamp.to_pydatetime()


def horizon_intervals(
    bundle: ModelBundle,
    hourly: pd.DataFrame,
    holdout_start: pd.Timestamp,
    one_step_residuals: np.ndarray,
) -> tuple[list[int], list[float], list[float]]:
    """Calibrate residual bounds per horizon bucket.

    The first bucket uses the one-step holdout residuals. Later buckets use the
    backtest residuals; a bucket with too few samples inherits its predecessor,
    and bounds are forced to widen monotonically with the horizon.
    """
    edges = list(INTERVAL_HORIZON_EDGES)
    lower, upper = residual_bounds(one_step_residuals)
    lowers, uppers = [lower], [upper]

    horizons, residuals = collect_horizon_residuals(
        bundle, hourly, holdout_start, edges[-1]
    )
    previous = 0
    for edge in edges[1:]:
        mask = (horizons > previous) & (horizons <= edge)
        previous = edge
        if int(mask.sum()) >= MIN_BUCKET_RESIDUALS:
            bucket_lower, bucket_upper = residual_bounds(residuals[mask])
        else:
            bucket_lower, bucket_upper = lowers[-1], uppers[-1]
        lowers.append(min(bucket_lower, lowers[-1]))
        uppers.append(max(bucket_upper, uppers[-1]))

    logger.info(
        "Calibrated prediction intervals from %d backtest residuals.", len(residuals)
    )
    return edges, lowers, uppers
