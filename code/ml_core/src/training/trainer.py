import logging
from typing import Any

import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from ..config import (
    DEFAULT_GROUP_COL,
    DEFAULT_LAGS,
    DEFAULT_TARGET_COL,
    DEFAULT_TIME_COL,
    DEFAULT_WINDOWS,
    HOLDOUT_FRACTION,
    MIN_TRAINING_SAMPLES,
    get_max_depth,
    get_n_estimators,
    get_refit_on_full_data,
    required_history_hours,
)
from ..data.resampling import fill_short_gaps, to_hourly_series
from ..data.validation import validate_raw_data
from ..exceptions import InsufficientDataError
from ..features.builder import preprocess_data_for_model
from ..features.holiday_calendar import resolve_country
from ..features.schema import feature_names
from ..models.bundle import ModelBundle, utc_now_iso
from .backtest import horizon_intervals
from .evaluation import interval_level, regression_metrics, residual_bounds

OBSERVED_COL = "_observed"

logger = logging.getLogger(__name__)


def new_model() -> RandomForestRegressor:
    return RandomForestRegressor(
        n_estimators=get_n_estimators(),
        max_depth=get_max_depth(),
        random_state=42,
        n_jobs=-1,
    )


def _hourly_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Validate raw readings and regularise them to one row per user per hour."""
    if df is None or df.empty:
        raise InsufficientDataError("There is no energy data to train on.")

    validation = validate_raw_data(df)
    for warning in validation.warnings:
        logger.warning("Training data: %s", warning)

    raw = df.dropna(subset=[DEFAULT_TIME_COL, DEFAULT_TARGET_COL])
    if raw.empty:
        raise InsufficientDataError("There is no usable energy data to train on.")
    return to_hourly_series(raw)


def _training_frame(
    hourly: pd.DataFrame,
    lags: list[int] | None,
    windows: list[int] | None,
    holiday_country: str | None,
) -> pd.DataFrame:
    """Build features the same way forecasting sees its history.

    Short gaps are interpolated (see ``fill_short_gaps``) so lag and rolling
    features exist around them, exactly as they do at inference time. Rows whose
    own target was interpolated are not used as training targets.
    """
    frame = hourly.copy()
    frame[OBSERVED_COL] = frame[DEFAULT_TARGET_COL].notna()
    if DEFAULT_GROUP_COL in frame.columns:
        frame[DEFAULT_TARGET_COL] = frame.groupby(DEFAULT_GROUP_COL)[
            DEFAULT_TARGET_COL
        ].transform(fill_short_gaps)
    else:
        frame[DEFAULT_TARGET_COL] = fill_short_gaps(frame[DEFAULT_TARGET_COL])

    processed = preprocess_data_for_model(
        frame, lags=lags, windows=windows, holiday_country=holiday_country
    )
    processed = processed[processed[OBSERVED_COL]].drop(columns=[OBSERVED_COL])
    return processed.sort_values(
        [DEFAULT_TIME_COL, DEFAULT_GROUP_COL], kind="stable"
    ).reset_index(drop=True)


def prepare_training_frame(
    df: pd.DataFrame,
    lags: list[int] | None = None,
    windows: list[int] | None = None,
    holiday_country: str | None = None,
) -> pd.DataFrame:
    hourly = _hourly_frame(df)
    return _training_frame(hourly, lags, windows, resolve_country(holiday_country))


def train_model(
    df: pd.DataFrame,
    lags: list[int] | None = None,
    windows: list[int] | None = None,
    holiday_country: str | None = None,
    refit_on_full_data: bool | None = None,
) -> tuple[ModelBundle, dict[str, Any]]:
    """Train and evaluate a forecasting model.

    A model is first fitted on the earlier 80% of the timeline and scored on the
    most recent 20%; those holdout errors calibrate the prediction intervals.
    With ``refit_on_full_data`` (default, ``MODEL_REFIT_FULL_DATA``) a second
    model is then fitted on all rows, which uses the newest data but doubles the
    fitting time. Disable it to keep the holdout model as the final model.
    """
    lags = list(lags) if lags is not None else list(DEFAULT_LAGS)
    windows = list(windows) if windows is not None else list(DEFAULT_WINDOWS)
    country = resolve_country(holiday_country)
    refit = (
        get_refit_on_full_data() if refit_on_full_data is None else refit_on_full_data
    )

    hourly = _hourly_frame(df)
    processed = _training_frame(hourly, lags, windows, country)
    columns = feature_names(DEFAULT_TARGET_COL, lags, windows)

    if len(processed) < MIN_TRAINING_SAMPLES:
        raise InsufficientDataError(
            f"At least {MIN_TRAINING_SAMPLES} hourly samples with complete history "
            f"are required to train; found {len(processed)}."
        )

    X = processed[columns]
    y = processed[DEFAULT_TARGET_COL]

    split = int(len(processed) * (1.0 - HOLDOUT_FRACTION))
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]
    holdout_start = processed[DEFAULT_TIME_COL].iloc[split]

    holdout_model = new_model().fit(X_train, y_train)
    predictions = holdout_model.predict(X_test)
    residuals = y_test.to_numpy() - predictions

    metrics: dict[str, Any] = {
        **regression_metrics(y_test, predictions),
        "feature_count": len(columns),
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "user_count": int(processed[DEFAULT_GROUP_COL].nunique()),
        "refit_on_full_data": refit,
        "holiday_country": country,
    }

    final_model = new_model().fit(X, y) if refit else holdout_model
    history_hours = required_history_hours(lags, windows)

    def make_bundle(
        model: RandomForestRegressor,
        edges: list[int],
        lowers: list[float],
        uppers: list[float],
    ) -> ModelBundle:
        return ModelBundle(
            model=model,
            feature_columns=columns,
            lags=lags,
            windows=windows,
            target_col=DEFAULT_TARGET_COL,
            history_hours=history_hours,
            metrics=metrics,
            residual_lower=lowers[0],
            residual_upper=uppers[0],
            interval_level=interval_level(),
            interval_edges=edges,
            interval_lower=lowers,
            interval_upper=uppers,
            holiday_country=country,
            trained_at=utc_now_iso(),
        )

    # Backtest recursive forecasts with the holdout model so that interval width
    # reflects error accumulation over the horizon, not just one-step error.
    lower, upper = residual_bounds(residuals)
    holdout_bundle = make_bundle(holdout_model, [1], [lower], [upper])
    edges, lowers, uppers = horizon_intervals(
        holdout_bundle, hourly, holdout_start, residuals
    )
    bundle = make_bundle(final_model, edges, lowers, uppers)

    logger.info(
        "Model training complete. MSE: %.4f, R2: %.4f",
        metrics["mean_squared_error"],
        metrics["r2_score"],
    )
    return bundle, metrics
