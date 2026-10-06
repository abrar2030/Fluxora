import importlib
import pathlib

import ml_core


def test_every_exported_name_resolves():
    for name in ml_core.__all__:
        assert hasattr(ml_core, name)


def test_version_is_defined():
    assert ml_core.__version__ == "1.0.0"


def test_package_is_marked_typed():
    assert (pathlib.Path(ml_core.__file__).parent / "py.typed").is_file()


def test_subpackages_import_independently():
    for name in ("data", "features", "models", "training", "inference"):
        assert importlib.import_module(f"ml_core.{name}")


def test_exceptions_share_a_base_class():
    for name in (
        "DataValidationError",
        "InsufficientDataError",
        "InsufficientHistoryError",
        "ModelNotFoundError",
        "ModelLoadError",
    ):
        assert issubclass(getattr(ml_core, name), ml_core.MLCoreError)
