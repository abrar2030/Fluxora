# Basic Prediction Example

Learn how to make energy consumption predictions using Fluxora's API and Python library.

---

## Overview

This example demonstrates:

- Authenticating with the API
- Submitting energy data
- Retrieving predictions
- Interpreting results

---

## Prerequisites

- Fluxora API running at `http://localhost:8000`
- Python 3.9+ with `requests` library installed
- Valid user account (or create one via registration)

```bash
pip install requests pandas
```

---

## Example 1: API-Based Prediction

### Step 1: Register and Login

```python
import requests
import json

API_BASE = "http://localhost:8000"

# Register new user (if needed)
register_data = {
    "email": "demo@example.com",
    "password": "securepass123",
    "full_name": "Demo User"
}

response = requests.post(f"{API_BASE}/v1/auth/register", json=register_data)
print(f"Registration: {response.status_code}")

# Login to get access token
login_data = {
    "username": "demo@example.com",
    "password": "securepass123"
}

response = requests.post(f"{API_BASE}/v1/auth/login", json=login_data)
token_data = response.json()
TOKEN = token_data['access_token']

print(f"Access Token: {TOKEN[:20]}...")
```

### Step 2: Submit Historical Data

```python
# Headers for authenticated requests
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Submit several data points
from datetime import datetime, timedelta
import random

base_time = datetime.utcnow() - timedelta(days=7)

for i in range(168):  # 7 days * 24 hours
    timestamp = base_time + timedelta(hours=i)

    # Generate realistic energy data
    hour = timestamp.hour
    base_consumption = 45.0
    daily_pattern = 15.0 * (0.5 + 0.5 * abs((hour - 12) / 12))
    noise = random.gauss(0, 3)
    consumption = base_consumption + daily_pattern + noise

    data_point = {
        "timestamp": timestamp.isoformat(),
        "consumption_kwh": round(consumption, 2),
        "cost_usd": round(consumption * 0.10, 2),
        "temperature_c": round(20 + random.gauss(0, 3), 1),
        "humidity_percent": round(60 + random.gauss(0, 10), 1)
    }

    response = requests.post(
        f"{API_BASE}/v1/data/",
        headers=headers,
        json=data_point
    )

    if i % 24 == 0:
        print(f"Submitted day {i // 24 + 1}/7")

print("Historical data submitted successfully!")
```

### Step 3: Get Predictions

```python
# Request 3-day predictions
response = requests.get(
    f"{API_BASE}/v1/predictions/",
    headers=headers,
    params={"days": 3}
)

predictions = response.json()

print(f"\nReceived {len(predictions)} hourly predictions")
print("\nSample predictions (first 24 hours):")
print(f"{'Timestamp':<20} {'Predicted (kWh)':<15} {'Range':<20}")
print("-" * 60)

for pred in predictions[:24]:
    timestamp = pred['timestamp'][:16]  # Truncate for display
    predicted = pred['predicted_consumption']
    lower = pred['confidence_interval']['lower']
    upper = pred['confidence_interval']['upper']

    print(f"{timestamp:<20} {predicted:>6.2f} kWh      [{lower:.2f} - {upper:.2f}]")
```

### Step 4: Analyze Results

```python
# Calculate summary statistics
import pandas as pd

df_pred = pd.DataFrame(predictions)
df_pred['timestamp'] = pd.to_datetime(df_pred['timestamp'])

# Daily summary
daily_consumption = df_pred.groupby(
    df_pred['timestamp'].dt.date
)['predicted_consumption'].sum()

print("\n=== Daily Consumption Forecast ===")
for date, consumption in daily_consumption.items():
    print(f"{date}: {consumption:.2f} kWh (${consumption * 0.10:.2f})")

# Peak hours
df_pred['hour'] = df_pred['timestamp'].dt.hour
peak_hours = df_pred.groupby('hour')['predicted_consumption'].mean().sort_values(ascending=False)

print("\n=== Top 5 Peak Hours ===")
for hour, consumption in peak_hours.head(5).items():
    print(f"{hour:02d}:00 - {consumption:.2f} kWh")
```

**Expected Output:**

