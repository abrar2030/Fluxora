import threading
from datetime import datetime, timedelta, timezone
from typing import Any

import pandas as pd
from app.crud.data import get_data_by_time_range
from app.models.data import EnergyData
from ml_core import describe_model, forecast, load_bundle, run_training_pipeline
from ml_core.config import MAX_HISTORY_GAP_HOURS
from sqlalchemy.orm import Session

_training_lock = threading.Lock()


class TrainingInProgressError(Exception):
    pass


def _utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def load_training_frame(db: Session) -> pd.DataFrame:
    rows = (
        db.query(EnergyData.timestamp, EnergyData.consumption_kwh, EnergyData.user_id)
        .order_by(EnergyData.user_id, EnergyData.timestamp)
        .all()
    )
    return pd.DataFrame(
        [(r.timestamp, float(r.consumption_kwh), r.user_id) for r in rows],
        columns=["timestamp", "consumption_kwh", "user_id"],
    )


def load_user_history(db: Session, user_id: int, history_hours: int) -> pd.DataFrame:
    end = _utc_now_naive()
    start = end - timedelta(hours=history_hours + MAX_HISTORY_GAP_HOURS + 24)
    records = get_data_by_time_range(
        db, user_id=user_id, start_time=start, end_time=end
    )
    return pd.DataFrame(
        [(r.timestamp, float(r.consumption_kwh)) for r in records],
        columns=["timestamp", "consumption_kwh"],
    )


def train_from_database(db: Session) -> dict[str, Any]:
    if not _training_lock.acquire(blocking=False):
        raise TrainingInProgressError("Model training is already in progress.")
    try:
        frame = load_training_frame(db)
        return run_training_pipeline(frame)
    finally:
        _training_lock.release()


def predict_for_user(db: Session, user_id: int, days: int) -> list[dict[str, Any]]:
    bundle = load_bundle()
    history = load_user_history(db, user_id, bundle.history_hours)
    result = forecast(bundle, history, horizon_hours=days * 24)
    return [
        {
            "timestamp": row.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "predicted_consumption": round(float(row.predicted_consumption), 2),
            "confidence_interval": {
                "lower": round(float(row.lower), 2),
                "upper": round(float(row.upper), 2),
            },
        }
        for row in result.itertuples(index=False)
    ]


def model_status() -> dict[str, Any]:
    return describe_model()
