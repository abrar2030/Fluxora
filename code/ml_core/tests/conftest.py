import pytest
import src


@pytest.fixture(autouse=True)
def isolated_model_cache(tmp_path, monkeypatch):
    monkeypatch.setenv("MODEL_PATH", str(tmp_path / "model.joblib"))
    src.clear_cache()
    yield
    src.clear_cache()
