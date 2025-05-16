# packages/shared/data/feature_store.py
import pandas as pd
import os
import json
import pickle
from datetime import datetime
from packages.shared.utils.logger import get_logger

logger = get_logger(__name__)

class FeatureStoreClient:
    """
    A client to interact with a feature store.
    This is a conceptual implementation and would typically connect to a dedicated feature store service
    (e.g., Feast, Tecton, or a custom database solution).
    For this example, it will use in-memory storage or simple file-based storage.
    """

    def __init__(self, store_path: str = None):
        """
        Initializes the FeatureStoreClient.
        Args:
            store_path (str, optional): Path for file-based storage. If None, uses in-memory.
                                        For a real implementation, this would be connection parameters.
        """
        self.store_path = store_path
        self._in_memory_store = {} # {feature_view_name: {entity_id: {feature_name: value, ..._timestamp: ...}}}

        if self.store_path:
            logger.info(f"File-based feature store initialized at: {self.store_path}")
            # Implement loading from store_path if it exists
            if os.path.exists(self.store_path):
                try:
                    # Create directory structure if it doesn't exist
                    os.makedirs(os.path.dirname(self.store_path), exist_ok=True)

                    # Check if the file exists and load data
                    if os.path.isfile(self.store_path):
                        with open(self.store_path, 'rb') as f:
                            self._in_memory_store = pickle.load(f)
                        logger.info(f"Loaded feature store data from {self.store_path}")
                except Exception as e:
                    logger.error(f"Error loading feature store from {self.store_path}: {e}")
                    # Initialize empty store on error
                    self._in_memory_store = {}
        else:
            logger.info("In-memory feature store initialized.")

    def register_feature_view(self, feature_view_name: str, entity_keys: list[str], features: list[str]):
        """
        Registers a new feature view (conceptual).
        Args:
            feature_view_name (str): Name of the feature view.
            entity_keys (list[str]): List of entity keys for this view.
            features (list[str]): List of feature names in this view.
        """
        # In a real system, this would define the schema in the feature store.
        if feature_view_name not in self._in_memory_store:
            self._in_memory_store[feature_view_name] = {}

            # Store metadata about the feature view
            self._in_memory_store[f"{feature_view_name}_metadata"] = {
                "entity_keys": entity_keys,
                "features": features,
                "created_at": datetime.utcnow().isoformat()
            }

            logger.info(f"Feature view {feature_view_name} registered with entity keys: {entity_keys} and features: {features}")

            # Persist changes if using file storage
            self._persist_store()
        else:
            logger.warning(f"Feature view {feature_view_name} already registered.")

    def push_features(self, feature_view_name: str, entity_id: str, feature_values: dict, event_timestamp: datetime = None):
        """
        Pushes feature values for a given entity to the feature store.
        Args:
            feature_view_name (str): The name of the feature view.
            entity_id (str): The ID of the entity.
            feature_values (dict): A dictionary of feature names to feature values.
            event_timestamp (datetime, optional): The timestamp of the event. Defaults to now().
        """
        if feature_view_name not in self._in_memory_store:
            logger.error(f"Feature view {feature_view_name} not registered. Cannot push features.")
            raise ValueError(f"Feature view {feature_view_name} not registered.")

        timestamp = event_timestamp or datetime.utcnow()
        record = {**feature_values, "_event_timestamp": timestamp}

        if entity_id not in self._in_memory_store[feature_view_name]:
            self._in_memory_store[feature_view_name][entity_id] = []

        # For simplicity, appending; a real store would handle time-series versioning, updates etc.
        self._in_memory_store[feature_view_name][entity_id].append(record)
        logger.info(f"Pushed features for entity {entity_id} to {feature_view_name} at {timestamp}")

        # Persist changes if using file storage
        self._persist_store()

    def _persist_store(self):
        """
        Persists the in-memory store to disk if store_path is set.
        """
        if self.store_path:
            try:
                # Create directory structure if it doesn't exist
                os.makedirs(os.path.dirname(self.store_path), exist_ok=True)

                # Write to file
                with open(self.store_path, 'wb') as f:
                    pickle.dump(self._in_memory_store, f)
                logger.debug(f"Feature store persisted to {self.store_path}")
            except Exception as e:
                logger.error(f"Error persisting feature store to {self.store_path}: {e}")

    def get_online_features(self, feature_view_name: str, entity_id: str, features: list[str] = None) -> dict:
        """
        Retrieves the latest online features for a given entity.
        Args:
            feature_view_name (str): The name of the feature view.
            entity_id (str): The ID of the entity.
            features (list[str], optional): Specific features to retrieve. If None, retrieves all.
        Returns:
            dict: A dictionary of feature names to their latest values, or empty if not found.
        """
        if feature_view_name not in self._in_memory_store or entity_id not in self._in_memory_store[feature_view_name]:
            logger.warning(f"No features found for entity {entity_id} in feature view {feature_view_name}")
            return {}

        # Get the latest record (simplistic: last appended)
        all_records = self._in_memory_store[feature_view_name][entity_id]
        if not all_records:
            return {}

        latest_record = sorted(all_records, key=lambda x: x["_event_timestamp"], reverse=True)[0]

        if features:
            return {f: latest_record.get(f) for f in features if f in latest_record}
        else:
            # Exclude internal timestamp
            return {k: v for k, v in latest_record.items() if k != "_event_timestamp"}

    def get_historical_features(self, feature_view_name: str, entity_df: pd.DataFrame, features: list[str] = None) -> pd.DataFrame:
        """
        Retrieves historical features for a set of entities and timestamps (point-in-time correct).
        This is a complex operation in real feature stores.
        Args:
            feature_view_name (str): The name of the feature view.
            entity_df (pd.DataFrame): DataFrame with entity IDs and timestamps for feature retrieval.
                                      Expected columns: entity_id_column_name, timestamp_column_name.
            features (list[str], optional): Specific features to retrieve. If None, retrieves all.
        Returns:
            pd.DataFrame: DataFrame with entities, timestamps, and their corresponding historical features.
        """
        if feature_view_name not in self._in_memory_store:
            logger.warning(f"Feature view {feature_view_name} not found in store")
            return entity_df.copy()

        # This requires joining entity_df with the feature store data based on entity ID and timestamp (point-in-time join)
        results = []

        for _, row in entity_df.iterrows():
            # Assuming entity_df has columns like 'entity_id' and 'timestamp'
            entity_id = row.get("entity_id")  # Adjust column name as needed
            timestamp = row.get("timestamp")  # Timestamp for point-in-time lookup

            if entity_id and entity_id in self._in_memory_store[feature_view_name]:
                # Get all records for this entity
                entity_records = self._in_memory_store[feature_view_name][entity_id]

                if timestamp:
                    # Filter records that are before or at the specified timestamp
                    valid_records = [
                        r for r in entity_records
                        if r["_event_timestamp"] <= timestamp
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

# Example Usage
if __name__ == "__main__":
    fs_client = FeatureStoreClient()
    fs_client.register_feature_view(
        feature_view_name="user_transaction_features",
        entity_keys=["user_id"],
        features=["avg_transaction_value_7d", "transaction_count_24h"]
    )

    user1_features = {
        "avg_transaction_value_7d": 150.75,
        "transaction_count_24h": 5
    }
    fs_client.push_features("user_transaction_features", "user123", user1_features)

    user2_features = {
        "avg_transaction_value_7d": 88.20,
        "transaction_count_24h": 2
    }
    fs_client.push_features("user_transaction_features", "user456", user2_features, event_timestamp=datetime(2023, 1, 10, 10, 0, 0))
    fs_client.push_features("user_transaction_features", "user456", {**user2_features, "transaction_count_24h": 3}, event_timestamp=datetime(2023, 1, 10, 12, 0, 0))


    retrieved_features_user1 = fs_client.get_online_features("user_transaction_features", "user123")
    logger.info(f"Online features for user123: {retrieved_features_user1}")

    retrieved_features_user2 = fs_client.get_online_features("user_transaction_features", "user456", ["transaction_count_24h"])
    logger.info(f"Online transaction_count_24h for user456: {retrieved_features_user2}")

    # Example historical retrieval
    entity_data = pd.DataFrame({
        "user_id": ["user123", "user456", "user789"],
        "event_time": [datetime.utcnow(), datetime(2023, 1, 10, 11, 0, 0), datetime.utcnow()]
    })
    # Rename columns to match expected for conceptual historical join
    entity_data.rename(columns={"user_id": "entity_id", "event_time": "timestamp"}, inplace=True)

    historical_data = fs_client.get_historical_features("user_transaction_features", entity_data)
    logger.info("Conceptual historical features:")
    logger.info(historical_data)
