# Advanced Energy Consumption Forecasting System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/)
[![MLflow](https://img.shields.io/badge/MLflow-Enabled-orange)](https://mlflow.org/)

An end-to-end MLOps solution for industrial-grade energy consumption forecasting, featuring automated retraining, real-time monitoring, and Kubernetes-native deployment.

## 🚀 Key Features

- **Multi-Model Serving**: XGBoost, LSTM, Prophet ensemble predictions  
- **MLOps Infrastructure**:
  - Kubernetes-native deployment with Istio  
  - MLflow Model Registry  
  - Feast Feature Store  
  - Prometheus/Grafana monitoring  
- **Data Quality Assurance**:
  - Great Expectations validations  
  - Temporal coherence checks  
  - Automated data drift detection  
- **Production-Grade API**:
  - JWT Authentication  
  - Rate limiting  
  - Canary deployments  
- **Smart Forecasting**:
  - Probabilistic predictions  
  - SHAP explainability  
  - Counterfactual analysis  

## 📦 Installation

### Prerequisites
- Kubernetes cluster (minikube supported)  
- Python 3.10+  
- Docker 20.10+  
- Apache Spark 3.3+  

```bash
# Clone repository
git clone https://github.com/abrar2030/Fluxora.git
cd Fluxora

# Initialize environment
make bootstrap && dvc pull


## 🛠️ Usage

### Data Pipeline
```bash
# Run complete data processing
make data_pipeline
```

### Model Training
```bash
# Train all models
make train

# Hyperparameter tuning
make tune
```

### Deployment
```bash
# Deploy to Kubernetes
make deploy_prod

# Monitor deployment
kubectl get pods -n energy-forecast
```

## 🌐 API Endpoints

| Endpoint       | Method | Description                     |
|----------------|--------|---------------------------------|
| `/predict`     | POST   | Get energy forecasts            |
| `/monitor`     | GET    | Model performance metrics       |
| `/retrain`     | POST   | Trigger model retraining        |
| `/health`      | GET    | System health status            |

### Sample Prediction Request:
```bash
curl -X POST http://api/predict \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $SECRET_KEY" \
  -d '{
    "timestamp": "2023-08-15T14:00:00",
    "meter_id": "MT_001",
    "historical_load": [0.45, 0.48, 0.52]
  }'
```

### Sample Response:
```json
{
  "prediction": 0.49,
  "confidence_interval": [0.46, 0.53],
  "model_version": "prod-v1.2.0",
  "shap_values": {
    "temperature": 0.12,
    "hour_of_day": -0.08
  }
}
```

## 📊 Monitoring Stack

Access monitoring tools:
```bash
# Grafana
open http://localhost:3000

# Prometheus
open http://localhost:9090

# MLflow UI
mlflow ui --port 5000
```

## 🧩 Project Structure
```
energy-forecasting/
├── deployments/          # Kubernetes manifests
├── feature_repo/         # Feast feature definitions
├── mlflow/               # Experiment tracking
├── monitoring/           # Grafana/Prometheus configs
├── pipelines/            # Prefect workflows
└── src/
    ├── api/              # FastAPI service
    ├── data/             # ETL pipelines
    ├── models/           # Model architectures
    ├── monitoring/       # Data drift detection
    └── visualization/    # Plotting utilities
```

## ⚙️ Configuration

Modify `config/config.yaml`:
```yaml
model:
  production_threshold: 0.85  # Minimum accuracy for deployment
  drift:
    threshold: 0.15           # Data drift alert level

feature_store:
  offline_store: s3://energy-data/features
  online_store: redis://redis:6379

api:
  rate_limit: "100/minute"
```

## 🤖 Model Versioning
```python
from src.models.model_versioning import promote_model

# Promote best performing model
promote_model(
    run_id="a1b2c3d4", 
    validation_metric="mae",
    threshold=0.45
)
```

## 🔍 Data Validation
```python
from src.data.data_validator import validate_energy_data

# Validate incoming data
validation_report = validate_energy_data(
    df, 
    expectation_suite="energy_suite"
)

if not validation_report.success:
    handle_invalid_data(validation_report)
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add some amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📜 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
```
