from typing import Annotated, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import joblib
import os
import pandas as pd
import numpy as np

from ...backend.dependencies import get_db
from ...backend.security import get_current_active_user
from ...schemas.user import User
from ...data.features.feature_engineering import preprocess_data_for_model

router = APIRouter(
    prefix="/predictions",
    tags=["predictions"],
    dependencies=[Depends(get_current_active_user)]
)

# Define the path to the trained model
MODEL_PATH = os.path.join(os.getcwd(), "fluxora_model.joblib")

def load_model():
    """Loads the trained model from disk."""
    if not os.path.exists(MODEL_PATH):
        # Fallback to mock data if model is not trained
        return None
    try:
        return joblib.load(MODEL_PATH)
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

def generate_mock_predictions(days: int) -> List[Dict[str, Any]]:
    """Generates mock prediction data."""
    data = []
    now = datetime.utcnow()

    for i in range(days * 24):
        timestamp = now + timedelta(hours=i)
        hour = timestamp.hour
        base_load = 50
        daily_cycle = np.sin((hour / 24) * 2 * np.pi) * 20
        noise = np.random.normal(0, 5)
        predicted = base_load + daily_cycle + noise
        
        data.append({
            "timestamp": timestamp.isoformat(),
            "predicted_consumption": round(predicted, 2),
            "confidence_interval": {
                "lower": round(predicted * 0.85, 2),
                "upper": round(predicted * 1.15, 2),
            },
        })
    return data

@router.get("/", response_model=List[Dict[str, Any]])
def get_predictions(
    days: int = 7,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """
    Generates energy consumption predictions for the next 'days' ahead.
    """
    model = load_model()
    
    if model is None:
        # If model is not available, return mock data
        return generate_mock_predictions(days)

    # --- Real Prediction Logic (Simplified) ---
    
    # 1. Get the last 24 hours of real data for feature creation
    from ...crud.data import get_data_records
    # We need enough data to create lag features (e.g., 24 hours)
    historical_records = get_data_records(db, user_id=current_user.id, limit=48) 
    
    if not historical_records:
        return generate_mock_predictions(days)

    # Convert to DataFrame
    historical_df = pd.DataFrame([r.__dict__ for r in historical_records])
    historical_df['timestamp'] = pd.to_datetime(historical_df['timestamp'])
    historical_df = historical_df.sort_values('timestamp')

    # 2. Create a DataFrame for the prediction period (the future)
    future_timestamps = [historical_df['timestamp'].iloc[-1] + timedelta(hours=i) for i in range(1, days * 24 + 1)]
    future_df = pd.DataFrame({
        'timestamp': future_timestamps,
        'consumption_kwh': np.nan, # Target is unknown
        'user_id': current_user.id
    })

    # 3. Combine historical and future data for feature engineering
    full_df = pd.concat([historical_df, future_df], ignore_index=True)
    
    # 4. Iteratively predict and update the dataframe (Autoregressive approach)
    # This is a simplified, slow loop. In production, this would be optimized.
    
    # Start index for prediction is the first NaN value
    start_idx = len(historical_df)
    
    for i in range(start_idx, len(full_df)):
        # Create features for the current time step
        temp_df = preprocess_data_for_model(full_df.iloc[:i].copy())
        
        # Get the feature vector for the current time step
        current_features = temp_df.iloc[-1]
        
        # Define features used in training (must match train.py)
        target_col = 'consumption_kwh'
        features = [col for col in temp_df.columns if col not in [target_col, 'timestamp', 'user_id']]
        
        X_pred = current_features[features].to_frame().T
        
        # Predict
        prediction = model.predict(X_pred)[0]
        
        # Update the full_df with the prediction for the next iteration
        full_df.loc[i, 'consumption_kwh'] = prediction

    # 5. Extract the predictions
    predictions_df = full_df.iloc[start_idx:].copy()
    
    # 6. Format the output
    results = []
    for _, row in predictions_df.iterrows():
        # Simple confidence interval for demonstration
        predicted = row['consumption_kwh']
        results.append({
            "timestamp": row['timestamp'].isoformat(),
            "predicted_consumption": round(predicted, 2),
            "confidence_interval": {
                "lower": round(predicted * 0.9, 2),
                "upper": round(predicted * 1.1, 2),
            },
        })

    return results