```
Registration: 201
Access Token: eyJhbGciOiJIUzI1NiIsI...
Submitted day 1/7
Submitted day 2/7
...
Submitted day 7/7
Historical data submitted successfully!

Received 72 hourly predictions

Sample predictions (first 24 hours):
Timestamp            Predicted (kWh) Range
------------------------------------------------------------
2025-12-31T00:00   52.34 kWh      [47.11 - 57.57]
2025-12-31T01:00   48.92 kWh      [44.03 - 53.81]
...

=== Daily Consumption Forecast ===
2025-12-31: 1245.67 kWh ($124.57)
2026-01-01: 1189.34 kWh ($118.93)
2026-01-02: 1267.89 kWh ($126.79)

=== Top 5 Peak Hours ===
14:00 - 62.45 kWh
15:00 - 61.23 kWh
13:00 - 59.87 kWh
16:00 - 58.54 kWh
12:00 - 56.78 kWh
```

---

## Example 2: Python Library-Based Prediction

### Direct Model Usage

```python
import os
import sys
sys.path.insert(0, os.path.join(os.getcwd(), 'code'))

import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from data.features.feature_engineering import preprocess_data_for_model

# Load the trained model
MODEL_PATH = 'code/fluxora_model.joblib'
model = joblib.load(MODEL_PATH)

print(f"Model loaded from {MODEL_PATH}")

# Create sample historical data
def create_sample_data(days=7):
    """Generate sample energy consumption data."""
    start_time = datetime.now() - timedelta(days=days)
    timestamps = [start_time + timedelta(hours=i) for i in range(days * 24)]

    consumption = []
    for ts in timestamps:
        hour = ts.hour
        day_of_week = ts.weekday()

        # Base load
        base = 50.0

        # Daily pattern (higher during day, lower at night)
        daily = 20.0 * np.sin((hour - 6) * np.pi / 12)

        # Weekly pattern (higher weekdays)
        weekly = 5.0 if day_of_week < 5 else -5.0

        # Random noise
        noise = np.random.normal(0, 3)

        consumption.append(max(0, base + daily + weekly + noise))

    df = pd.DataFrame({
        'timestamp': timestamps,
        'consumption_kwh': consumption,
        'user_id': 1
    })

    return df

# Generate historical data
historical_data = create_sample_data(days=7)
print(f"\nGenerated {len(historical_data)} historical records")

# Preprocess data for model
processed_data = preprocess_data_for_model(historical_data.copy())

# Prepare features
target_col = 'consumption_kwh'
feature_cols = [col for col in processed_data.columns
                if col not in [target_col, 'timestamp', 'user_id']]

X = processed_data[feature_cols]
print(f"Features: {len(feature_cols)}")

# Make predictions on historical data (for validation)
predictions_hist = model.predict(X)

# Calculate accuracy on historical data
actual = processed_data[target_col]
mse = np.mean((actual - predictions_hist) ** 2)
mae = np.mean(np.abs(actual - predictions_hist))
print(f"\nHistorical Validation:")
print(f"  MSE: {mse:.4f}")
print(f"  MAE: {mae:.4f}")

# Now predict future (24 hours)
future_start = historical_data['timestamp'].iloc[-1] + timedelta(hours=1)
future_timestamps = [future_start + timedelta(hours=i) for i in range(24)]

# Initialize future dataframe
future_data = pd.DataFrame({
    'timestamp': future_timestamps,
    'consumption_kwh': np.nan,
    'user_id': 1
})

# Combine historical and future
full_data = pd.concat([historical_data, future_data], ignore_index=True)

# Iteratively predict each future timestep
start_idx = len(historical_data)
for i in range(start_idx, len(full_data)):
    # Process data up to current point
    temp_df = preprocess_data_for_model(full_data.iloc[:i+1].copy())
    current_features = temp_df.iloc[-1][feature_cols]

    # Predict
    prediction = model.predict(current_features.to_frame().T)[0]
    full_data.loc[i, 'consumption_kwh'] = prediction

# Extract future predictions
future_predictions = full_data.iloc[start_idx:].copy()

print("\n=== 24-Hour Forecast ===")
print(f"{'Hour':<10} {'Timestamp':<20} {'Predicted (kWh)':<15}")
print("-" * 50)

for idx, row in future_predictions.iterrows():
    hour_offset = idx - start_idx
    timestamp_str = row['timestamp'].strftime('%Y-%m-%d %H:%M')
    predicted = row['consumption_kwh']
    print(f"+{hour_offset:02d}h      {timestamp_str}   {predicted:>6.2f} kWh")

# Daily summary
total_predicted = future_predictions['consumption_kwh'].sum()
avg_predicted = future_predictions['consumption_kwh'].mean()
peak_predicted = future_predictions['consumption_kwh'].max()

print(f"\n=== Summary ===")
print(f"Total (24h): {total_predicted:.2f} kWh")
print(f"Average: {avg_predicted:.2f} kWh/hour")
print(f"Peak: {peak_predicted:.2f} kWh")
print(f"Estimated Cost: ${total_predicted * 0.10:.2f}")
```

