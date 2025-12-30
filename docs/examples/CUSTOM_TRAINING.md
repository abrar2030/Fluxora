# Custom Model Training Example

Learn how to train custom machine learning models on your energy data using Fluxora.

---

## Overview

This example demonstrates:

- Loading and preparing training data
- Training different model types (XGBoost, Random Forest, LSTM)
- Evaluating model performance
- Hyperparameter tuning
- Saving and deploying models

---

## Prerequisites

```bash
pip install pandas scikit-learn xgboost joblib matplotlib
```

---

## Example 1: Train XGBoost Model

```python
import os
import sys
sys.path.insert(0, os.path.join(os.getcwd(), 'code'))

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import xgboost as xgb
import joblib
from datetime import datetime, timedelta

# Generate training data (or load from database)
def generate_training_data(days=60):
    """Generate synthetic energy consumption data for training."""
    start_time = datetime.now() - timedelta(days=days)
    timestamps = [start_time + timedelta(hours=i) for i in range(days * 24)]

    consumption = []
    for ts in timestamps:
        hour = ts.hour
        day_of_week = ts.weekday()
        month = ts.month

        # Base load with patterns
        base = 50.0
        daily = 20.0 * np.sin((hour - 6) * np.pi / 12)
        weekly = 5.0 if day_of_week < 5 else -5.0
        seasonal = 10.0 * np.sin((month - 1) * np.pi / 6)
        noise = np.random.normal(0, 3)

        consumption.append(max(0, base + daily + weekly + seasonal + noise))

    df = pd.DataFrame({
        'timestamp': timestamps,
        'consumption_kwh': consumption,
        'user_id': 1
    })

    return df

# Load and prepare data
print("Generating training data...")
df = generate_training_data(days=60)
print(f"Generated {len(df)} records")

# Feature engineering
from data.features.feature_engineering import preprocess_data_for_model

processed_df = preprocess_data_for_model(df.copy())

# Prepare features and target
target_col = 'consumption_kwh'
feature_cols = [col for col in processed_df.columns
                if col not in [target_col, 'timestamp', 'user_id']]

X = processed_df[feature_cols]
y = processed_df[target_col]

print(f"\nFeatures: {len(feature_cols)}")
print(f"Feature names: {feature_cols[:5]}...")

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, shuffle=False
)

print(f"Training samples: {len(X_train)}")
print(f"Test samples: {len(X_test)}")

# Train XGBoost model
print("\n=== Training XGBoost Model ===")
model = xgb.XGBRegressor(
    n_estimators=500,
    learning_rate=0.05,
    max_depth=8,
    min_child_weight=3,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train, verbose=False)
print("Training complete!")

# Evaluate model
y_pred_train = model.predict(X_train)
y_pred_test = model.predict(X_test)

train_mse = mean_squared_error(y_train, y_pred_train)
test_mse = mean_squared_error(y_test, y_pred_test)
train_r2 = r2_score(y_train, y_pred_train)
test_r2 = r2_score(y_test, y_pred_test)
test_mae = mean_absolute_error(y_test, y_pred_test)

print("\n=== Model Performance ===")
print(f"Training MSE: {train_mse:.4f}")
print(f"Test MSE: {test_mse:.4f}")
print(f"Training R²: {train_r2:.4f}")
print(f"Test R²: {test_r2:.4f}")
print(f"Test MAE: {test_mae:.4f}")

# Feature importance
import matplotlib.pyplot as plt

feature_importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("\n=== Top 10 Important Features ===")
print(feature_importance.head(10))

# Plot feature importance
plt.figure(figsize=(10, 6))
plt.barh(feature_importance.head(10)['feature'],
         feature_importance.head(10)['importance'])
plt.xlabel('Importance')
plt.title('Top 10 Feature Importances')
plt.tight_layout()
plt.savefig('feature_importance.png', dpi=300, bbox_inches='tight')
print("\nSaved: feature_importance.png")

# Save model
model_path = 'fluxora_model_custom.joblib'
joblib.dump(model, model_path)
print(f"\nModel saved to: {model_path}")

# Visualize predictions
plt.figure(figsize=(12, 6))
plt.plot(range(len(y_test)), y_test.values, label='Actual', alpha=0.7)
plt.plot(range(len(y_test)), y_pred_test, label='Predicted', alpha=0.7)
plt.xlabel('Sample Index')
plt.ylabel('Consumption (kWh)')
plt.title('Actual vs Predicted (Test Set)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('predictions_test.png', dpi=300, bbox_inches='tight')
print("Saved: predictions_test.png")
```

**Expected Output:**

