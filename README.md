# Energy Consumption Time Series Forecasting

![GitHub](https://img.shields.io/github/license/yourusername/energy_forecasting)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![CI/CD](https://github.com/yourusername/energy_forecasting/actions/workflows/main.yml/badge.svg)

An end-to-end MLOps project for forecasting household energy consumption using machine learning and deep learning models, featuring Docker deployment and CI/CD pipelines.

## 📌 Features

- **Models**: XGBoost, LSTM (TensorFlow), and Facebook Prophet
- **MLOps Components**:
  - Data versioning & preprocessing pipelines
  - Hyperparameter tuning with Optuna
  - Dockerized Flask API
  - CI/CD with GitHub Actions
  - Logging & configuration management
- Advanced time series features:
  - Lag features
  - Rolling statistics
  - Custom seasonality (Prophet)

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Docker (for API deployment)
- Make (optional)

### Installation
```bash
git clone https://github.com/yourusername/energy_forecasting.git
cd energy_forecasting
pip install -r requirements.txt
```

### Usage

#### Download data:
```bash
make download_data
```

#### Preprocess data and train models:
```bash
make train
```

#### Start prediction API:
```bash
make run_api
```

## 📂 Project Structure
```
energy_forecasting/
├── data/               # Data storage
├── models/             # Serialized models
├── notebooks/          # Jupyter notebooks for EDA
├── src/                # Source code
│   ├── api/            # Flask API implementation
│   ├── data_processing/ # Data pipelines
│   ├── models/         # Model implementations
│   ├── evaluation/     # Metrics & backtesting
│   └── utils/          # Helper functions
├── tests/              # Unit tests
├── config/             # Configuration files
└── .github/workflows/  # CI/CD pipelines
```

## ⚙️ Configuration
Modify `config/config.yaml` for:

- Data paths
- Model hyperparameters
- API settings

```yaml
data:
  url: "https://archive.ics.uci.edu/ml/machine-learning-databases/00321/LD2011_2014.txt.zip"
models:
  lstm_params:
    epochs: 100
api:
  port: 5000
```

## 🌐 API Usage
After starting the API:

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"data": [0.5, 25, 3, 0.48, 0.52, 0.6]}'
```

**Response:**
```json
{"prediction": [0.723]}
```

## 📊 Model Evaluation
Metrics calculated during training:

- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- MAPE (Mean Absolute Percentage Error)

Run evaluation:
```python
from src.evaluation.evaluate import backtest
results = backtest(model, X_test, y_test, model_type='xgboost')
```

## 🔧 Testing
Run unit tests:
```bash
pytest tests/
```

## 🤖 MLOps Features

### Prefect Data Pipeline:
```python
from prefect import flow

@flow
def main_pipeline():
    download_data()
    preprocess()
    train_models()
```

### Optuna Hyperparameter Tuning:
```bash
python src/models/tune.py
```

### CI/CD Pipeline:
- Automatic testing on push/pull requests
- Model performance validation

## 📈 Results
Example forecasting results (from `notebooks/EDA.ipynb`):
- Daily Seasonality
- Weekly & yearly patterns
- Error distribution plots

## 🤝 Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License
MIT License - see [LICENSE](LICENSE) for details

## 📚 Acknowledgments
- UCI Machine Learning Repository for dataset
- Facebook Prophet team
- XGBoost & TensorFlow developers

---

**This README includes**:
- Badges for quick project status
- Visual hierarchy with emojis
- Clear installation/usage instructions
- API examples
- Contribution guidelines
- License information
- Mobile-friendly formatting

**To Use**:
1. Replace `yourusername` in URLs with your GitHub username
2. Add actual screenshots to `docs/images/`
3. Customize the "Acknowledgments" section as needed
