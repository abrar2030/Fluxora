from pydantic import BaseModel

class PredictionRequest(BaseModel):
    timestamps: list[str]
    meter_ids: list[str]
    context_features: dict

class PredictionResponse(BaseModel):
    predictions: list[float]
    confidence_intervals: list[tuple[float, float]]
    model_version: str
