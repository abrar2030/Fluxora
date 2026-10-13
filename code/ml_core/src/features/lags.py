import pandas as pd


def create_lag_features(
    df: pd.DataFrame,
    target_col: str,
    lags: list[int],
    group_col: str | None = None,
) -> pd.DataFrame:
    df = df.copy()
    use_group = bool(group_col) and group_col in df.columns
    for lag in lags:
        column = f"{target_col}_lag_{lag}"
        if use_group:
            df[column] = df.groupby(group_col)[target_col].shift(lag)
        else:
            df[column] = df[target_col].shift(lag)
    return df


def create_rolling_features(
    df: pd.DataFrame,
    target_col: str,
    windows: list[int],
    group_col: str | None = None,
) -> pd.DataFrame:
    df = df.copy()
    use_group = bool(group_col) and group_col in df.columns
    for window in windows:
        mean_col = f"{target_col}_rolling_mean_{window}"
        std_col = f"{target_col}_rolling_std_{window}"
        if use_group:
            grouped = df.groupby(group_col)[target_col]
            df[mean_col] = grouped.transform(
                lambda s, w=window: s.shift(1).rolling(window=w).mean()
            )
            df[std_col] = grouped.transform(
                lambda s, w=window: s.shift(1).rolling(window=w).std()
            )
        else:
            shifted = df[target_col].shift(1)
            df[mean_col] = shifted.rolling(window=window).mean()
            df[std_col] = shifted.rolling(window=window).std()
    return df
