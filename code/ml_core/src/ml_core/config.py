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
MODEL_SCHEMA_VERSION = 2


def get_model_path() -> str:
    return os.path.abspath(os.getenv("MODEL_PATH", "fluxora_model.joblib"))


def get_n_estimators() -> int:
    return max(1, int(os.getenv("MODEL_N_ESTIMATORS", "100")))


def get_max_depth() -> int | None:
    value = os.getenv("MODEL_MAX_DEPTH")
    return int(value) if value else None


def required_history_hours(lags: list[int], windows: list[int]) -> int:
    return max(list(lags) + list(windows))
