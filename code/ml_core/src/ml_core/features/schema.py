from ..config import DEFAULT_LAGS, DEFAULT_TARGET_COL, DEFAULT_WINDOWS

CALENDAR_FEATURES = [
    "hour",
    "day_of_week",
    "day_of_year",
    "month",
    "is_weekend",
    "quarter",
    "hour_sin",
    "hour_cos",
    "day_of_week_sin",
    "day_of_week_cos",
    "month_sin",
    "month_cos",
]


def feature_names(
    target_col: str = DEFAULT_TARGET_COL,
    lags: list[int] | None = None,
    windows: list[int] | None = None,
) -> list[str]:
    lags = lags if lags is not None else DEFAULT_LAGS
    windows = windows if windows is not None else DEFAULT_WINDOWS
    names = list(CALENDAR_FEATURES)
    names += [f"{target_col}_lag_{lag}" for lag in lags]
    for window in windows:
        names.append(f"{target_col}_rolling_mean_{window}")
        names.append(f"{target_col}_rolling_std_{window}")
    return names
