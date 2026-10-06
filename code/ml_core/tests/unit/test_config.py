import os

from ml_core import config


def test_model_path_defaults_to_absolute(monkeypatch):
    monkeypatch.delenv("MODEL_PATH", raising=False)
    path = config.get_model_path()
    assert os.path.isabs(path)
    assert path.endswith("fluxora_model.joblib")


def test_model_path_reads_environment(monkeypatch, tmp_path):
    target = str(tmp_path / "custom.joblib")
    monkeypatch.setenv("MODEL_PATH", target)
    assert config.get_model_path() == target


def test_estimators_never_below_one(monkeypatch):
    monkeypatch.setenv("MODEL_N_ESTIMATORS", "0")
    assert config.get_n_estimators() == 1


def test_max_depth_is_optional(monkeypatch):
    monkeypatch.delenv("MODEL_MAX_DEPTH", raising=False)
    assert config.get_max_depth() is None
    monkeypatch.setenv("MODEL_MAX_DEPTH", "7")
    assert config.get_max_depth() == 7


def test_required_history_uses_largest_lag_or_window():
    assert config.required_history_hours([1, 2, 24], [3, 168]) == 168
