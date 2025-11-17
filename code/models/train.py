import logging
import os
from code.core.config import get_config
from code.features.build_features import FeaturePipeline

import mlflow
import numpy as np
import optuna
import pandas as pd
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)


def load_data():
    """
    Load training data from configured source

    Returns:
        DataFrame: Training data
    """
    config = get_config()
    data_source = config.get("data", {}).get("source", "")

    if data_source.startswith("s3://"):
        # Load from S3
        from io import StringIO

        import boto3

        s3_path = data_source.replace("s3://", "")
        bucket_name = s3_path.split("/")[0]
        key = "/".join(s3_path.split("/")[1:])

        s3 = boto3.client("s3")
        obj = s3.get_object(Bucket=bucket_name, Key=key)
        data = pd.read_csv(obj["Body"])
    else:
        # Load from local file
        data = pd.read_csv(data_source)

    return data


def prepare_training_data(data):
    """
    Prepare data for training

    Args:
        data: Raw data

    Returns:
        X_train, X_val, y_train, y_val: Training and validation data
    """
    # Extract features using the feature pipeline
    pipeline = FeaturePipeline()

    # Prepare data in the format expected by the pipeline
    from code.backend.schemas import PredictionRequest

    # Convert data to format expected by feature pipeline
    request_data = PredictionRequest(
        timestamps=data["timestamp"].tolist(),
        meter_ids=data["meter_id"].tolist(),
        context_features={
            col: data[col].tolist()
            for col in data.columns
            if col not in ["timestamp", "meter_id", "target"]
        },
    )

    # Transform features
    X = pipeline.transform(request_data)
    y = data["target"].values

    # Split into training and validation sets
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    return X_train, X_val, y_train, y_val


def train_xgboost_model(X_train, y_train, X_val, y_val, params=None):
    """
    Train an XGBoost model

    Args:
        X_train: Training features
        y_train: Training targets
        X_val: Validation features
        y_val: Validation targets
        params: Model parameters

    Returns:
        Trained model
    """
    import xgboost as xgb

    # Get default parameters from config if not provided
    if params is None:
        config = get_config()
        params = config.get("model", {}).get("xgboost", {})

    # Convert to DMatrix format
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dval = xgb.DMatrix(X_val, label=y_val)

    # Train model
    model = xgb.train(
        params,
        dtrain,
        num_boost_round=params.get("n_estimators", 100),
        evals=[(dtrain, "train"), (dval, "val")],
        early_stopping_rounds=10,
        verbose_eval=False,
    )

    return model


def train_lstm_model(X_train, y_train, X_val, y_val, params=None):
    """
    Train an LSTM model

    Args:
        X_train: Training features
        y_train: Training targets
        X_val: Validation features
        y_val: Validation targets
        params: Model parameters

    Returns:
        Trained model
    """
    import tensorflow as tf
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.models import Sequential

    # Get default parameters from config if not provided
    if params is None:
        config = get_config()
        params = config.get("model", {}).get("lstm", {})

    # Reshape input for LSTM [samples, timesteps, features]
    # Assuming 1 timestep for simplicity
    X_train_reshaped = X_train.reshape((X_train.shape[0], 1, X_train.shape[1]))
    X_val_reshaped = X_val.reshape((X_val.shape[0], 1, X_val.shape[1]))

    # Build model
    model = Sequential()
    model.add(
        LSTM(
            units=params.get("units", 50),
            input_shape=(1, X_train.shape[1]),
            return_sequences=False,
        )
    )
    model.add(Dropout(params.get("dropout", 0.2)))
    model.add(Dense(1))

    # Compile model
    model.compile(optimizer="adam", loss="mse", metrics=["mae"])

    # Train model
    model.fit(
        X_train_reshaped,
        y_train,
        epochs=params.get("epochs", 50),
        batch_size=params.get("batch_size", 32),
        validation_data=(X_val_reshaped, y_val),
        verbose=0,
        callbacks=[
            tf.keras.callbacks.EarlyStopping(
                monitor="val_loss", patience=5, restore_best_weights=True
            )
        ],
    )

    return model


def objective(trial):
    """
    Objective function for hyperparameter optimization

    Args:
        trial: Optuna trial object

    Returns:
        Validation error
    """
    # Load data
    data = load_data()
    X_train, X_val, y_train, y_val = prepare_training_data(data)

    # Get model type from config
    config = get_config()
    model_type = config.get("model", {}).get("type", "xgboost")

    if model_type == "xgboost":
        # Define hyperparameters to optimize
        params = {
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.1, log=True),
            "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
            "max_depth": trial.suggest_int("max_depth", 3, 10),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
            "objective": "reg:squarederror",
            "eval_metric": "rmse",
        }

        # Train model
        model = train_xgboost_model(X_train, y_train, X_val, y_val, params)

        # Evaluate model
        import xgboost as xgb

        dval = xgb.DMatrix(X_val, label=y_val)
        y_pred = model.predict(dval)

    elif model_type == "lstm":
        # Define hyperparameters to optimize
        params = {
            "units": trial.suggest_int("units", 32, 256),
            "dropout": trial.suggest_float("dropout", 0.1, 0.5),
            "batch_size": trial.suggest_int("batch_size", 16, 128),
            "epochs": 50,  # Fixed for optimization
        }

        # Train model
        model = train_lstm_model(X_train, y_train, X_val, y_val, params)

        # Evaluate model
        X_val_reshaped = X_val.reshape((X_val.shape[0], 1, X_val.shape[1]))
        y_pred = model.predict(X_val_reshaped).flatten()

    else:
        raise ValueError(f"Unsupported model type: {model_type}")

    # Calculate RMSE
    rmse = np.sqrt(np.mean((y_pred - y_val) ** 2))

    return rmse


def train_model():
    """
    Train a model with the best hyperparameters

    Returns:
        Trained model
    """
    # Start MLflow run
    mlflow.start_run()

    # Load data
    data = load_data()
    X_train, X_val, y_train, y_val = prepare_training_data(data)

    # Get model type from config
    config = get_config()
    model_type = config.get("model", {}).get("type", "xgboost")

    # Optimize hyperparameters
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=10)

    # Log best parameters
    best_params = study.best_params
    for param_name, param_value in best_params.items():
        mlflow.log_param(param_name, param_value)

    # Train model with best parameters
    if model_type == "xgboost":
        # Add fixed parameters
        best_params["objective"] = "reg:squarederror"
        best_params["eval_metric"] = "rmse"

        model = train_xgboost_model(X_train, y_train, X_val, y_val, best_params)

        # Save model
        model_dir = f"models/{model_type}/latest"
        os.makedirs(model_dir, exist_ok=True)
        model.save_model(f"{model_dir}/model.xgb")

        # Log model to MLflow
        mlflow.xgboost.log_model(model, "model")

    elif model_type == "lstm":
        model = train_lstm_model(X_train, y_train, X_val, y_val, best_params)

        # Save model
        model_dir = f"models/{model_type}/latest"
        os.makedirs(model_dir, exist_ok=True)
        model.save(f"{model_dir}/model")

        # Log model to MLflow
        mlflow.tensorflow.log_model(model, "model")

    else:
        raise ValueError(f"Unsupported model type: {model_type}")

    # End MLflow run
    mlflow.end_run()

    return model


if __name__ == "__main__":
    train_model()
