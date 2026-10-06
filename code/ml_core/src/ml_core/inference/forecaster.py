from datetime import datetime, timezone

import numpy as np
import pandas as pd

from ..config import DEFAULT_TIME_COL, MAX_HISTORY_GAP_HOURS, MAX_MISSING_HISTORY_RATIO
from ..data.resampling import to_hourly_series
from ..exceptions import InsufficientHistoryError
from ..features.schema import CALENDAR_FEATURES
from ..features.temporal import create_cyclical_features, create_time_series_features
from ..models.bundle import ModelBundle


def _current_hour(now: datetime | None) -> pd.Timestamp:
    moment = now if now is not None else datetime.now(timezone.utc)
    stamp = pd.Timestamp(moment)
    if stamp.tzinfo is not None:
        stamp = stamp.tz_convert("UTC").tz_localize(None)
    return stamp.floor("h")


def _recent_window(series: pd.Series, hours: int) -> np.ndarray:
    window = series.iloc[-hours:]
    if len(window) < hours:
        raise InsufficientHistoryError(
            f"At least {hours} hours of recent history are required to forecast."
        )
    missing = float(window.isna().mean())
    if missing > MAX_MISSING_HISTORY_RATIO:
        raise InsufficientHistoryError(
            "The recent history has too many missing hours to forecast reliably."
        )
    filled = window.interpolate(limit_direction="both")
    return np.array(filled.to_numpy(dtype=np.float64), dtype=np.float64)


def _calendar_matrix(index: pd.DatetimeIndex) -> np.ndarray:
    frame = pd.DataFrame({DEFAULT_TIME_COL: index})
    frame = create_time_series_features(frame)
    frame = create_cyclical_features(frame)
    return np.asarray(frame[CALENDAR_FEATURES].to_numpy(dtype=np.float64))


def forecast(
    bundle: ModelBundle,
    history: pd.DataFrame,
    horizon_hours: int,
    now: datetime | None = None,
) -> pd.DataFrame:
    if horizon_hours < 1:
        raise ValueError("horizon_hours must be at least 1.")

    current = _current_hour(now)
    start = current + pd.Timedelta(hours=1)

    hourly = to_hourly_series(history, group_col=None)
    hourly = hourly[hourly[DEFAULT_TIME_COL] <= current]
    hourly = hourly.dropna(subset=[bundle.target_col])
    if hourly.empty:
        raise InsufficientHistoryError("No recent consumption history is available.")

    last_observed = hourly[DEFAULT_TIME_COL].max()
    gap_hours = int((start - last_observed) / pd.Timedelta(hours=1)) - 1
    if gap_hours > MAX_HISTORY_GAP_HOURS:
        raise InsufficientHistoryError(
            f"The latest reading is {gap_hours} hours old; forecasting needs data "
            f"from the last {MAX_HISTORY_GAP_HOURS} hours."
        )

    full_index = pd.date_range(hourly[DEFAULT_TIME_COL].min(), last_observed, freq="h")
    series = (
        hourly.set_index(DEFAULT_TIME_COL)[bundle.target_col]
        .reindex(full_index)
        .astype(float)
    )
    recent = _recent_window(series, bundle.history_hours)

    first_step = last_observed + pd.Timedelta(hours=1)
    last_step = start + pd.Timedelta(hours=horizon_hours - 1)
    step_index = pd.date_range(first_step, last_step, freq="h")
    calendar = _calendar_matrix(step_index)

    calendar_width = len(CALENDAR_FEATURES)
    lag_count = len(bundle.lags)
    window_count = len(bundle.windows)
    width = calendar_width + lag_count + 2 * window_count

    buffer = np.concatenate([recent, np.zeros(len(step_index))])
    history_len = len(recent)
    vector = np.zeros(width, dtype=np.float64)
    predictions = np.zeros(len(step_index), dtype=np.float64)
    flat = bundle.flat

    for i in range(len(step_index)):
        position = history_len + i
        vector[:calendar_width] = calendar[i]
        offset = calendar_width
        for lag in bundle.lags:
            vector[offset] = buffer[position - lag]
            offset += 1
        for window in bundle.windows:
            window_start = position - window
            segment = buffer[window_start:position]
            vector[offset] = segment.mean()
            vector[offset + 1] = segment.std(ddof=1)
            offset += 2
        value = max(flat.predict_one(vector), 0.0)
        predictions[i] = value
        buffer[position] = value

    keep = step_index >= start
    timestamps = step_index[keep]
    values = predictions[keep]
    lower = np.maximum(values + bundle.residual_lower, 0.0)
    upper = np.maximum(values + bundle.residual_upper, values)

    return pd.DataFrame(
        {
            DEFAULT_TIME_COL: timestamps,
            "predicted_consumption": values,
            "lower": np.minimum(lower, values),
            "upper": upper,
        }
    )
