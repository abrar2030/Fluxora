import pandas as pd


class TestHourlySeries:
    def test_fills_gaps_with_nan(self):
        from src.data.resampling import to_hourly_series

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
        from src.data.resampling import to_hourly_series

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
        from src.data.resampling import to_hourly_series

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
        from src.data.resampling import to_hourly_series

        df = pd.DataFrame(
            {
                "timestamp": pd.to_datetime(["2024-01-01 05:00+05:00"]),
                "consumption_kwh": [1.0],
                "user_id": [1],
            }
        )
        result = to_hourly_series(df)
        assert result["timestamp"].iloc[0] == pd.Timestamp("2024-01-01 00:00")


class TestFillShortGaps:
    def test_short_gap_is_interpolated(self):
        import numpy as np
        from src.data.resampling import fill_short_gaps

        series = pd.Series([1.0, np.nan, np.nan, 4.0])
        assert fill_short_gaps(series, max_gap_hours=2).tolist() == [1.0, 2.0, 3.0, 4.0]

    def test_long_gap_is_left_entirely_missing(self):
        import numpy as np
        from src.data.resampling import fill_short_gaps

        series = pd.Series([1.0, np.nan, np.nan, np.nan, 5.0])
        result = fill_short_gaps(series, max_gap_hours=2)
        assert result.iloc[1:4].isna().all()
        assert result.iloc[0] == 1.0 and result.iloc[4] == 5.0

    def test_edges_are_never_extrapolated(self):
        import numpy as np
        from src.data.resampling import fill_short_gaps

        series = pd.Series([np.nan, 2.0, 3.0, np.nan])
        result = fill_short_gaps(series, max_gap_hours=5)
        assert np.isnan(result.iloc[0]) and np.isnan(result.iloc[3])
