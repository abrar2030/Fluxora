import pandas as pd
import pytest
from tests.factories import hourly_frame


class TestModelTraining:
    def test_train_model_returns_bundle_and_metrics(self):
        from ml_core.training.trainer import train_model

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
        from ml_core.training.trainer import train_model

        _, metrics = train_model(hourly_frame(users=(1, 2)))
        assert metrics["user_count"] == 2

    def test_train_model_rejects_empty_frame(self):
        from ml_core.exceptions import InsufficientDataError
        from ml_core.training.trainer import train_model

        with pytest.raises(InsufficientDataError):
            train_model(
                pd.DataFrame(columns=["timestamp", "consumption_kwh", "user_id"])
            )

    def test_train_model_rejects_too_little_history(self):
        from ml_core.exceptions import InsufficientDataError
        from ml_core.training.trainer import train_model

        with pytest.raises(InsufficientDataError):
            train_model(hourly_frame(days=8))

    def test_train_model_rejects_negative_consumption(self):
        from ml_core.exceptions import DataValidationError
        from ml_core.training.trainer import train_model

        df = hourly_frame()
        df.loc[0, "consumption_kwh"] = -1.0
        with pytest.raises(DataValidationError):
            train_model(df)

    def test_run_training_pipeline_saves_loadable_model(self, tmp_path):
        from ml_core import load_bundle, run_training_pipeline

        model_path = str(tmp_path / "model.joblib")
        result = run_training_pipeline(hourly_frame(), model_path=model_path)
        assert "mean_squared_error" in result["metrics"]
        assert result["model"]["available"] is True
        bundle = load_bundle(model_path)
        assert bundle.feature_columns
