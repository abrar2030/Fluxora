import pandas as pd
import pytest
from tests.factories import hourly_frame


class TestForecasting:
    def _bundle(self):
        from src.training.trainer import train_model

        frame = hourly_frame(users=(1, 2))
        bundle, _ = train_model(frame)
        return bundle, frame[frame["user_id"] == 1]

    def test_forecast_length_and_ordering(self):
        from src import forecast

        bundle, history = self._bundle()
        result = forecast(bundle, history, horizon_hours=48)
        assert len(result) == 48
        assert result["timestamp"].is_monotonic_increasing
        assert (result["lower"] <= result["predicted_consumption"]).all()
        assert (result["predicted_consumption"] <= result["upper"]).all()
        assert (result["lower"] >= 0).all()

    def test_forecast_starts_after_the_current_hour(self):
        from datetime import datetime, timezone

        from src import forecast

        bundle, history = self._bundle()
        result = forecast(bundle, history, horizon_hours=3)
        current = pd.Timestamp(datetime.now(timezone.utc)).tz_localize(None).floor("h")
        assert result["timestamp"].iloc[0] == current + pd.Timedelta(hours=1)

    def test_forecast_tracks_the_daily_cycle(self):
        from src import forecast

        bundle, history = self._bundle()
        result = forecast(bundle, history, horizon_hours=72)
        assert result["predicted_consumption"].nunique() > 20
        assert result["predicted_consumption"].std() > 3

    def test_forecast_requires_enough_history(self):
        from src import InsufficientHistoryError, forecast

        bundle, history = self._bundle()
        with pytest.raises(InsufficientHistoryError):
            forecast(bundle, history.tail(30), horizon_hours=24)

    def test_forecast_rejects_stale_history(self):
        from src import InsufficientHistoryError, forecast

        bundle, history = self._bundle()
        stale = history.copy()
        stale["timestamp"] = stale["timestamp"] - pd.Timedelta(days=30)
        with pytest.raises(InsufficientHistoryError):
            forecast(bundle, stale, horizon_hours=24)

    def test_forecast_rejects_empty_history(self):
        from src import InsufficientHistoryError, forecast

        bundle, _ = self._bundle()
        empty = pd.DataFrame(columns=["timestamp", "consumption_kwh"])
        with pytest.raises(InsufficientHistoryError):
            forecast(bundle, empty, horizon_hours=24)

    def test_short_history_gaps_are_filled(self):
        from src import forecast

        bundle, history = self._bundle()
        gappy = history.drop(history.index[-60:-57])
        assert len(forecast(bundle, gappy, horizon_hours=6)) == 6

    def test_long_history_gaps_are_rejected(self):
        from src import InsufficientHistoryError, forecast

        bundle, history = self._bundle()
        gappy = history.drop(history.index[-60:-48])
        with pytest.raises(InsufficientHistoryError, match="gap"):
            forecast(bundle, gappy, horizon_hours=6)

    def test_interval_width_follows_the_horizon_buckets(self):
        import dataclasses

        from src import forecast

        bundle, history = self._bundle()
        wide = dataclasses.replace(
            bundle,
            interval_edges=[1, 3, 6],
            interval_lower=[-1.0, -2.0, -3.0],
            interval_upper=[1.0, 2.0, 3.0],
            residual_lower=-1.0,
            residual_upper=1.0,
        )
        wide.warm()
        result = forecast(wide, history, horizon_hours=8)
        width = (result["upper"] - result["lower"]).to_numpy()
        values = result["predicted_consumption"].to_numpy()
        assert (result["upper"] - values).round(6).tolist()[0] == 1.0
        assert width[1] >= width[0] and width[7] >= width[2] >= width[1]
        assert (result["upper"] - values).iloc[7] == 3.0
