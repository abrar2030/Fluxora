import numpy as np
import pandas as pd

from ..config import DEFAULT_TIME_COL
from .holiday_calendar import holiday_flags


def create_cyclical_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "hour" in df.columns:
        df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
        df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
    if "day_of_week" in df.columns:
        df["day_of_week_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
        df["day_of_week_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)
    if "month" in df.columns:
        df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
        df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
    return df


def create_calendar_features(
    df: pd.DataFrame, holiday_country: str | None = None
) -> pd.DataFrame:
    df = df.copy()
    if not isinstance(df.index, pd.DatetimeIndex):
        if "timestamp" not in df.columns:
            raise ValueError(
                "DataFrame must have a DatetimeIndex or a 'timestamp' column."
            )
        df = df.set_index(pd.to_datetime(df["timestamp"]))

    df["is_holiday"] = holiday_flags(df.index, holiday_country)

    if "hour" not in df.columns:
        df["hour"] = df.index.hour
    if "day_of_week" not in df.columns:
        df["day_of_week"] = df.index.dayofweek
    if "month" not in df.columns:
        df["month"] = df.index.month

    return create_cyclical_features(df)


def create_time_series_features(
    df: pd.DataFrame,
    time_col: str = DEFAULT_TIME_COL,
    holiday_country: str | None = None,
) -> pd.DataFrame:
    df = df.copy()
    df[time_col] = pd.to_datetime(df[time_col])
    df["hour"] = df[time_col].dt.hour
    df["day_of_week"] = df[time_col].dt.dayofweek
    df["day_of_year"] = df[time_col].dt.dayofyear
    df["month"] = df[time_col].dt.month
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    df["is_holiday"] = holiday_flags(df[time_col], holiday_country)
    df["quarter"] = df[time_col].dt.quarter
    return df
