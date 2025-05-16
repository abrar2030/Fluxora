from fastapi import FastAPI, Depends
from src.api.schemas import PredictionRequest, PredictionResponse
from src.models.predict import get_model, predict_with_model
from src.features.build_features import FeaturePipeline
from src.utils.config import get_config
import numpy as np

app = FastAPI(title="Fluxora API", description="Energy prediction API")

# Load configuration
config = get_config()

# Initialize feature pipeline and model
feature_pipeline = FeaturePipeline()
model = get_model()

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "version": config.get("version", "0.1.0")}

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
    std_dev = np.std(predictions, axis=0) if len(predictions.shape) > 1 else np.std(predictions)
    confidence_intervals = [(float(pred - 1.96 * std_dev), float(pred + 1.96 * std_dev)) for pred in predictions]

    return {
        "predictions": predictions.tolist(),
        "confidence_intervals": confidence_intervals,
        "model_version": config.get("model_version", "0.1.0")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