**Expected Output:**

```
Model loaded from code/fluxora_model.joblib
Generated 168 historical records
Features: 15

Historical Validation:
  MSE: 12.3456
  MAE: 2.8901

=== 24-Hour Forecast ===
Hour       Timestamp            Predicted (kWh)
--------------------------------------------------
+00h      2025-12-30 18:00    52.34 kWh
+01h      2025-12-30 19:00    48.92 kWh
+02h      2025-12-30 20:00    45.67 kWh
...
+23h      2025-12-31 17:00    61.23 kWh

=== Summary ===
Total (24h): 1234.56 kWh
Average: 51.44 kWh/hour
Peak: 65.78 kWh
Estimated Cost: $123.46
```

---

## Example 3: Batch Prediction Script

Save as `batch_predict.py`:

```python
#!/usr/bin/env python3
"""
Batch prediction script for multiple meters.
"""

import requests
import pandas as pd
from datetime import datetime

API_BASE = "http://localhost:8000"
TOKEN = "your_access_token_here"  # Get from login

def get_predictions(days=7):
    """Get predictions from API."""
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(
        f"{API_BASE}/v1/predictions/",
        headers=headers,
        params={"days": days}
    )
    return response.json()

def export_to_csv(predictions, filename="predictions.csv"):
    """Export predictions to CSV file."""
    df = pd.DataFrame(predictions)
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    df['hour'] = pd.to_datetime(df['timestamp']).dt.hour

    # Add calculated fields
    df['lower_bound'] = df['confidence_interval'].apply(lambda x: x['lower'])
    df['upper_bound'] = df['confidence_interval'].apply(lambda x: x['upper'])
    df['cost_estimate'] = df['predicted_consumption'] * 0.10

    # Select columns for export
    export_df = df[[
        'date', 'hour', 'predicted_consumption',
        'lower_bound', 'upper_bound', 'cost_estimate'
    ]]

    export_df.to_csv(filename, index=False)
    print(f"Predictions exported to {filename}")

def main():
    print("Fetching predictions...")
    predictions = get_predictions(days=7)

    print(f"Received {len(predictions)} predictions")

    # Export to CSV
    export_to_csv(predictions)

    # Print summary
    df = pd.DataFrame(predictions)
    total = df['predicted_consumption'].sum()
    avg = df['predicted_consumption'].mean()

    print(f"\n7-Day Summary:")
    print(f"  Total: {total:.2f} kWh")
    print(f"  Average: {avg:.2f} kWh/hour")
    print(f"  Estimated Cost: ${total * 0.10:.2f}")

if __name__ == "__main__":
    main()
```

**Usage:**

```bash
python batch_predict.py
```

---

## Next Steps

- **[Advanced Analytics Example](ADVANCED_ANALYTICS.md)** - Detailed analytics and reporting
- **[Custom Model Training](CUSTOM_TRAINING.md)** - Train your own models
- **[API Reference](../API.md)** - Complete API documentation
- **[Usage Guide](../USAGE.md)** - More usage patterns

---

## Troubleshooting

**Issue:** 401 Unauthorized error

**Solution:**

```python
# Token might be expired, login again
response = requests.post(f"{API_BASE}/v1/auth/login", json=login_data)
TOKEN = response.json()['access_token']
```

**Issue:** No predictions returned

**Solution:**

```python
# Ensure you have submitted historical data (at least 48 hours)
# Check if model is trained
response = requests.get(f"{API_BASE}/health")
print(response.json())
```

---

**Questions?** Check the [Troubleshooting Guide](../TROUBLESHOOTING.md) or open an issue.
