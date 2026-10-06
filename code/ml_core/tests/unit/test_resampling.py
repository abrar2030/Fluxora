import pandas as pd


class TestHourlySeries:
    def test_fills_gaps_with_nan(self):
        from ml_core.data.resampling import to_hourly_series

        df = pd.DataFrame(
            {
                "timestamp": pd.to_datetime(["2024-01-01 00:10", "2024-01-01 03:20"]),
                "consumption_kwh": [1.0, 4.0],
                "user_id": [1, 1],
            }
        )
        result = to_hourly_series(df)
        assert len(result) == 4
        assert result["consumption_kwh"].isna().sum() == 2

    def test_sums_readings_within_the_same_hour(self):
        from ml_core.data.resampling import to_hourly_series

        df = pd.DataFrame(
            {
                "timestamp": pd.to_datetime(
                    ["2024-01-01 00:00", "2024-01-01 00:30", "2024-01-01 01:00"]
                ),
                "consumption_kwh": [1.0, 2.0, 5.0],
                "user_id": [1, 1, 1],
            }
        )
        result = to_hourly_series(df)
        assert result["consumption_kwh"].tolist() == [3.0, 5.0]

    def test_groups_are_independent(self):
        from ml_core.data.resampling import to_hourly_series

        df = pd.DataFrame(
            {
                "timestamp": pd.to_datetime(
                    ["2024-01-01 00:00", "2024-01-01 02:00", "2024-01-05 00:00"]
                ),
                "consumption_kwh": [1.0, 2.0, 3.0],
                "user_id": [1, 1, 2],
            }
        )
        result = to_hourly_series(df)
        assert (result["user_id"] == 1).sum() == 3
        assert (result["user_id"] == 2).sum() == 1

    def test_timezone_aware_input_is_normalised_to_utc(self):
        from ml_core.data.resampling import to_hourly_series

        df = pd.DataFrame(
            {
                "timestamp": pd.to_datetime(["2024-01-01 05:00+05:00"]),
                "consumption_kwh": [1.0],
                "user_id": [1],
            }
        )
        result = to_hourly_series(df)
        assert result["timestamp"].iloc[0] == pd.Timestamp("2024-01-01 00:00")
