import pandas as pd

from ..config import DEFAULT_GROUP_COL, DEFAULT_TARGET_COL, DEFAULT_TIME_COL


def to_utc_naive(values: pd.Series) -> pd.Series:
    return pd.to_datetime(values, utc=True).dt.tz_localize(None)


def to_hourly_series(
    df: pd.DataFrame,
    time_col: str = DEFAULT_TIME_COL,
    target_col: str = DEFAULT_TARGET_COL,
    group_col: str | None = DEFAULT_GROUP_COL,
) -> pd.DataFrame:
    use_group = bool(group_col) and group_col in df.columns
    columns = [time_col, target_col] + ([group_col] if use_group else [])
    frame = df[columns].copy()
    frame[time_col] = to_utc_naive(frame[time_col]).dt.floor("h")

    group_name: str = group_col if (use_group and group_col) else "__group__"
    if not use_group:
        frame[group_name] = 0

    totals = frame.groupby([group_name, time_col], as_index=False)[target_col].sum(
        min_count=1
    )

    parts = []
    for group_value, chunk in totals.groupby(group_name):
        index = pd.date_range(chunk[time_col].min(), chunk[time_col].max(), freq="h")
        values = chunk.set_index(time_col)[target_col].reindex(index)
        part = pd.DataFrame({time_col: index, target_col: values.to_numpy()})
        if use_group:
            part[group_col] = group_value
        parts.append(part)

    ordered = [time_col] + ([group_col] if use_group else []) + [target_col]
    if not parts:
        return pd.DataFrame(columns=ordered)
    return pd.concat(parts, ignore_index=True)[ordered]
