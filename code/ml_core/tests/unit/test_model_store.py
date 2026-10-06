import pytest
from tests.factories import hourly_frame


class TestModelStore:
    def test_missing_model_raises(self, tmp_path):
        from ml_core import ModelNotFoundError, describe_model, load_bundle

        path = str(tmp_path / "absent.joblib")
        with pytest.raises(ModelNotFoundError):
            load_bundle(path)
        assert describe_model(path) == {"available": False}

    def test_corrupt_model_raises_load_error(self, tmp_path):
        from ml_core import ModelLoadError, load_bundle

        path = tmp_path / "corrupt.joblib"
        path.write_bytes(b"not a model")
        with pytest.raises(ModelLoadError):
            load_bundle(str(path))

    def test_legacy_model_format_is_rejected(self, tmp_path):
        import joblib
        from ml_core import ModelLoadError, load_bundle
        from sklearn.ensemble import RandomForestRegressor

        path = str(tmp_path / "legacy.joblib")
        joblib.dump(RandomForestRegressor(n_estimators=2), path)
        with pytest.raises(ModelLoadError):
            load_bundle(path)

    def test_bundle_is_cached_until_file_changes(self, tmp_path):
        from ml_core import load_bundle, run_training_pipeline

        path = str(tmp_path / "model.joblib")
        run_training_pipeline(hourly_frame(), model_path=path)
        first = load_bundle(path)
        assert load_bundle(path) is first
        run_training_pipeline(hourly_frame(seed=7), model_path=path)
        assert load_bundle(path) is not first
