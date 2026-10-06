import ml_core
import pytest


@pytest.fixture(autouse=True)
def isolated_model_cache(tmp_path, monkeypatch):
    monkeypatch.setenv("MODEL_PATH", str(tmp_path / "model.joblib"))
    ml_core.clear_cache()
    yield
    ml_core.clear_cache()
