import pandas as pd
import pytest
from tests.factories import hourly_frame


class TestForecasting:
    def _bundle(self):
        from ml_core.training.trainer import train_model

        frame = hourly_frame(users=(1, 2))
        bundle, _ = train_model(frame)
        return bundle, frame[frame["user_id"] == 1]

    def test_forecast_length_and_ordering(self):
        from ml_core import forecast

        bundle, history = self._bundle()
        result = forecast(bundle, history, horizon_hours=48)
        assert len(result) == 48
        assert result["timestamp"].is_monotonic_increasing
        assert (result["lower"] <= result["predicted_consumption"]).all()
        assert (result["predicted_consumption"] <= result["upper"]).all()
        assert (result["lower"] >= 0).all()

    def test_forecast_starts_after_the_current_hour(self):
        from datetime import datetime, timezone

        from ml_core import forecast

        bundle, history = self._bundle()
        result = forecast(bundle, history, horizon_hours=3)
        current = pd.Timestamp(datetime.now(timezone.utc)).tz_localize(None).floor("h")
        assert result["timestamp"].iloc[0] == current + pd.Timedelta(hours=1)

    def test_forecast_tracks_the_daily_cycle(self):
        from ml_core import forecast

        bundle, history = self._bundle()
        result = forecast(bundle, history, horizon_hours=72)
        assert result["predicted_consumption"].nunique() > 20
        assert result["predicted_consumption"].std() > 3

    def test_forecast_requires_enough_history(self):
        from ml_core import InsufficientHistoryError, forecast

        bundle, history = self._bundle()
        with pytest.raises(InsufficientHistoryError):
            forecast(bundle, history.tail(30), horizon_hours=24)

    def test_forecast_rejects_stale_history(self):
        from ml_core import InsufficientHistoryError, forecast

        bundle, history = self._bundle()
        stale = history.copy()
        stale["timestamp"] = stale["timestamp"] - pd.Timedelta(days=30)
        with pytest.raises(InsufficientHistoryError):
            forecast(bundle, stale, horizon_hours=24)

    def test_forecast_rejects_empty_history(self):
        from ml_core import InsufficientHistoryError, forecast

        bundle, _ = self._bundle()
        empty = pd.DataFrame(columns=["timestamp", "consumption_kwh"])
        with pytest.raises(InsufficientHistoryError):
            forecast(bundle, empty, horizon_hours=24)
