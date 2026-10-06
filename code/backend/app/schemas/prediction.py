from typing import Any

from pydantic import BaseModel


class ConfidenceInterval(BaseModel):
    lower: float
    upper: float


class PredictionPoint(BaseModel):
    timestamp: str
    predicted_consumption: float
    confidence_interval: ConfidenceInterval


class ModelInfo(BaseModel):
    available: bool
    trained_at: str | None = None
    feature_count: int | None = None
    history_hours: int | None = None
    interval_level: float | None = None
    metrics: dict[str, Any] | None = None


class TrainResponse(BaseModel):
    status: str
    metrics: dict[str, Any]
    model: ModelInfo
