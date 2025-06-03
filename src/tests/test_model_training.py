"""
Unit tests for the model training logic.
"""
import pytest
import numpy as np
import pandas as pd
import os
import tempfile
from unittest.mock import patch, MagicMock

# Import the functions to test
from src.models.train import (
    load_data,
    prepare_training_data,
    train_xgboost_model,
    train_lstm_model,
    objective,
    train_model
)

@pytest.fixture
def sample_data():
    """Create sample data for model training tests."""
    # Create a DataFrame with features and target
    np.random.seed(42)
    n_samples = 100
    
    data = pd.DataFrame({
        'feature1': np.random.normal(0, 1, n_samples),
        'feature2': np.random.normal(0, 1, n_samples),
        'feature3': np.random.normal(0, 1, n_samples),
        'target': np.random.normal(0, 1, n_samples)
    })
    
    return data

@pytest.fixture
def prepared_data(sample_data):
    """Create prepared training and validation data."""
    X = sample_data[['feature1', 'feature2', 'feature3']].values
    y = sample_data['target'].values
    
    # Split into train and validation sets (80/20)
    split_idx = int(len(X) * 0.8)
    X_train, X_val = X[:split_idx], X[split_idx:]
    y_train, y_val = y[:split_idx], y[split_idx:]
    
    return X_train, X_val, y_train, y_val

@patch('src.models.train.load_data')
def test_prepare_training_data(mock_load_data, sample_data):
    """Test data preparation for training."""
    mock_load_data.return_value = sample_data
    
    X_train, X_val, y_train, y_val = prepare_training_data(sample_data)
    
    # Check shapes
    assert X_train.shape[1] == 3  # 3 features
    assert X_val.shape[1] == 3
    assert len(y_train.shape) == 1
    assert len(y_val.shape) == 1
    
    # Check train/val split
    assert X_train.shape[0] > X_val.shape[0]
    assert y_train.shape[0] == X_train.shape[0]
    assert y_val.shape[0] == X_val.shape[0]

@patch('src.models.train.xgb')
def test_train_xgboost_model(mock_xgb, prepared_data):
    """Test XGBoost model training."""
    X_train, X_val, y_train, y_val = prepared_data
    
    # Create mock XGBoost model
    mock_model = MagicMock()
    mock_xgb.train.return_value = mock_model
    
    # Define parameters
    params = {
        'learning_rate': 0.1,
        'n_estimators': 100,
        'max_depth': 5,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'min_child_weight': 1,
        'objective': 'reg:squarederror',
        'eval_metric': 'rmse'
    }
    
    # Train model
    model = train_xgboost_model(X_train, y_train, X_val, y_val, params)
    
    # Verify XGBoost was called correctly
    assert mock_xgb.DMatrix.call_count == 2  # Once for train, once for validation
    assert mock_xgb.train.call_count == 1
    
    # Verify model was returned
    assert model == mock_model

@patch('src.models.train.Sequential')
@patch('src.models.train.LSTM')
@patch('src.models.train.Dense')
@patch('src.models.train.Dropout')
def test_train_lstm_model(mock_dropout, mock_dense, mock_lstm, mock_sequential, prepared_data):
    """Test LSTM model training."""
    X_train, X_val, y_train, y_val = prepared_data
    
    # Create mock Sequential model
    mock_model = MagicMock()
    mock_sequential.return_value = mock_model
    
    # Define parameters
    params = {
        'units': 50,
        'dropout': 0.2,
        'batch_size': 32,
        'epochs': 10
    }
    
    # Train model
    model = train_lstm_model(X_train, y_train, X_val, y_val, params)
    
    # Verify model creation
    assert mock_sequential.call_count == 1
    assert mock_lstm.call_count == 1
    assert mock_dropout.call_count == 1
    assert mock_dense.call_count == 1
    
    # Verify model compilation and training
    assert mock_model.compile.call_count == 1
    assert mock_model.fit.call_count == 1
    
    # Verify model was returned
    assert model == mock_model

@patch('src.models.train.load_data')
@patch('src.models.train.prepare_training_data')
@patch('src.models.train.get_config')
@patch('src.models.train.xgb')
def test_objective_xgboost(mock_xgb, mock_get_config, mock_prepare_data, mock_load_data, prepared_data, sample_data):
    """Test objective function with XGBoost model."""
    X_train, X_val, y_train, y_val = prepared_data
    mock_load_data.return_value = sample_data
    mock_prepare_data.return_value = (X_train, X_val, y_train, y_val)
    
    # Mock config to return XGBoost as model type
    mock_get_config.return_value = {'model': {'type': 'xgboost'}}
    
    # Create mock XGBoost model
    mock_model = MagicMock()
    mock_model.predict.return_value = y_val  # For simplicity, predict same as actual
    mock_xgb.train.return_value = mock_model
    
    # Create mock trial
    mock_trial = MagicMock()
    mock_trial.suggest_float.return_value = 0.1
    mock_trial.suggest_int.return_value = 5
    
    # Run objective function
    rmse = objective(mock_trial)
    
    # Verify RMSE is a float
    assert isinstance(rmse, float)
    
    # Verify trial suggestions were used
    assert mock_trial.suggest_float.call_count >= 3  # learning_rate, subsample, colsample_bytree
    assert mock_trial.suggest_int.call_count >= 3  # n_estimators, max_depth, min_child_weight

