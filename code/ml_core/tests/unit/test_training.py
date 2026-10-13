import pandas as pd
import pytest
from tests.factories import hourly_frame


class TestModelTraining:
    def test_train_model_returns_bundle_and_metrics(self):
        from src.training.trainer import train_model

        bundle, metrics = train_model(hourly_frame())
        assert bundle.model is not None
        assert len(bundle.feature_columns) == metrics["feature_count"]
        for key in (
            "mean_squared_error",
            "root_mean_squared_error",
            "mean_absolute_error",
            "r2_score",
            "feature_count",
            "training_samples",
            "test_samples",
            "user_count",
        ):
            assert key in metrics
        assert metrics["mean_squared_error"] >= 0
        assert metrics["r2_score"] > 0.5
        assert bundle.residual_lower <= bundle.residual_upper

    def test_train_model_scopes_features_per_user(self):
        from src.training.trainer import train_model

        _, metrics = train_model(hourly_frame(users=(1, 2)))
        assert metrics["user_count"] == 2

    def test_train_model_rejects_empty_frame(self):
        from src.exceptions import InsufficientDataError
        from src.training.trainer import train_model

        with pytest.raises(InsufficientDataError):
            train_model(
                pd.DataFrame(columns=["timestamp", "consumption_kwh", "user_id"])
            )

    def test_train_model_rejects_too_little_history(self):
        from src.exceptions import InsufficientDataError
        from src.training.trainer import train_model

        with pytest.raises(InsufficientDataError):
            train_model(hourly_frame(days=8))

    def test_train_model_rejects_negative_consumption(self):
        from src.exceptions import DataValidationError
        from src.training.trainer import train_model

        df = hourly_frame()
        df.loc[0, "consumption_kwh"] = -1.0
        with pytest.raises(DataValidationError):
            train_model(df)

    def test_run_training_pipeline_saves_loadable_model(self, tmp_path):
        from src import load_bundle, run_training_pipeline

        model_path = str(tmp_path / "model.joblib")
        result = run_training_pipeline(hourly_frame(), model_path=model_path)
        assert "mean_squared_error" in result["metrics"]
        assert result["model"]["available"] is True
        bundle = load_bundle(model_path)
        assert bundle.feature_columns


class TestGapHandling:
    def test_short_gaps_do_not_break_features_or_become_targets(self):
        from src.training.trainer import prepare_training_frame

        frame = hourly_frame(users=(1,))
        hole = frame["timestamp"].iloc[300:303]
        gappy = frame.drop(frame.index[300:303])
        result = prepare_training_frame(gappy)
        assert not result["timestamp"].isin(hole).any()
        after = frame["timestamp"].iloc[303]
        assert (result["timestamp"] == after).any()

    def test_long_gaps_remove_the_rows_that_depend_on_them(self):
        from src.config import MAX_FILL_GAP_HOURS
        from src.training.trainer import prepare_training_frame

        frame = hourly_frame(users=(1,))
        gappy = frame.drop(frame.index[300 : 300 + MAX_FILL_GAP_HOURS + 4])
        result = prepare_training_frame(gappy)
        resume = frame["timestamp"].iloc[300 + MAX_FILL_GAP_HOURS + 4]
        assert not (result["timestamp"] == resume).any()

    def test_null_rows_are_dropped_not_rejected(self):
        from src.training.trainer import train_model

        frame = hourly_frame()
        frame.loc[frame.index[::97], "consumption_kwh"] = None
        _, metrics = train_model(frame)
        assert metrics["training_samples"] > 0


class TestRefit:
    def _count_fits(self, monkeypatch, **kwargs):
        from src.training import trainer

        calls = []
        real = trainer.new_model

        def counting():
            calls.append(1)
            return real()

        monkeypatch.setattr(trainer, "new_model", counting)
        _, metrics = trainer.train_model(hourly_frame(), **kwargs)
        return len(calls), metrics

    def test_default_refits_on_full_data(self, monkeypatch):
        monkeypatch.delenv("MODEL_REFIT_FULL_DATA", raising=False)
        fits, metrics = self._count_fits(monkeypatch)
        assert fits == 2 and metrics["refit_on_full_data"] is True

    def test_refit_can_be_disabled_by_argument(self, monkeypatch):
        fits, metrics = self._count_fits(monkeypatch, refit_on_full_data=False)
        assert fits == 1 and metrics["refit_on_full_data"] is False

    def test_refit_can_be_disabled_by_environment(self, monkeypatch):
        monkeypatch.setenv("MODEL_REFIT_FULL_DATA", "false")
        fits, _ = self._count_fits(monkeypatch)
        assert fits == 1


class TestHorizonIntervals:
    def test_bounds_widen_monotonically_with_horizon(self):
        from src.training.trainer import train_model

        bundle, _ = train_model(hourly_frame(users=(1, 2)))
        n = len(bundle.interval_edges)
        assert n == len(bundle.interval_lower) == len(bundle.interval_upper) > 1
        assert bundle.interval_edges == sorted(bundle.interval_edges)
        lower, upper = bundle.interval_lower, bundle.interval_upper
        assert all(a >= b for a, b in zip(lower, lower[1:], strict=False))
        assert all(a <= b for a, b in zip(upper, upper[1:], strict=False))
        assert bundle.residual_lower == lower[0]
        assert bundle.residual_upper == upper[0]

    def test_backtest_collects_residuals_across_horizons(self):
        from src.training.backtest import collect_horizon_residuals
        from src.training.trainer import _hourly_frame, train_model

        frame = hourly_frame(users=(1, 2))
        bundle, _ = train_model(frame)
        hourly = _hourly_frame(frame)
        start = hourly["timestamp"].iloc[int(len(hourly) * 0.8)]
        horizons, residuals = collect_horizon_residuals(bundle, hourly, start, 48)
        assert len(horizons) == len(residuals) > 0
        assert horizons.min() >= 1 and horizons.max() <= 48
        assert len(set(horizons.tolist())) > 10
