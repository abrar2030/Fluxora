import os
from typing import Any, Dict


def get_config() -> Dict[str, Any]:
    """
    Simple configuration function to replace hydra dependency

    Returns:
        Dict: Configuration dictionary
    """
    config = {
        "version": "1.0.0",
        "model_version": "0.1.0-test",
        "model": {
            "type": "xgboost",
            "params": {"max_depth": 6, "eta": 0.3, "objective": "reg:squarederror"},
        },
        "api": {"host": "0.0.0.0", "port": 8000},
        "feature_store": {"path": "./config/feature_store"},
        "monitoring": {"enabled": True, "drift_threshold": 0.25},
    }
    return config


def save_config(config: Dict[str, Any], path: str) -> Any:
    """
    Save configuration to file

    Args:
        config: Configuration dictionary
        path: Path to save the configuration
    """
    import json

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(config, f, indent=2)
