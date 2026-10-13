import os

DEFAULT_LAGS: list[int] = [1, 2, 24]
DEFAULT_WINDOWS: list[int] = [3, 24 * 7]
DEFAULT_TARGET_COL = "consumption_kwh"
DEFAULT_GROUP_COL = "user_id"
DEFAULT_TIME_COL = "timestamp"

MIN_TRAINING_SAMPLES = 100
MAX_HISTORY_GAP_HOURS = 24 * 7
MAX_MISSING_HISTORY_RATIO = 0.2
HOLDOUT_FRACTION = 0.2
INTERVAL_LOWER_QUANTILE = 0.05
INTERVAL_UPPER_QUANTILE = 0.95
MODEL_SCHEMA_VERSION = 3

# Missing hourly readings are linearly interpolated only when the run of missing
# hours is at most this long. The same limit is applied when building training
# features and when preparing the history for a forecast, so the model never
# sees a kind of gap at inference time that it did not see during training.
MAX_FILL_GAP_HOURS = 6

# Prediction intervals are calibrated per forecast horizon. Each value is the
# last horizon (in hours ahead) covered by one calibration bucket; horizons
# beyond the final edge reuse the final bucket.
INTERVAL_HORIZON_EDGES: list[int] = [1, 3, 6, 12, 24, 48, 96, 168]
BACKTEST_MAX_GROUPS = 3
BACKTEST_ORIGINS_PER_GROUP = 4
MIN_BUCKET_RESIDUALS = 30

DEFAULT_HOLIDAY_COUNTRY = "US"


def get_model_path() -> str:
    return os.path.abspath(os.getenv("MODEL_PATH", "fluxora_model.joblib"))


def get_n_estimators() -> int:
    return max(1, int(os.getenv("MODEL_N_ESTIMATORS", "100")))


def get_max_depth() -> int | None:
    value = os.getenv("MODEL_MAX_DEPTH")
    return int(value) if value else None


def required_history_hours(lags: list[int], windows: list[int]) -> int:
    return max(list(lags) + list(windows))


def get_refit_on_full_data() -> bool:
    value = os.getenv("MODEL_REFIT_FULL_DATA", "true").strip().lower()
    return value not in {"0", "false", "no", "off"}


def get_holiday_country() -> str:
    """Holiday calendar used for the ``is_holiday`` feature.

    ``US`` (default) uses the US federal calendar bundled with pandas. ``NONE``
    disables holidays. Any other ISO 3166 code (e.g. ``PK``, ``GB``) needs the
    optional ``holidays`` package.
    """
    value = os.getenv("HOLIDAY_COUNTRY", DEFAULT_HOLIDAY_COUNTRY).strip().upper()
    return value or "NONE"
