from typing import Any

import pandas as pd

from ..config import get_model_path
from ..models.store import save_bundle
from .trainer import train_model


def run_training_pipeline(df: pd.DataFrame, model_path: str = "") -> dict[str, Any]:
    bundle, metrics = train_model(df)
    save_bundle(bundle, path=model_path or get_model_path())
    return {"metrics": metrics, "model": bundle.describe()}
