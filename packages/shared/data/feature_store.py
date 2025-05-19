"""
Feature store client implementation for Fluxora.
"""
import os
import json
import logging
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeatureStoreClient:
    """
    In-memory feature store client for storing and retrieving features.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the feature store client.
        
        Args:
            storage_path: Optional path to persist feature store data
        """
        self._in_memory_store = {}
        self._storage_path = storage_path
        logger.info("In-memory feature store initialized.")
        
        # Load from storage if path provided
        if storage_path and os.path.exists(storage_path):
            self._load_store()
    
    def _persist_store(self) -> None:
        """Persist the store to disk if storage path is provided."""
        if self._storage_path:
            os.makedirs(os.path.dirname(self._storage_path), exist_ok=True)
            with open(self._storage_path, 'w') as f:
                json.dump(self._in_memory_store, f)
    
    def _load_store(self) -> None:
        """Load the store from disk if storage path is provided."""
        if self._storage_path and os.path.exists(self._storage_path):
            with open(self._storage_path, 'r') as f:
                self._in_memory_store = json.load(f)
    
    def register_feature_view(self, 
                             feature_view_name: str, 
                             entity_keys: List[str],
                             features: List[str]) -> None:
        """
        Register a new feature view.
        
        Args:
            feature_view_name: Name of the feature view
            entity_keys: List of entity key names
            features: List of feature names
        """
        if feature_view_name not in self._in_memory_store:
            self._in_memory_store[feature_view_name] = {}
            
            # Store metadata
            metadata_key = f"{feature_view_name}_metadata"
            self._in_memory_store[metadata_key] = {
                "entity_keys": entity_keys,
                "features": features,
                "created_at": datetime.now().isoformat()
            }
            
            # Persist changes
            self._persist_store()
            logger.info(f"Feature view {feature_view_name} registered successfully.")
        else:
            logger.warning(f"Feature view {feature_view_name} already exists.")
    
    def push_features(self, 
                     feature_view_name: str, 
                     entity_id: str, 
                     features: Dict[str, Any],
                     event_timestamp: Optional[datetime] = None) -> None:
        """
        Push features for an entity to a feature view.
        
        Args:
            feature_view_name: Name of the feature view
            entity_id: Entity identifier
            features: Dictionary of feature name to feature value
            event_timestamp: Optional timestamp for the feature values
        """
        if feature_view_name not in self._in_memory_store:
            logger.warning(f"Feature view {feature_view_name} not found. Creating it.")
            self._in_memory_store[feature_view_name] = {}
        
        if entity_id not in self._in_memory_store[feature_view_name]:
            self._in_memory_store[feature_view_name][entity_id] = []
        
        # Add timestamp if not provided
        feature_record = features.copy()
        feature_record["_event_timestamp"] = event_timestamp.isoformat() if event_timestamp else datetime.now().isoformat()
        
        # Add to entity's feature history
        self._in_memory_store[feature_view_name][entity_id].append(feature_record)
        
        # Persist changes
        self._persist_store()
        logger.debug(f"Features pushed for entity {entity_id} in view {feature_view_name}.")
    
    def get_online_features(self, 
                           feature_view_name: str, 
                           entity_id: str,
                           features: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get the latest feature values for an entity.
        
        Args:
            feature_view_name: Name of the feature view
            entity_id: Entity identifier
            features: Optional list of specific features to retrieve
            
        Returns:
            Dictionary of feature name to feature value
        """
        if feature_view_name not in self._in_memory_store:
            # Modified to raise KeyError instead of just logging a warning
            raise KeyError(f"Feature view {feature_view_name} not found")
        
        if entity_id not in self._in_memory_store[feature_view_name]:
            logger.warning(f"No features found for entity {entity_id} in feature view {feature_view_name}")
            return {}
        
        # Get the latest feature record
        feature_records = self._in_memory_store[feature_view_name][entity_id]
        if not feature_records:
            return {}
        
        # Sort by timestamp and get the latest
        sorted_records = sorted(feature_records, key=lambda x: x["_event_timestamp"], reverse=True)
        latest_record = sorted_records[0]
        
        # Filter to requested features if specified
        if features:
            return {f: latest_record.get(f) for f in features if f in latest_record}
        else:
            # Return all features except internal metadata
            return {k: v for k, v in latest_record.items() if not k.startswith("_")}
    
    def get_historical_features(self, 
                               feature_view_name: str, 
                               entity_data: pd.DataFrame,
                               features: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Get historical feature values for entities at specific timestamps.
        
        Args:
            feature_view_name: Name of the feature view
            entity_data: DataFrame with entity_id and timestamp columns
            features: Optional list of specific features to retrieve
            
        Returns:
            DataFrame with entity data and joined feature values
        """
        if feature_view_name not in self._in_memory_store:
            raise ValueError(f"Feature view {feature_view_name} not found")
        
        results = []
        
        for _, row in entity_data.iterrows():
            entity_id = row.get("entity_id")
            timestamp = row.get("timestamp")
            
            if entity_id in self._in_memory_store[feature_view_name]:
                feature_records = self._in_memory_store[feature_view_name][entity_id]
                
                if timestamp:
                    # Find records before or at the timestamp
                    valid_records = [
                        r for r in feature_records 
                        if datetime.fromisoformat(r["_event_timestamp"]) <= timestamp
                    ]
                    if valid_records:
                        # Get the latest record before or at the timestamp
                        latest_valid = sorted(valid_records, key=lambda x: x["_event_timestamp"], reverse=True)[0]
                        # Extract requested features
                        if features:
                            feature_values = {f: latest_valid.get(f) for f in features if f in latest_valid}
                        else:
                            feature_values = {k: v for k, v in latest_valid.items() if k != "_event_timestamp"}
                        results.append({**row.to_dict(), **feature_values})
                    else:
                        # No valid records found before the timestamp
                        results.append(row.to_dict())
                else:
                    # No timestamp provided, get latest features
                    online_feats = self.get_online_features(feature_view_name, entity_id, features)
                    results.append({**row.to_dict(), **online_feats})
            else:
                # Entity not found in store
                results.append(row.to_dict())
        return pd.DataFrame(results)
    
    def delete_feature_view(self, feature_view_name: str) -> bool:
        """
        Deletes a feature view and all its data.
        Args:
            feature_view_name (str): The name of the feature view to delete.
        Returns:
            bool: True if successful, False otherwise.
        """
        if feature_view_name not in self._in_memory_store:
            logger.warning(f"Feature view {feature_view_name} not found, nothing to delete.")
            return False
        try:
            # Remove the feature view and its metadata
            del self._in_memory_store[feature_view_name]
            # Also remove metadata if it exists
            metadata_key = f"{feature_view_name}_metadata"
            if metadata_key in self._in_memory_store:
                del self._in_memory_store[metadata_key]
            logger.info(f"Feature view {feature_view_name} deleted successfully.")
            # Persist changes if using file storage
            self._persist_store()
            return True
        except Exception as e:
            logger.error(f"Error deleting feature view {feature_view_name}: {e}")
            return False
    
    def list_feature_views(self) -> list[str]:
        """
        Lists all registered feature views.
        Returns:
            list[str]: List of feature view names.
        """
        # Filter out metadata entries
        return [k for k in self._in_memory_store.keys() if not k.endswith("_metadata")]
    
    def get_feature_view_metadata(self, feature_view_name: str) -> dict:
        """
        Gets metadata for a feature view.
        Args:
            feature_view_name (str): The name of the feature view.
        Returns:
            dict: Metadata for the feature view, or empty dict if not found.
        """
        metadata_key = f"{feature_view_name}_metadata"
        return self._in_memory_store.get(metadata_key, {})
