import pandas as pd
import pytest


def _index(*days: str) -> pd.DatetimeIndex:
    return pd.DatetimeIndex([pd.Timestamp(day) for day in days])


class TestHolidayCalendar:
    def test_is_holiday_is_a_model_feature(self):
        from src.features.schema import CALENDAR_FEATURES, feature_names

        assert "is_holiday" in CALENDAR_FEATURES
        assert "is_holiday" in feature_names()

    def test_us_calendar_is_the_default(self, monkeypatch):
        from src import holiday_flags

        monkeypatch.delenv("HOLIDAY_COUNTRY", raising=False)
        flags = holiday_flags(_index("2024-07-04 10:00", "2024-07-05 10:00"))
        assert flags.tolist() == [1, 0]

    def test_none_disables_holidays(self):
        from src import holiday_flags

        flags = holiday_flags(_index("2024-07-04", "2024-12-25"), country="NONE")
        assert flags.tolist() == [0, 0]

    def test_country_comes_from_environment(self, monkeypatch):
        from src import holiday_flags

        monkeypatch.setenv("HOLIDAY_COUNTRY", "none")
        assert holiday_flags(_index("2024-07-04")).tolist() == [0]

    def test_other_countries_use_the_holidays_package(self):
        pytest.importorskip("holidays")
        from src import holiday_flags

        flags = holiday_flags(
            _index("2024-03-23", "2024-03-24", "2024-07-04"), country="PK"
        )
        assert flags.tolist() == [1, 0, 0]

    def test_unknown_country_raises_configuration_error(self):
        from src import ConfigurationError, holiday_flags

        with pytest.raises(ConfigurationError):
            holiday_flags(_index("2024-07-04"), country="ZZ")

    def test_time_series_features_mark_holidays(self):
        from src.features.temporal import create_time_series_features

        df = pd.DataFrame(
            {"timestamp": pd.date_range("2024-12-25", periods=48, freq="h")}
        )
        result = create_time_series_features(df, holiday_country="US")
        assert result["is_holiday"].tolist() == [1] * 24 + [0] * 24

    def test_bundle_remembers_the_training_calendar(self):
        from src.training.trainer import train_model
        from tests.factories import hourly_frame

        bundle, metrics = train_model(hourly_frame(), holiday_country="NONE")
        assert bundle.holiday_country == "NONE"
        assert metrics["holiday_country"] == "NONE"
