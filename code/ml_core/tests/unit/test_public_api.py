import importlib
import pathlib

import src


def test_every_exported_name_resolves():
    for name in src.__all__:
        assert hasattr(src, name)


def test_version_is_defined():
    assert src.__version__ == "1.0.0"


def test_package_is_marked_typed():
    assert (pathlib.Path(src.__file__).parent / "py.typed").is_file()


def test_subpackages_import_independently():
    for name in ("data", "features", "models", "training", "inference"):
        assert importlib.import_module(f"src.{name}")


def test_exceptions_share_a_base_class():
    for name in (
        "ConfigurationError",
        "DataValidationError",
        "InsufficientDataError",
        "InsufficientHistoryError",
        "ModelNotFoundError",
        "ModelLoadError",
    ):
        assert issubclass(getattr(src, name), src.MLCoreError)
