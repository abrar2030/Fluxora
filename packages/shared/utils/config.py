# packages/shared/utils/config.py
"""Configuration settings for the application."""

from packages.shared.utils.logger import get_logger

# Initialize logger for this module
logger = get_logger(__name__)

# Example column mapping for data drift and other processes
# This should be customized based on the actual dataset structure
column_mapping = {
    "target": "target_variable_name", # Name of the target variable column
    "prediction": "prediction_score_name", # Name of the prediction score column (if applicable)
    "datetime": "timestamp_column_name", # Name of the datetime column for time-series data
    
    # List of numerical features
    "numerical_features": [
        "feature1", 
        "feature2", 
        # ... add other numerical feature names
    ],
    
    # List of categorical features
    "categorical_features": [
        "category_a", 
        "category_b",
        # ... add other categorical feature names
    ],
    
    # Optional: ID column if applicable
    "id_column": "unique_identifier_column"
}

# Example: Model training parameters
model_params = {
    "model_type": "RandomForestClassifier", # or "XGBoost", "LightGBM", etc.
    "random_state": 42,
    "n_estimators": 100,
    "max_depth": 10
}

# Example: API settings
api_settings = {
    "host": "0.0.0.0",
    "port": 8000
}

# Example: Feature Store settings (if used)
feature_store_config = {
    "type": "file_based", # or "feast", "tecton", "in_memory"
    "path": "data/feature_store_db" # if file_based
}

logger.info("Configuration loaded.")

