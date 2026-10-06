import numpy as np
import pandas as pd


def hourly_frame(
    users: tuple[int, ...] = (1,), days: int = 30, seed: int = 1
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    end = pd.Timestamp.now("UTC").tz_localize(None).floor("h")
    index = pd.date_range(end - pd.Timedelta(hours=days * 24 - 1), end, freq="h")
    rows = []
    for user in users:
        base = 40 + 10 * user
        values = (
            base
            + 15 * np.sin(index.hour / 24 * 2 * np.pi)
            + rng.normal(0, 2, len(index))
        )
        rows.append(
            pd.DataFrame(
                {
                    "timestamp": index,
                    "consumption_kwh": np.clip(values, 0, None),
                    "user_id": user,
                }
            )
        )
    return pd.concat(rows, ignore_index=True)
