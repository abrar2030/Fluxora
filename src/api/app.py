from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from src.utils.monitoring import monitor_requests

app = FastAPI()
Instrumentator().instrument(app).expose(app)

@app.post("/predict", response_model=PredictionResponse)
@monitor_requests
async def predict(payload: PredictionRequest):
    """
    Batch prediction endpoint with automated monitoring
    """
    preprocessed = feature_pipeline.transform(payload.data)
    predictions = model.predict(preprocessed)
    
    return {
        "predictions": predictions.tolist(),
        "model_version": config.current_model_version,
        "metadata": payload.metadata
    }