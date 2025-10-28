from typing import Dict, List, Union

import numpy as np
import pandas as pd

from fluxora.core.config import get_config


class FeaturePipeline:
    """
    Pipeline for transforming raw data into features for model prediction
    """

    def __init__(self):
        self.config = get_config()
        self.preprocessing_config = self.config.get("preprocessing", {})

    def transform(self, data):
        """
        Transform raw data into features for model prediction

        Args:
            data: PredictionRequest object containing timestamps, meter_ids, and context_features

        Returns:
            Processed features ready for model prediction
        """
        # Convert to DataFrame for easier processing
        df = pd.DataFrame({"timestamp": data.timestamps, "meter_id": data.meter_ids})

        # Add context features
        for feature_name, values in data.context_features.items():
            if isinstance(values, list) and len(values) == len(df):
                df[feature_name] = values
            else:
                # If a single value is provided, broadcast it to all rows
                df[feature_name] = values

        # Apply temporal feature extraction
        df = self._extract_temporal_features(df)

        # Apply feature normalization if configured
        if self.preprocessing_config.get("normalize", True):
            df = self._normalize_features(df)

        # Select only the features needed for the model
        feature_cols = self._get_feature_columns()
        features = df[feature_cols].values

        return features

    def _extract_temporal_features(self, df):
        """
        Extract temporal features from timestamp
        """
        # Convert timestamp to datetime if it's not already
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Extract basic time features
        df["hour"] = df["timestamp"].dt.hour
        df["day_of_week"] = df["timestamp"].dt.dayofweek
        df["month"] = df["timestamp"].dt.month
        df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

        # Extract cyclical time features
        df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
        df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
        df["day_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
        df["day_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)
        df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
        df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)

        return df

    def _normalize_features(self, df):
        """
        Normalize numerical features
        """
        # Get numerical columns excluding ID and timestamp columns
        num_cols = df.select_dtypes(include=["float64", "int64"]).columns
        num_cols = [col for col in num_cols if col not in ["meter_id"]]

        # Apply normalization
        for col in num_cols:
            mean = self.preprocessing_config.get(f"mean_{col}", df[col].mean())
            std = self.preprocessing_config.get(f"std_{col}", df[col].std())
            if std > 0:
                df[col] = (df[col] - mean) / std

        return df

    def _get_feature_columns(self):
        """
        Get the list of feature columns to use for the model
        """
        # Default feature columns
        default_features = [
            "hour_sin",
            "hour_cos",
            "day_sin",
            "day_cos",
            "month_sin",
            "month_cos",
            "is_weekend",
        ]

        # Add any context features that were provided
        context_features = self.preprocessing_config.get("context_features", [])

        return default_features + context_features
