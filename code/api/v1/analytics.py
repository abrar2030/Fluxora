from typing import Annotated, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from collections import defaultdict

from ...backend.dependencies import get_db
from ...backend.security import get_current_active_user
from ...crud.data import get_data_by_time_range
from ...schemas.user import User
from ...models.data import EnergyData

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    dependencies=[Depends(get_current_active_user)]
)

def calculate_analytics(records: List[EnergyData], period: str) -> List[Dict[str, Any]]:
    """
    Calculates aggregated analytics data based on the time period.
    """
    if not records:
        return []

    # Convert to pandas DataFrame for easy manipulation
    import pandas as pd
    df = pd.DataFrame([r.__dict__ for r in records])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')

    # Determine aggregation frequency
    if period == "week":
        freq = 'D' # Daily aggregation for a week
    elif period == "month":
        freq = 'D' # Daily aggregation for a month
    elif period == "year":
        freq = 'W' # Weekly aggregation for a year
    else:
        raise ValueError("Invalid period")

    # Aggregate data
    aggregated_data = df.resample(freq).agg({
        'consumption_kwh': 'sum',
        'cost_usd': 'sum',
        'temperature_c': 'mean',
        'humidity_percent': 'mean'
    }).dropna().reset_index()

    # Calculate a simple 'efficiency' metric (e.g., inverse of consumption per degree)
    aggregated_data['efficiency'] = 100 - (aggregated_data['consumption_kwh'] / aggregated_data['temperature_c'].replace(0, 1))

    # Format output
    results = []
    for _, row in aggregated_data.iterrows():
        label = row['timestamp'].strftime('%Y-%m-%d')
        if period == 'year':
            label = f"Week {row['timestamp'].isocalendar()[1]}"
            
        results.append({
            "label": label,
            "consumption": round(row['consumption_kwh'], 2),
            "cost": round(row['cost_usd'] if row['cost_usd'] else 0, 2),
            "temperature": round(row['temperature_c'], 2),
            "efficiency": round(row['efficiency'], 2),
        })
        
    return results

@router.get("/", response_model=List[Dict[str, Any]])
def get_analytics(
    period: str = "month",
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """
    Provides aggregated energy consumption analytics for a given period.
    """
    end_time = datetime.utcnow()
    if period == "week":
        start_time = end_time - timedelta(days=7)
    elif period == "month":
        start_time = end_time - timedelta(days=30)
    elif period == "year":
        start_time = end_time - timedelta(days=365)
    else:
        raise HTTPException(status_code=400, detail="Invalid period. Must be 'week', 'month', or 'year'.")

    records = get_data_by_time_range(db, user_id=current_user.id, start_time=start_time, end_time=end_time)
    
    if not records:
        # Return a mock response if no real data is available
        return [
            {"label": "Day 1", "consumption": 50.5, "cost": 5.05, "temperature": 20.1, "efficiency": 75.0},
            {"label": "Day 2", "consumption": 60.2, "cost": 6.02, "temperature": 22.5, "efficiency": 70.5},
            {"label": "Day 3", "consumption": 45.1, "cost": 4.51, "temperature": 18.9, "efficiency": 80.1},
        ]

    try:
        analytics_data = calculate_analytics(records, period)
    except Exception as e:
        print(f"Error calculating analytics: {e}")
        raise HTTPException(status_code=500, detail="Error calculating analytics data.")

    return analytics_data
