from code.core.config import get_config
from code.features.build_features import FeaturePipeline
from code.models.predict import get_model, predict_with_model

import numpy as np
from fastapi import Depends, FastAPI

from .schemas import PredictionRequest, PredictionResponse

app = FastAPI(title="Fluxora API", description="Energy prediction API")

# Load configuration
config = get_config()

# Initialize feature pipeline and model
feature_pipeline = FeaturePipeline()
model = get_model()


# Register health check router
from .health_check import router as health_router

app.include_router(health_router)


@app.post("/predict", response_model=PredictionResponse)
async def predict(payload: PredictionRequest):
    """
    Batch prediction endpoint
    """
    # Transform input data using feature pipeline
    preprocessed = feature_pipeline.transform(payload)

    # Get predictions from model
    predictions = predict_with_model(model, preprocessed)

    # Calculate confidence intervals (95%)
    std_dev = (
        np.std(predictions, axis=0)
        if len(predictions.shape) > 1
        else np.std(predictions)
    )
    confidence_intervals = [
        (float(pred - 1.96 * std_dev), float(pred + 1.96 * std_dev))
        for pred in predictions
    ]

    return {
        "predictions": predictions.tolist(),
        "confidence_intervals": confidence_intervals,
        "model_version": config.get("model_version", "0.1.0"),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