@patch('src.models.train.load_data')
@patch('src.models.train.prepare_training_data')
@patch('src.models.train.get_config')
@patch('src.models.train.Sequential')
def test_objective_lstm(mock_sequential, mock_get_config, mock_prepare_data, mock_load_data, prepared_data, sample_data):
    """Test objective function with LSTM model."""
    X_train, X_val, y_train, y_val = prepared_data
    mock_load_data.return_value = sample_data
    mock_prepare_data.return_value = (X_train, X_val, y_train, y_val)
    
    # Mock config to return LSTM as model type
    mock_get_config.return_value = {'model': {'type': 'lstm'}}
    
    # Create mock Sequential model
    mock_model = MagicMock()
    mock_model.predict.return_value = np.expand_dims(y_val, axis=1)  # Reshape to match LSTM output
    mock_sequential.return_value = mock_model
    
    # Create mock trial
    mock_trial = MagicMock()
    mock_trial.suggest_int.return_value = 64
    mock_trial.suggest_float.return_value = 0.3
    
    # Run objective function
    rmse = objective(mock_trial)
    
    # Verify RMSE is a float
    assert isinstance(rmse, float)
    
    # Verify trial suggestions were used
    assert mock_trial.suggest_int.call_count >= 2  # units, batch_size
    assert mock_trial.suggest_float.call_count >= 1  # dropout

@patch('src.models.train.mlflow')
@patch('src.models.train.optuna')
@patch('src.models.train.load_data')
@patch('src.models.train.prepare_training_data')
@patch('src.models.train.get_config')
@patch('src.models.train.train_xgboost_model')
@patch('src.models.train.os.makedirs')
def test_train_model_xgboost(mock_makedirs, mock_train_xgb, mock_get_config, 
                            mock_prepare_data, mock_load_data, mock_optuna, mock_mlflow, 
                            prepared_data, sample_data):
    """Test full model training pipeline with XGBoost."""
    X_train, X_val, y_train, y_val = prepared_data
    mock_load_data.return_value = sample_data
    mock_prepare_data.return_value = (X_train, X_val, y_train, y_val)
    
    # Mock config to return XGBoost as model type
    mock_get_config.return_value = {'model': {'type': 'xgboost'}}
    
    # Create mock study and best trial
    mock_study = MagicMock()
    mock_study.best_params = {
        'learning_rate': 0.05,
        'n_estimators': 200,
        'max_depth': 6,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'min_child_weight': 3
    }
    mock_optuna.create_study.return_value = mock_study
    
    # Create mock XGBoost model
    mock_model = MagicMock()
    mock_train_xgb.return_value = mock_model
    
    # Run train_model
    model = train_model()
    
    # Verify MLflow was used
    assert mock_mlflow.start_run.call_count == 1
    assert mock_mlflow.log_param.call_count >= 1
    assert mock_mlflow.end_run.call_count == 1
    
    # Verify model was trained and saved
    assert mock_train_xgb.call_count == 1
    assert mock_model.save_model.call_count == 1
    
    # Verify model was returned
    assert model == mock_model

@patch('src.models.train.mlflow')
@patch('src.models.train.optuna')
@patch('src.models.train.load_data')
@patch('src.models.train.prepare_training_data')
@patch('src.models.train.get_config')
@patch('src.models.train.train_lstm_model')
@patch('src.models.train.os.makedirs')
def test_train_model_lstm(mock_makedirs, mock_train_lstm, mock_get_config, 
                         mock_prepare_data, mock_load_data, mock_optuna, mock_mlflow, 
                         prepared_data, sample_data):
    """Test full model training pipeline with LSTM."""
    X_train, X_val, y_train, y_val = prepared_data
    mock_load_data.return_value = sample_data
    mock_prepare_data.return_value = (X_train, X_val, y_train, y_val)
    
    # Mock config to return LSTM as model type
    mock_get_config.return_value = {'model': {'type': 'lstm'}}
    
    # Create mock study and best trial
    mock_study = MagicMock()
    mock_study.best_params = {
        'units': 128,
        'dropout': 0.3,
        'batch_size': 64
    }
    mock_optuna.create_study.return_value = mock_study
    
    # Create mock LSTM model
    mock_model = MagicMock()
    mock_train_lstm.return_value = mock_model
    
    # Run train_model
    model = train_model()
    
    # Verify MLflow was used
    assert mock_mlflow.start_run.call_count == 1
    assert mock_mlflow.log_param.call_count >= 1
    assert mock_mlflow.end_run.call_count == 1
    
    # Verify model was trained and saved
    assert mock_train_lstm.call_count == 1
    assert mock_model.save.call_count == 1
    
    # Verify model was returned
    assert model == mock_model

def test_invalid_model_type():
    """Test handling of invalid model type."""
    with patch('src.models.train.get_config') as mock_get_config:
        # Mock config to return invalid model type
        mock_get_config.return_value = {'model': {'type': 'invalid_model'}}
        
        # Create mock trial
        mock_trial = MagicMock()
        
        # Run objective function, should raise ValueError
        with pytest.raises(ValueError, match="Unsupported model type"):
            objective(mock_trial)
