"""
Enhanced drift detection and automated model retraining module.

This module provides functionality to:
1. Detect data drift using statistical methods
2. Trigger automated model retraining when significant drift is detected
3. Log and alert on drift detection and retraining events
4. Track model performance metrics over time
"""

import os
import sys
import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import subprocess
from typing import Dict, Tuple, Optional, Union, List, Any

# Import evidently for drift detection
try:
    from evidently.report import Report
    from evidently.metrics import DataDriftTable
    from evidently.metric_preset import DataDriftPreset
    from evidently.test_suite import TestSuite
    from evidently.test_preset import DataDriftTestPreset
    from evidently.tests import *
except ImportError:
    logging.error("Evidently not installed. Please install with: pip install evidently")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("drift_detection.log")
    ]
)
logger = logging.getLogger("drift_detector")

# Import project-specific modules
try:
    from src.utils.config import get_config
    from src.utils.alert_handler import AlertHandler
    config = get_config()
    alert_handler = AlertHandler()
except ImportError:
    # Fallback for standalone testing
    logger.warning("Could not import project modules, using mock config")
    
    class MockConfig:
        def __init__(self):
            self.column_mapping = {
                "numerical_features": ["feature1", "feature2"],
                "categorical_features": ["category_a"],
                "target": "target"
            }
            self.drift_threshold = 0.05
            self.retraining_cooldown_hours = 24
            self.model_registry_path = "models/registry"
            
    config = MockConfig()
    
    class MockAlertHandler:
        def trigger_alert(self, alert_type, details=None, level="INFO"):
            logger.info(f"ALERT [{level}] {alert_type}: {details}")
            
    alert_handler = MockAlertHandler()

