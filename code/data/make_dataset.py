import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


def generate_mock_data(
    start_date: str = "2023-01-01", end_date: str = "2023-01-31", num_meters: int = 5
) -> pd.DataFrame:
    """
    Generates mock time-series energy consumption data for training.

    Args:
        start_date: Start date for the time series.
        end_date: End date for the time series.
        num_meters: Number of unique meters to simulate.

    Returns:
        A pandas DataFrame with columns: timestamp, meter_id, target, and context features.
    """

    # Generate a time range
    timestamps = pd.date_range(start=start_date, end=end_date, freq="H")

    # Generate meter IDs
    meter_ids = [f"meter_{i+1}" for i in range(num_meters)]

    # Create a base DataFrame
    df = pd.DataFrame(
        {
            "timestamp": np.tile(timestamps, num_meters),
            "meter_id": np.repeat(meter_ids, len(timestamps)),
        }
    )

    # Generate a base energy consumption (target) with a daily and weekly cycle
    base_consumption = 50 + 10 * np.sin(2 * np.pi * df["timestamp"].dt.hour / 24)
    base_consumption += 5 * np.sin(2 * np.pi * df["timestamp"].dt.dayofweek / 7)

    # Add meter-specific offsets and noise
    for i, meter_id in enumerate(meter_ids):
        mask = df["meter_id"] == meter_id
        df.loc[mask, "target"] = (
            base_consumption[mask] + (i * 5) + np.random.normal(0, 2, size=mask.sum())
        )

    # Ensure all targets are positive
    df["target"] = df["target"].clip(lower=0)

    # Add context features (e.g., temperature, humidity)
    df["temperature"] = (
        15
        + 10 * np.sin(2 * np.pi * df["timestamp"].dt.dayofyear / 365)
        + np.random.normal(0, 1, size=len(df))
    )
    df["humidity"] = (
        60
        + 15 * np.cos(2 * np.pi * df["timestamp"].dt.dayofyear / 365)
        + np.random.normal(0, 2, size=len(df))
    )

    return df.sort_values(["meter_id", "timestamp"]).reset_index(drop=True)


def make_dataset(output_path: str = "data/raw/mock_data.csv"):
    """
    Generates the mock dataset and saves it to the specified path.
    """
    print(f"Generating mock dataset...")
    data = generate_mock_data()

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save the data
    data.to_csv(output_path, index=False)
    print(f"Mock dataset saved to {output_path}")


if __name__ == "__main__":
    # Assuming the project root is the current working directory
    make_dataset(output_path="../data/raw/mock_data.csv")