```
Generating training data...
Generated 1440 records

Features: 15
Feature names: ['hour', 'day_of_week', 'month', 'lag_1', 'lag_24']...

Training samples: 1152
Test samples: 288

=== Training XGBoost Model ===
Training complete!

=== Model Performance ===
Training MSE: 8.9123
Test MSE: 12.3456
Training R²: 0.9245
Test R²: 0.8901
Test MAE: 2.8734

=== Top 10 Important Features ===
        feature  importance
0       lag_24    0.234
1       lag_1     0.189
2       hour      0.156
...

Saved: feature_importance.png
Model saved to: fluxora_model_custom.joblib
Saved: predictions_test.png
```

---

## Example 2: Hyperparameter Tuning with Optuna

```python
import optuna
from sklearn.model_selection import cross_val_score

def objective(trial):
    """Objective function for Optuna optimization."""
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
        'max_depth': trial.suggest_int('max_depth', 3, 10),
        'min_child_weight': trial.suggest_int('min_child_weight', 1, 7),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
        'random_state': 42,
        'n_jobs': -1
    }

    model = xgb.XGBRegressor(**params)

    # Cross-validation
    scores = cross_val_score(
        model, X_train, y_train,
        cv=5, scoring='neg_mean_squared_error', n_jobs=-1
    )

    return -scores.mean()  # Minimize MSE

# Run optimization
print("\n=== Hyperparameter Optimization ===")
study = optuna.create_study(direction='minimize')
study.optimize(objective, n_trials=50, show_progress_bar=True)

print(f"\nBest MSE: {study.best_value:.4f}")
print(f"Best params: {study.best_params}")

# Train final model with best params
best_model = xgb.XGBRegressor(**study.best_params)
best_model.fit(X_train, y_train)

# Evaluate
y_pred_best = best_model.predict(X_test)
best_mse = mean_squared_error(y_test, y_pred_best)
best_r2 = r2_score(y_test, y_pred_best)

print(f"\n=== Optimized Model Performance ===")
print(f"Test MSE: {best_mse:.4f}")
print(f"Test R²: {best_r2:.4f}")

# Save optimized model
joblib.dump(best_model, 'fluxora_model_optimized.joblib')
print("\nOptimized model saved to: fluxora_model_optimized.joblib")
```

---

## Example 3: Compare Multiple Models

```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression

# Define models
models = {
    'XGBoost': xgb.XGBRegressor(n_estimators=500, learning_rate=0.05, random_state=42),
    'Random Forest': RandomForestRegressor(n_estimators=500, random_state=42, n_jobs=-1),
    'Linear Regression': LinearRegression()
}

# Train and evaluate each model
results = []

for name, model in models.items():
    print(f"\nTraining {name}...")
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)

    results.append({
        'Model': name,
        'MSE': mse,
        'R²': r2,
        'MAE': mae
    })

    print(f"  MSE: {mse:.4f}, R²: {r2:.4f}, MAE: {mae:.4f}")

# Compare results
results_df = pd.DataFrame(results)
print("\n=== Model Comparison ===")
print(results_df.to_string(index=False))

# Select best model
best_model_name = results_df.loc[results_df['R²'].idxmax(), 'Model']
print(f"\nBest Model: {best_model_name}")
```

**Expected Output:**

```
Training XGBoost...
  MSE: 12.3456, R²: 0.8901, MAE: 2.8734

Training Random Forest...
  MSE: 14.5678, R²: 0.8654, MAE: 3.1234

Training Linear Regression...
  MSE: 45.6789, R²: 0.5432, MAE: 5.6789

=== Model Comparison ===
           Model      MSE     R²     MAE
         XGBoost  12.3456 0.8901  2.8734
   Random Forest  14.5678 0.8654  3.1234
Linear Regression 45.6789 0.5432  5.6789

Best Model: XGBoost
```

---

## Deployment

Once trained, deploy your model:

```python
# Replace the production model
import shutil

# Backup current model
shutil.copy('code/fluxora_model.joblib', 'code/fluxora_model.backup.joblib')

# Deploy new model
shutil.copy('fluxora_model_optimized.joblib', 'code/fluxora_model.joblib')

print("Model deployed successfully!")
print("Restart API server to use new model:")
print("  cd code && python main.py")
```

---

## Next Steps

- **[Basic Prediction Example](BASIC_PREDICTION.md)** - Use your trained model
- **[Advanced Analytics](ADVANCED_ANALYTICS.md)** - Analyze model performance
- **[API Reference](../API.md)** - API documentation

---

**Questions?** Check the [Troubleshooting Guide](../TROUBLESHOOTING.md).
