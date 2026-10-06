import pandas as pd
import pytest


class TestFeatureEngineering:
    def test_create_time_series_features(self):
        from ml_core.features.temporal import create_time_series_features

        df = pd.DataFrame(
            {"timestamp": pd.date_range("2024-01-01", periods=5, freq="h")}
        )
        result = create_time_series_features(df)
        for col in ["hour", "day_of_week", "month", "is_weekend", "quarter"]:
            assert col in result.columns

    def test_create_lag_features(self):
        from ml_core.features.lags import create_lag_features

        df = pd.DataFrame({"consumption_kwh": range(10)})
        result = create_lag_features(df, "consumption_kwh", lags=[1, 2])
        assert "consumption_kwh_lag_1" in result.columns
        assert "consumption_kwh_lag_2" in result.columns

    def test_lag_feature_values_correct(self):
        from ml_core.features.lags import create_lag_features

        df = pd.DataFrame({"consumption_kwh": [10.0, 20.0, 30.0]})
        result = create_lag_features(df, "consumption_kwh", lags=[1])
        assert pd.isna(result["consumption_kwh_lag_1"].iloc[0])
        assert result["consumption_kwh_lag_1"].iloc[1] == 10.0
        assert result["consumption_kwh_lag_1"].iloc[2] == 20.0

    def test_create_rolling_features(self):
        from ml_core.features.lags import create_rolling_features

        df = pd.DataFrame({"consumption_kwh": range(20)})
        result = create_rolling_features(df, "consumption_kwh", windows=[3])
        assert "consumption_kwh_rolling_mean_3" in result.columns
        assert "consumption_kwh_rolling_std_3" in result.columns

    def test_rolling_mean_correct(self):
        from ml_core.features.lags import create_rolling_features

        df = pd.DataFrame({"consumption_kwh": [1.0, 2.0, 3.0, 4.0, 5.0]})
        result = create_rolling_features(df, "consumption_kwh", windows=[3])
        assert pd.isna(result["consumption_kwh_rolling_mean_3"].iloc[0])
        assert pd.isna(result["consumption_kwh_rolling_mean_3"].iloc[1])
        assert pd.isna(result["consumption_kwh_rolling_mean_3"].iloc[2])
        assert result["consumption_kwh_rolling_mean_3"].iloc[3] == pytest.approx(2.0)
        assert result["consumption_kwh_rolling_mean_3"].iloc[4] == pytest.approx(3.0)

    def test_rolling_features_do_not_include_current_row(self):
        from ml_core.features.lags import create_rolling_features

        df = pd.DataFrame({"consumption_kwh": [1.0, 2.0, 3.0, 4.0, float("nan")]})
        result = create_rolling_features(df, "consumption_kwh", windows=[3])
        assert not pd.isna(result["consumption_kwh_rolling_mean_3"].iloc[4])
        assert result["consumption_kwh_rolling_mean_3"].iloc[4] == pytest.approx(3.0)

    def test_preprocess_pipeline_drops_nan_rows(self):
        from ml_core.features.builder import preprocess_data_for_model

        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=50, freq="h"),
                "consumption_kwh": [float(i) for i in range(50)],
                "user_id": [1] * 50,
            }
        )
        result = preprocess_data_for_model(df)
        assert not result.isnull().any().any()
        assert len(result) < len(df)

    def test_preprocess_does_not_mutate_input(self):
        from ml_core.features.builder import preprocess_data_for_model

        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=30, freq="h"),
                "consumption_kwh": [float(i) for i in range(30)],
                "user_id": [1] * 30,
            }
        )
        original_cols = list(df.columns)
        preprocess_data_for_model(df)
        assert list(df.columns) == original_cols

    def test_is_weekend_correct(self):
        from ml_core.features.temporal import create_time_series_features

        df = pd.DataFrame(
            {"timestamp": pd.to_datetime(["2024-01-06", "2024-01-07", "2024-01-08"])}
        )
        result = create_time_series_features(df)
        assert result.loc[0, "is_weekend"] == 1
        assert result.loc[1, "is_weekend"] == 1
        assert result.loc[2, "is_weekend"] == 0

    def test_quarter_assignment(self):
        from ml_core.features.temporal import create_time_series_features

        df = pd.DataFrame(
            {
                "timestamp": pd.to_datetime(
                    ["2024-01-15", "2024-04-15", "2024-07-15", "2024-10-15"]
                )
            }
        )
        result = create_time_series_features(df)
        assert list(result["quarter"]) == [1, 2, 3, 4]


class TestTemporalFeatures:
    def test_cyclical_features_created(self):
        from ml_core.features.temporal import create_cyclical_features

        df = pd.DataFrame(
            {
                "hour": range(24),
                "day_of_week": [i % 7 for i in range(24)],
                "month": [(i % 12) + 1 for i in range(24)],
            }
        )
        result = create_cyclical_features(df)
        for col in [
            "hour_sin",
            "hour_cos",
            "day_of_week_sin",
            "day_of_week_cos",
            "month_sin",
            "month_cos",
        ]:
            assert col in result.columns

    def test_cyclical_values_in_range(self):
        from ml_core.features.temporal import create_cyclical_features

        df = pd.DataFrame(
            {
                "hour": range(24),
                "day_of_week": [0] * 24,
                "month": [1] * 24,
            }
        )
        result = create_cyclical_features(df)
        assert result["hour_sin"].between(-1.0, 1.0).all()
        assert result["hour_cos"].between(-1.0, 1.0).all()

    def test_hour_0_sin_is_zero(self):
        from ml_core.features.temporal import create_cyclical_features

        df = pd.DataFrame({"hour": [0], "day_of_week": [0], "month": [1]})
        result = create_cyclical_features(df)
        assert result["hour_sin"].iloc[0] == pytest.approx(0.0, abs=1e-10)
        assert result["hour_cos"].iloc[0] == pytest.approx(1.0, abs=1e-10)

    def test_calendar_features_with_timestamp_column(self):
        from ml_core.features.temporal import create_calendar_features

        df = pd.DataFrame(
            {"timestamp": pd.date_range("2024-01-01", periods=10, freq="D")}
        )
        result = create_calendar_features(df)
        assert "is_holiday" in result.columns
        assert "hour_sin" in result.columns

    def test_calendar_features_missing_column_raises(self):
        from ml_core.features.temporal import create_calendar_features

        df = pd.DataFrame({"value": [1, 2, 3]})
        with pytest.raises(ValueError):
            create_calendar_features(df)

    def test_cyclical_does_not_mutate_input(self):
        from ml_core.features.temporal import create_cyclical_features

        df = pd.DataFrame({"hour": [0, 6, 12, 18]})
        original_cols = list(df.columns)
        create_cyclical_features(df)
        assert list(df.columns) == original_cols
