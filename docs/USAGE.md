# Usage Guide

This guide covers typical usage patterns for Fluxora, including CLI usage, library usage, and common workflows.

---

## 📑 Table of Contents

- [Quick Start](#quick-start)
- [Basic Workflows](#basic-workflows)
- [CLI Usage](#cli-usage)
- [Python Library Usage](#python-library-usage)
- [API Usage](#api-usage)
- [Common Use Cases](#common-use-cases)
- [Best Practices](#best-practices)

---

## Quick Start

Get Fluxora running in 3 steps:

```bash
# 1. Install and activate
git clone https://github.com/quantsingularity/Fluxora.git && cd Fluxora
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Start the API server
cd code && python main.py

# 3. Access the API
curl http://localhost:8000/health
```

---

## Basic Workflows

### Workflow 1: First-Time Setup

Complete setup for a new installation:

```bash
# Step 1: Clone and install
git clone https://github.com/quantsingularity/Fluxora.git
cd Fluxora
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Step 2: Configure environment
cp code/.env.example code/.env
# Edit code/.env with your settings

# Step 3: Initialize database
cd code
python -c "from backend.database import init_db; init_db()"

# Step 4: Train initial model
python models/train.py

# Step 5: Start API server
python main.py
```

**Expected Output:**

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Workflow 2: Training a Model

Train a machine learning model on your energy data:

```bash
# Using Python script
cd code
python models/train.py

# Or using Make command
cd .. && make train
```

**Example Output:**

```
[INFO] Starting training pipeline...
[INFO] Loading data from database...
[INFO] Model Training Complete. MSE: 12.3456, R2: 0.8901
[INFO] Model saved to fluxora_model.joblib
```

### Workflow 3: Making Predictions

Get energy consumption predictions via API:

```bash
# Register user and get token
curl -X POST http://localhost:8000/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123",
    "full_name": "John Doe"
  }'

# Login to get access token
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "securepass123"
  }'

# Get predictions (use token from login response)
curl -X GET "http://localhost:8000/v1/predictions/?days=7" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response Example:**

```json
[
  {
    "timestamp": "2025-12-30T18:00:00",
    "predicted_consumption": 52.34,
    "confidence_interval": {
      "lower": 47.11,
      "upper": 57.57
    }
  }
]
```

### Workflow 4: Viewing Analytics

Retrieve analytics data for a specific period:

```bash
# Get weekly analytics
curl -X GET "http://localhost:8000/v1/analytics/?period=week" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Get monthly analytics
curl -X GET "http://localhost:8000/v1/analytics/?period=month" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Get yearly analytics
curl -X GET "http://localhost:8000/v1/analytics/?period=year" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## CLI Usage

Fluxora provides several command-line interfaces through scripts and Make targets.

### Using Make Commands

```bash
# Install all dependencies
make install

# Prepare data (runs ETL pipeline)
make data

# Train models
make train

# Hyperparameter tuning
make tune

# Deploy with Docker
make deploy

# Start monitoring stack
make monitor

# Run tests
make test

# Clean up artifacts
make clean
```

### Direct Script Execution

#### Training Script

```bash
cd code
python models/train.py

# With custom configuration
python models/train.py --experiment-name=prod_v2
```

#### Hyperparameter Tuning

```bash
cd code
python models/tune_hyperparams.py --storage=mlruns
```

#### Real-time Data Fetching

```bash
cd scripts
python fetch_realtime_data.py
```

#### API Server

```bash
cd code

# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## Python Library Usage

Use Fluxora components as Python libraries in your own code.

### Example 1: Load and Use Trained Model

```python
import joblib
import pandas as pd
from data.features.feature_engineering import preprocess_data_for_model

# Load the trained model
model = joblib.load('fluxora_model.joblib')

# Prepare your data
raw_data = pd.DataFrame({
    'timestamp': ['2025-12-30T10:00:00'],
    'consumption_kwh': [45.2],
    'user_id': [1]
})

# Preprocess data
processed_data = preprocess_data_for_model(raw_data)

# Make prediction
features = [col for col in processed_data.columns
            if col not in ['consumption_kwh', 'timestamp', 'user_id']]
X = processed_data[features]
prediction = model.predict(X)

print(f"Predicted consumption: {prediction[0]:.2f} kWh")
```

### Example 2: Train Custom Model

```python
from models.train import load_data_from_db, train_model, save_model

# Load data
data_df = load_data_from_db()

# Train model
model, metrics = train_model(data_df)

# Save model
save_model(model, path='my_custom_model.joblib')

# Print metrics
print(f"MSE: {metrics['mean_squared_error']:.4f}")
print(f"R2 Score: {metrics['r2_score']:.4f}")
```

### Example 3: Use Feature Store

```python
from features.feature_store import get_online_features

# Define entity rows
entity_rows = [
    {'meter_id': 'MT_001', 'timestamp': '2025-12-30T10:00:00'},
    {'meter_id': 'MT_002', 'timestamp': '2025-12-30T11:00:00'}
]

# Define feature references
feature_refs = [
    'energy_stats:lag_24h',
    'energy_stats:rolling_7d_mean',
    'weather:temperature',
    'weather:humidity'
]

# Get features
features_df = get_online_features(
    entity_rows=entity_rows,
    feature_refs=feature_refs
)

print(features_df.head())
```

### Example 4: Use Circuit Breaker

```python
from core.circuit_breaker import CircuitBreaker

# Define fallback function
def fallback_prediction(*args, **kwargs):
    return {"prediction": 50.0, "source": "fallback"}

# Create circuit breaker
@CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=30,
    fallback_function=fallback_prediction
)
def make_prediction(data):
    # Your prediction logic here
    result = model.predict(data)
    return {"prediction": result[0], "source": "model"}

# Use the protected function
try:
    result = make_prediction(input_data)
    print(result)
except Exception as e:
    print(f"Prediction failed: {e}")
```

### Example 5: Use Retry Logic

```python
from core.retry import retry_with_backoff

@retry_with_backoff(max_retries=3, backoff_factor=2.0)
def fetch_external_data(url):
    import requests
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.json()

# Use the retry-protected function
data = fetch_external_data('https://api.example.com/energy-data')
```

---

## API Usage

### Authentication Flow

```bash
# 1. Register new user
curl -X POST http://localhost:8000/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123",
    "full_name": "John Doe"
  }'

# 2. Login to get access token
TOKEN=$(curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "securepass123"
  }' | jq -r '.access_token')

# 3. Use token for authenticated requests
curl -X GET http://localhost:8000/v1/predictions/ \
  -H "Authorization: Bearer $TOKEN"
```

### Data Management

```bash
# Upload energy data
curl -X POST http://localhost:8000/v1/data/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2025-12-30T10:00:00",
    "consumption_kwh": 45.2,
    "cost_usd": 4.52,
    "temperature_c": 22.5,
    "humidity_percent": 65.0
  }'

# Get data by date range
curl -X GET "http://localhost:8000/v1/data/?start_date=2025-12-01&end_date=2025-12-30" \
  -H "Authorization: Bearer $TOKEN"

# Get specific data record
curl -X GET http://localhost:8000/v1/data/123 \
  -H "Authorization: Bearer $TOKEN"

# Update data record
curl -X PUT http://localhost:8000/v1/data/123 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "consumption_kwh": 46.0,
    "cost_usd": 4.60
  }'

# Delete data record
curl -X DELETE http://localhost:8000/v1/data/123 \
  -H "Authorization: Bearer $TOKEN"
```

---

## Common Use Cases

### Use Case 1: Daily Energy Monitoring

Monitor daily energy consumption and receive predictions:

```python
import requests
from datetime import datetime, timedelta

# Configuration
API_BASE = "http://localhost:8000"
TOKEN = "your_access_token_here"
headers = {"Authorization": f"Bearer {TOKEN}"}

# Get yesterday's analytics
response = requests.get(
    f"{API_BASE}/v1/analytics/?period=week",
    headers=headers
)
analytics = response.json()

# Get next 7 days predictions
response = requests.get(
    f"{API_BASE}/v1/predictions/?days=7",
    headers=headers
)
predictions = response.json()

# Print summary
print("Energy Consumption Summary:")
print(f"Last 7 days average: {sum(a['consumption'] for a in analytics[-7:])/7:.2f} kWh")
print(f"Next 7 days predicted: {sum(p['predicted_consumption'] for p in predictions[:7])/7:.2f} kWh")
```

### Use Case 2: Anomaly Detection

Detect unusual consumption patterns:

```python
import pandas as pd
import numpy as np

# Get historical data
response = requests.get(
    f"{API_BASE}/v1/data/?start_date=2025-11-01&end_date=2025-12-30",
    headers=headers
)
data = pd.DataFrame(response.json())

# Calculate statistics
mean_consumption = data['consumption_kwh'].mean()
std_consumption = data['consumption_kwh'].std()

# Detect anomalies (values beyond 3 standard deviations)
anomalies = data[
    (data['consumption_kwh'] > mean_consumption + 3 * std_consumption) |
    (data['consumption_kwh'] < mean_consumption - 3 * std_consumption)
]

print(f"Detected {len(anomalies)} anomalies:")
print(anomalies[['timestamp', 'consumption_kwh']])
```

### Use Case 3: Model Retraining Pipeline

Automate model retraining on new data:

```python
from models.train import load_data_from_db, train_model, save_model
from core.logging_framework import get_logger

logger = get_logger(__name__)

def retrain_model():
    """Retrain model with latest data"""
    logger.info("Starting model retraining...")

    # Load latest data
    data_df = load_data_from_db()

    # Train new model
    model, metrics = train_model(data_df)

    # Save if performance improved
    if metrics['r2_score'] > 0.8:
        save_model(model)
        logger.info(f"New model saved. R2: {metrics['r2_score']:.4f}")
    else:
        logger.warning(f"Model performance below threshold: {metrics['r2_score']:.4f}")

    return metrics

# Run retraining
if __name__ == "__main__":
    metrics = retrain_model()
    print(metrics)
```

---

## Best Practices

### Security

```bash
# 1. Always use environment variables for sensitive data
export DATABASE_URL="postgresql://user:pass@localhost/fluxora"
export SECRET_KEY="your-secret-key-here"

# 2. Use strong passwords
# Minimum 12 characters with uppercase, lowercase, numbers, special chars

# 3. Enable HTTPS in production
# Configure nginx or use cloud load balancer with SSL certificate
```

### Performance

```python
# 1. Batch predictions for efficiency
data_batch = [record1, record2, record3]  # Process multiple records at once

# 2. Cache frequently accessed data
from functools import lru_cache

@lru_cache(maxsize=128)
def get_model_predictions(timestamp, meter_id):
    # Cached prediction function
    pass

# 3. Use connection pooling for database
# Already configured in backend.database module
```

### Monitoring

```bash
# 1. Check health endpoint regularly
curl http://localhost:8000/health

# 2. Monitor logs
tail -f logs/fluxora.log

# 3. Set up alerts for failures
# Configure Prometheus alerting rules in infrastructure/monitoring/
```

### Data Quality

```python
# 1. Validate input data
from core.data_validator import validate_energy_data

validated_data = validate_energy_data(raw_data)

# 2. Handle missing values
data_df.fillna(method='ffill', inplace=True)

# 3. Remove outliers before training
from scipy import stats
z_scores = np.abs(stats.zscore(data_df['consumption_kwh']))
data_df = data_df[z_scores < 3]
```

---

## Next Steps

- **[API Reference](API.md)** - Detailed API endpoint documentation
- **[CLI Reference](CLI.md)** - Complete CLI command guide
- **[Configuration](CONFIGURATION.md)** - Environment and config options
- **[Examples](examples/)** - More working code examples
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions

---

**Need Help?** Check the [Troubleshooting Guide](TROUBLESHOOTING.md) or open an issue on [GitHub](https://github.com/quantsingularity/Fluxora/issues).
