import pandas as pd

from ..config import (
    DEFAULT_GROUP_COL,
    DEFAULT_LAGS,
    DEFAULT_TARGET_COL,
    DEFAULT_TIME_COL,
    DEFAULT_WINDOWS,
)
from .lags import create_lag_features, create_rolling_features
from .temporal import create_cyclical_features, create_time_series_features


def build_model_features(
    df: pd.DataFrame,
    target_col: str = DEFAULT_TARGET_COL,
    lags: list[int] | None = None,
    windows: list[int] | None = None,
    group_col: str | None = DEFAULT_GROUP_COL,
    time_col: str = DEFAULT_TIME_COL,
) -> pd.DataFrame:
    lags = lags if lags is not None else DEFAULT_LAGS
    windows = windows if windows is not None else DEFAULT_WINDOWS
    effective_group = group_col if (group_col and group_col in df.columns) else None

    df = create_time_series_features(df, time_col=time_col)
    df = create_cyclical_features(df)
    df = create_lag_features(df, target_col, lags, group_col=effective_group)
    df = create_rolling_features(df, target_col, windows, group_col=effective_group)
    return df


def preprocess_data_for_model(
    df: pd.DataFrame,
    group_col: str | None = DEFAULT_GROUP_COL,
    lags: list[int] | None = None,
    windows: list[int] | None = None,
) -> pd.DataFrame:
    df = build_model_features(df, lags=lags, windows=windows, group_col=group_col)
    return df.dropna()