class DriftDetector:
    """Class for detecting data drift and triggering model retraining."""
    
    def __init__(self, 
                 reference_data: pd.DataFrame = None,
                 reference_data_path: str = None,
                 column_mapping: Dict = None,
                 drift_threshold: float = None,
                 retraining_cooldown_hours: int = None,
                 model_registry_path: str = None,
                 retraining_script_path: str = None):
        """
        Initialize the drift detector.
        
        Args:
            reference_data: DataFrame containing reference data (e.g., training data)
            reference_data_path: Path to saved reference data (alternative to reference_data)
            column_mapping: Dictionary mapping column types (numerical, categorical, target)
            drift_threshold: Threshold for drift detection (0-1)
            retraining_cooldown_hours: Minimum hours between retraining triggers
            model_registry_path: Path to model registry for tracking versions
            retraining_script_path: Path to script that performs model retraining
        """
        # Load reference data if path is provided
        if reference_data is None and reference_data_path:
            try:
                if reference_data_path.endswith('.csv'):
                    self.reference_data = pd.read_csv(reference_data_path)
                elif reference_data_path.endswith('.parquet'):
                    self.reference_data = pd.read_parquet(reference_data_path)
                else:
                    raise ValueError(f"Unsupported file format: {reference_data_path}")
            except Exception as e:
                logger.error(f"Error loading reference data: {e}")
                self.reference_data = None
        else:
            self.reference_data = reference_data
            
        # Set configuration
        self.column_mapping = column_mapping or config.column_mapping
        self.drift_threshold = drift_threshold or getattr(config, 'drift_threshold', 0.05)
        self.retraining_cooldown_hours = retraining_cooldown_hours or getattr(config, 'retraining_cooldown_hours', 24)
        self.model_registry_path = model_registry_path or getattr(config, 'model_registry_path', 'models/registry')
        self.retraining_script_path = retraining_script_path or getattr(config, 'retraining_script_path', 'src/models/train.py')
        
        # Initialize retraining tracking
        self.last_retraining_time = self._load_last_retraining_time()
        self.drift_history = self._load_drift_history()
        
        logger.info(f"DriftDetector initialized with threshold {self.drift_threshold}")
        
    def _load_last_retraining_time(self) -> Optional[datetime]:
        """Load the timestamp of the last model retraining."""
        try:
            registry_file = os.path.join(self.model_registry_path, 'retraining_history.json')
            if os.path.exists(registry_file):
                with open(registry_file, 'r') as f:
                    history = json.load(f)
                    if history and 'last_retraining_time' in history:
                        return datetime.fromisoformat(history['last_retraining_time'])
        except Exception as e:
            logger.error(f"Error loading retraining history: {e}")
        return None
        
    def _save_last_retraining_time(self, timestamp: datetime) -> None:
        """Save the timestamp of the last model retraining."""
        try:
            os.makedirs(self.model_registry_path, exist_ok=True)
            registry_file = os.path.join(self.model_registry_path, 'retraining_history.json')
            
            history = {}
            if os.path.exists(registry_file):
                with open(registry_file, 'r') as f:
                    history = json.load(f)
            
            history['last_retraining_time'] = timestamp.isoformat()
            history.setdefault('retraining_history', []).append({
                'timestamp': timestamp.isoformat(),
                'trigger': 'data_drift'
            })
            
            with open(registry_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving retraining history: {e}")
    
    def _load_drift_history(self) -> List[Dict]:
        """Load the history of drift detection results."""
        try:
            history_file = os.path.join(self.model_registry_path, 'drift_history.json')
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading drift history: {e}")
        return []
    
    def _save_drift_history(self, drift_detected: bool, drift_score: float, details: Dict = None) -> None:
        """Save drift detection results to history."""
        try:
            os.makedirs(self.model_registry_path, exist_ok=True)
            history_file = os.path.join(self.model_registry_path, 'drift_history.json')
            
            history = self.drift_history
            history.append({
                'timestamp': datetime.now().isoformat(),
                'drift_detected': drift_detected,
                'drift_score': drift_score,
                'details': details or {}
            })
            
            # Keep only the last 100 entries to avoid file growth
            if len(history) > 100:
                history = history[-100:]
            
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
                
            self.drift_history = history
        except Exception as e:
            logger.error(f"Error saving drift history: {e}")
    
    def detect_drift(self, 
                    current_data: pd.DataFrame, 
                    reference_data: pd.DataFrame = None,
                    column_mapping_override: Dict = None) -> Tuple[Optional[Report], bool, float]:
        """
        Detect data drift between current data and reference data.
        
        Args:
            current_data: DataFrame containing current data to check for drift
            reference_data: DataFrame containing reference data (optional, uses self.reference_data if None)
            column_mapping_override: Optional override for column mapping
            
        Returns:
            Tuple of (drift_report, drift_detected, drift_score)
        """
        if reference_data is None:
            reference_data = self.reference_data
            
        if reference_data is None:
            logger.error("No reference data provided for drift detection")
            return None, False, 0.0
            
        column_mapping = column_mapping_override or self.column_mapping
        
        try:
            # Create data drift report
            data_drift_report = Report(metrics=[
                DataDriftPreset(num_feature_names=column_mapping.get("numerical_features", []),
                               cat_feature_names=column_mapping.get("categorical_features", []))
            ])
            
            # Calculate drift
            data_drift_report.run(reference_data=reference_data, current_data=current_data)
            
            # Extract drift information - structure depends on evidently version
            drift_info = data_drift_report.as_dict().get("data_drift", {})
            
            # Get dataset drift flag
            dataset_drift_detected = drift_info.get("data", {}).get("metrics", {}).get("dataset_drift", False)
            
            # Fallback if the above path is not found, check older/alternative structures
            if not isinstance(dataset_drift_detected, bool):
                dataset_drift_detected = drift_info.get("metrics", [{}])[0].get("dataset_drift", False)
            
            # Calculate drift score (average of feature drift scores)
            drift_scores = []
            
            # Extract feature drift scores - structure depends on evidently version
            features = drift_info.get("data", {}).get("metrics", {}).get("features", {})
            if not features:
                features = {}
                for metric in drift_info.get("metrics", []):
                    if "features" in metric:
                        features = metric["features"]
                        break
            
            # Calculate average drift score across features
            for feature_name, feature_data in features.items():
                drift_score = feature_data.get("drift_score", None)
                if drift_score is not None:
                    drift_scores.append(drift_score)
            
            avg_drift_score = np.mean(drift_scores) if drift_scores else 0.0
            
            # Override drift detection based on threshold if needed
            if avg_drift_score > self.drift_threshold:
                dataset_drift_detected = True
            
            # Log and save results
            if dataset_drift_detected:
                logger.warning(f"DATA DRIFT DETECTED! Average drift score: {avg_drift_score:.4f}")
                alert_handler.trigger_alert(
                    "DATA_DRIFT_ALERT",
                    details={
                        "drift_score": avg_drift_score,
                        "threshold": self.drift_threshold,
                        "message": "Significant data drift detected in the dataset."
                    },
                    level="WARNING"
                )
            else:
                logger.info(f"No significant data drift detected. Average drift score: {avg_drift_score:.4f}")
            
            # Save drift history
            self._save_drift_history(
                drift_detected=dataset_drift_detected,
                drift_score=avg_drift_score,
                details={"feature_scores": {k: v.get("drift_score", 0) for k, v in features.items()}}
            )
            
            return data_drift_report, dataset_drift_detected, avg_drift_score
            
        except Exception as e:
            logger.error(f"Error during data drift detection: {e}")
            alert_handler.trigger_alert(
                "DRIFT_DETECTION_ERROR",
                details={"error_message": str(e)},
                level="ERROR"
            )
            return None, False, 0.0
    
    def should_trigger_retraining(self) -> bool:
        """
        Check if retraining should be triggered based on cooldown period.
        
        Returns:
            bool: True if retraining should be triggered, False otherwise
        """
        if self.last_retraining_time is None:
            return True
            
        cooldown_delta = timedelta(hours=self.retraining_cooldown_hours)
        time_since_last_retraining = datetime.now() - self.last_retraining_time
        
        return time_since_last_retraining > cooldown_delta
    
    def trigger_retraining(self) -> bool:
        """
        Trigger model retraining process.
        
        Returns:
            bool: True if retraining was triggered successfully, False otherwise
        """
        if not self.should_trigger_retraining():
            logger.info(f"Retraining cooldown period not elapsed. Last retraining: {self.last_retraining_time}")
            return False
            
        try:
            logger.info("Triggering model retraining...")
            
            # Check if retraining script exists
            if not os.path.exists(self.retraining_script_path):
                logger.error(f"Retraining script not found at {self.retraining_script_path}")
                return False
                
            # Execute retraining script
            result = subprocess.run(
                ["python", self.retraining_script_path, "--trigger=drift"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("Model retraining triggered successfully")
                self._save_last_retraining_time(datetime.now())
                
                alert_handler.trigger_alert(
                    "MODEL_RETRAINING_TRIGGERED",
                    details={"trigger": "data_drift", "status": "success"},
                    level="INFO"
                )
                return True
            else:
                logger.error(f"Model retraining failed: {result.stderr}")
                
                alert_handler.trigger_alert(
                    "MODEL_RETRAINING_FAILED",
                    details={"trigger": "data_drift", "error": result.stderr},
                    level="ERROR"
                )
                return False
                
        except Exception as e:
            logger.error(f"Error triggering model retraining: {e}")
            
            alert_handler.trigger_alert(
                "MODEL_RETRAINING_ERROR",
                details={"trigger": "data_drift", "error": str(e)},
                level="ERROR"
            )
            return False
    
    def run_drift_detection_and_retraining(self, current_data: pd.DataFrame) -> Dict:
        """
        Run the complete drift detection and retraining pipeline.
        
        Args:
            current_data: DataFrame containing current data to check for drift
            
        Returns:
            Dict: Results including drift detection and retraining status
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "drift_detected": False,
            "drift_score": 0.0,
            "retraining_triggered": False,
            "retraining_successful": False
        }
        
        # Run drift detection
        drift_report, drift_detected, drift_score = self.detect_drift(current_data)
        
        results["drift_detected"] = drift_detected
        results["drift_score"] = drift_score
        
        # Trigger retraining if drift detected
        if drift_detected:
            should_retrain = self.should_trigger_retraining()
            results["retraining_triggered"] = should_retrain
            
            if should_retrain:
                retraining_success = self.trigger_retraining()
                results["retraining_successful"] = retraining_success
            else:
                logger.info("Retraining not triggered due to cooldown period")
        
        return results

# Function for backward compatibility
def detect_data_drift(current_data: pd.DataFrame, 
                     reference_data: pd.DataFrame = None,
                     column_mapping_override: Dict = None) -> Tuple[Optional[Report], bool]:
    """
    Legacy function for detecting data drift between current data and reference data.
    
    Args:
        current_data: DataFrame containing current data to check for drift
        reference_data: DataFrame containing reference data
        column_mapping_override: Optional override for column mapping
        
    Returns:
        Tuple of (drift_report, drift_detected)
    """
    detector = DriftDetector(reference_data=reference_data)
    report, drift_detected, _ = detector.detect_drift(
        current_data=current_data,
        column_mapping_override=column_mapping_override
    )
    return report, drift_detected

# Example Usage
if __name__ == "__main__":
    logger.info("Running enhanced drift_detection.py example...")
    
    # Create dummy data for demonstration
    # Reference data (e.g., training data or a stable period)
    ref_data = pd.DataFrame({
        config.column_mapping["numerical_features"][0]: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        config.column_mapping["numerical_features"][1]: [10, 20, 30, 40, 50, 50, 40, 30, 20, 10, 11, 12, 13, 14, 15],
        config.column_mapping["categorical_features"][0]: ["A", "B", "A", "C", "B", "A", "C", "A", "B", "C", "A", "B", "A", "C", "B"],
        config.column_mapping["target"]: [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
    })
    
    # Current data with drift
    current_data_drifted = pd.DataFrame({
        config.column_mapping["numerical_features"][0]: [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], # Shifted distribution
        config.column_mapping["numerical_features"][1]: [15, 25, 35, 45, 55, 60, 55, 45, 35, 25, 10, 20, 30, 40, 50], # Shifted distribution
        config.column_mapping["categorical_features"][0]: ["B", "C", "B", "A", "C", "B", "A", "B", "C", "A", "B", "C", "B", "A", "C"], # Changed proportions
        config.column_mapping["target"]: [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1] # Potentially different target distribution
    })
    
    # Current data without drift
    current_data_no_drift = ref_data.copy()
    current_data_no_drift[config.column_mapping["numerical_features"][0]] = current_data_no_drift[config.column_mapping["numerical_features"][0]] + 0.1 # Minor noise, no real drift
    
    # Initialize drift detector
    detector = DriftDetector(reference_data=ref_data)
    
    # Test with drifted data
    logger.info("\n--- Testing with Drifted Data ---")
    results_drifted = detector.run_drift_detection_and_retraining(current_data_drifted)
    logger.info(f"Results with drifted data: {json.dumps(results_drifted, indent=2)}")
    
    # Test with non-drifted data
    logger.info("\n--- Testing with Non-Drifted Data ---")
    results_no_drift = detector.run_drift_detection_and_retraining(current_data_no_drift)
    logger.info(f"Results with non-drifted data: {json.dumps(results_no_drift, indent=2)}")
