import logging
import os
import tempfile
import threading
from typing import Any

import joblib

from ..config import MODEL_SCHEMA_VERSION, get_model_path
from ..exceptions import ModelLoadError, ModelNotFoundError
from .bundle import ModelBundle

logger = logging.getLogger(__name__)

_cache_lock = threading.Lock()
_cache: dict[str, tuple[tuple[int, int], ModelBundle]] = {}


def save_bundle(bundle: ModelBundle, path: str = "") -> str:
    target = os.path.abspath(path) if path else get_model_path()
    directory = os.path.dirname(target)
    os.makedirs(directory, exist_ok=True)

    payload = {
        "schema_version": MODEL_SCHEMA_VERSION,
        "model": bundle.model,
        "feature_columns": bundle.feature_columns,
        "lags": bundle.lags,
        "windows": bundle.windows,
        "target_col": bundle.target_col,
        "history_hours": bundle.history_hours,
        "metrics": bundle.metrics,
        "residual_lower": bundle.residual_lower,
        "residual_upper": bundle.residual_upper,
        "interval_level": bundle.interval_level,
        "trained_at": bundle.trained_at,
    }

    handle, temp_path = tempfile.mkstemp(dir=directory, suffix=".tmp")
    os.close(handle)
    try:
        joblib.dump(payload, temp_path)
        os.replace(temp_path, target)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    with _cache_lock:
        _cache.pop(target, None)
    logger.info("Model saved to %s", target)
    return target


def _signature(path: str) -> tuple[int, int]:
    stat = os.stat(path)
    return stat.st_mtime_ns, stat.st_size


def _bundle_from_payload(payload: Any) -> ModelBundle:
    if not isinstance(payload, dict) or payload.get("schema_version") != (
        MODEL_SCHEMA_VERSION
    ):
        raise ModelLoadError(
            "The stored model uses an unsupported format. Retrain the model."
        )
    try:
        return ModelBundle(
            model=payload["model"],
            feature_columns=list(payload["feature_columns"]),
            lags=list(payload["lags"]),
            windows=list(payload["windows"]),
            target_col=payload["target_col"],
            history_hours=int(payload["history_hours"]),
            metrics=dict(payload["metrics"]),
            residual_lower=float(payload["residual_lower"]),
            residual_upper=float(payload["residual_upper"]),
            interval_level=float(payload["interval_level"]),
            trained_at=str(payload["trained_at"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ModelLoadError(f"The stored model is incomplete: {exc}") from exc


def load_bundle(path: str = "") -> ModelBundle:
    target = os.path.abspath(path) if path else get_model_path()
    if not os.path.exists(target):
        raise ModelNotFoundError("No trained model is available.")

    try:
        signature = _signature(target)
    except OSError as exc:
        raise ModelLoadError(f"Could not access the model file: {exc}") from exc

    with _cache_lock:
        cached = _cache.get(target)
        if cached is not None and cached[0] == signature:
            return cached[1]

    try:
        payload = joblib.load(target)
    except Exception as exc:
        raise ModelLoadError(f"Could not read the model file: {exc}") from exc

    bundle = _bundle_from_payload(payload)
    bundle.warm()

    with _cache_lock:
        _cache[target] = (signature, bundle)
    return bundle


def clear_cache() -> None:
    with _cache_lock:
        _cache.clear()


def describe_model(path: str = "") -> dict[str, Any]:
    try:
        return load_bundle(path).describe()
    except ModelNotFoundError:
        return {"available": False}
