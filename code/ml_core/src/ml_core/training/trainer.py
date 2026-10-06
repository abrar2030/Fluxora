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
    required_history_hours,
)
from ..data.resampling import to_hourly_series
from ..data.validation import validate_raw_data
from ..exceptions import InsufficientDataError
from ..features.builder import preprocess_data_for_model
from ..features.schema import feature_names
from ..models.bundle import ModelBundle, utc_now_iso
from .evaluation import interval_level, regression_metrics, residual_bounds

logger = logging.getLogger(__name__)


def new_model() -> RandomForestRegressor:
    return RandomForestRegressor(
        n_estimators=get_n_estimators(),
        max_depth=get_max_depth(),
        random_state=42,
        n_jobs=-1,
    )


def prepare_training_frame(
    df: pd.DataFrame,
    lags: list[int] | None = None,
    windows: list[int] | None = None,
) -> pd.DataFrame:
    if df is None or df.empty:
        raise InsufficientDataError("There is no energy data to train on.")

    raw = df.dropna(subset=[DEFAULT_TIME_COL, DEFAULT_TARGET_COL])
    if raw.empty:
        raise InsufficientDataError("There is no usable energy data to train on.")
    validate_raw_data(raw)

    hourly = to_hourly_series(raw)
    processed = preprocess_data_for_model(hourly, lags=lags, windows=windows)
    return processed.sort_values(
        [DEFAULT_TIME_COL, DEFAULT_GROUP_COL], kind="stable"
    ).reset_index(drop=True)


def train_model(
    df: pd.DataFrame,
    lags: list[int] | None = None,
    windows: list[int] | None = None,
) -> tuple[ModelBundle, dict[str, Any]]:
    lags = list(lags) if lags is not None else list(DEFAULT_LAGS)
    windows = list(windows) if windows is not None else list(DEFAULT_WINDOWS)

    processed = prepare_training_frame(df, lags=lags, windows=windows)
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

    holdout_model = new_model().fit(X_train, y_train)
    predictions = holdout_model.predict(X_test)
    residuals = y_test.to_numpy() - predictions

    metrics: dict[str, Any] = {
        **regression_metrics(y_test, predictions),
        "feature_count": len(columns),
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "user_count": int(processed[DEFAULT_GROUP_COL].nunique()),
    }

    final_model = new_model().fit(X, y)
    lower, upper = residual_bounds(residuals)

    bundle = ModelBundle(
        model=final_model,
        feature_columns=columns,
        lags=lags,
        windows=windows,
        target_col=DEFAULT_TARGET_COL,
        history_hours=required_history_hours(lags, windows),
        metrics=metrics,
        residual_lower=lower,
        residual_upper=upper,
        interval_level=interval_level(),
        trained_at=utc_now_iso(),
    )
    logger.info(
        "Model training complete. MSE: %.4f, R2: %.4f",
        metrics["mean_squared_error"],
        metrics["r2_score"],
    )
    return bundle, metrics
