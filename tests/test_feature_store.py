"""
Unit tests for the feature store implementation.
"""

from datetime import datetime, timedelta

import pandas as pd
import pytest
from fluxora.data.feature_store import FeatureStoreClient


@pytest.fixture
def feature_store():
    """Create a clean feature store for testing."""
    fs = FeatureStoreClient()
    # Clean up any existing feature views from previous tests
    for view in fs.list_feature_views():
        fs.delete_feature_view(view)
    return fs


@pytest.fixture
def sample_feature_view(feature_store):
    """Create a sample feature view with test data."""
    feature_store.register_feature_view(
        feature_view_name="test_features",
        entity_keys=["user_id"],
        features=["avg_transaction_value", "transaction_count"],
    )
    return feature_store


@pytest.fixture
def sample_features():
    """Sample feature data for testing."""
    return {"avg_transaction_value": 150.75, "transaction_count": 5}


def test_register_feature_view(feature_store):
    """Test registering a new feature view."""
    # Register a new feature view
    feature_store.register_feature_view(
        feature_view_name="energy_features",
        entity_keys=["device_id"],
        features=["power_consumption", "voltage", "current"],
    )

    # Verify feature view was registered
    feature_views = feature_store.list_feature_views()
    assert "energy_features" in feature_views

    # Verify metadata
    metadata = feature_store.get_feature_view_metadata("energy_features")
    assert metadata["entity_keys"] == ["device_id"]
    assert set(metadata["features"]) == {"power_consumption", "voltage", "current"}


def test_push_and_get_online_features(sample_feature_view, sample_features):
    """Test pushing features and retrieving them."""
    # Push features for a test entity
    sample_feature_view.push_features("test_features", "user123", sample_features)

    # Retrieve features
    retrieved_features = sample_feature_view.get_online_features(
        "test_features", "user123"
    )

    # Verify retrieved features match pushed features
    assert (
        retrieved_features["avg_transaction_value"]
        == sample_features["avg_transaction_value"]
    )
    assert (
        retrieved_features["transaction_count"] == sample_features["transaction_count"]
    )


def test_push_features_with_timestamp(sample_feature_view, sample_features):
    """Test pushing features with timestamps."""
    # Push features with different timestamps
    timestamp1 = datetime.now() - timedelta(hours=2)
    timestamp2 = datetime.now() - timedelta(hours=1)

    sample_feature_view.push_features(
        "test_features",
        "user456",
        {"avg_transaction_value": 100.0, "transaction_count": 3},
        event_timestamp=timestamp1,
    )

    sample_feature_view.push_features(
        "test_features",
        "user456",
        {"avg_transaction_value": 200.0, "transaction_count": 7},
        event_timestamp=timestamp2,
    )

    # Retrieve latest features (should be from timestamp2)
    retrieved_features = sample_feature_view.get_online_features(
        "test_features", "user456"
    )

    assert retrieved_features["avg_transaction_value"] == 200.0
    assert retrieved_features["transaction_count"] == 7


def test_get_historical_features(sample_feature_view):
    """Test retrieving historical features."""
    # Push features with different timestamps
    timestamp1 = datetime(2023, 1, 10, 10, 0, 0)
    timestamp2 = datetime(2023, 1, 10, 12, 0, 0)

    sample_feature_view.push_features(
        "test_features",
        "user789",
        {"avg_transaction_value": 50.0, "transaction_count": 1},
        event_timestamp=timestamp1,
    )

    sample_feature_view.push_features(
        "test_features",
        "user789",
        {"avg_transaction_value": 75.0, "transaction_count": 2},
        event_timestamp=timestamp2,
    )

    # Create entity data with timestamps
    entity_data = pd.DataFrame(
        {
            "entity_id": ["user789", "user789"],
            "timestamp": [
                datetime(2023, 1, 10, 11, 0, 0),
                datetime(2023, 1, 10, 13, 0, 0),
            ],
        }
    )

    # Get historical features
    historical_data = sample_feature_view.get_historical_features(
        "test_features", entity_data
    )

    # First row should have features from timestamp1 (as it's before the query timestamp)
    assert historical_data.iloc[0]["avg_transaction_value"] == 50.0
    assert historical_data.iloc[0]["transaction_count"] == 1

    # Second row should have features from timestamp2 (as it's the latest before the query timestamp)
    assert historical_data.iloc[1]["avg_transaction_value"] == 75.0
    assert historical_data.iloc[1]["transaction_count"] == 2


def test_get_specific_features(sample_feature_view, sample_features):
    """Test retrieving specific features."""
    # Push features
    sample_feature_view.push_features("test_features", "user123", sample_features)

    # Retrieve only transaction_count
    retrieved_features = sample_feature_view.get_online_features(
        "test_features", "user123", ["transaction_count"]
    )

    # Verify only requested feature is returned
    assert "transaction_count" in retrieved_features
    assert "avg_transaction_value" not in retrieved_features
    assert (
        retrieved_features["transaction_count"] == sample_features["transaction_count"]
    )


def test_entity_not_found(sample_feature_view):
    """Test behavior when entity is not found."""
    # Try to retrieve features for non-existent entity
    retrieved_features = sample_feature_view.get_online_features(
        "test_features", "nonexistent_user"
    )

    # Should return empty dict
    assert retrieved_features == {}


def test_feature_view_not_found(feature_store):
    """Test behavior when feature view is not found."""
    # Try to retrieve features for non-existent feature view
    with pytest.raises(KeyError):
        feature_store.get_online_features("nonexistent_view", "user123")


def test_delete_feature_view(sample_feature_view, sample_features):
    """Test deleting a feature view."""
    # Push some features
    sample_feature_view.push_features("test_features", "user123", sample_features)

    # Delete the feature view
    result = sample_feature_view.delete_feature_view("test_features")
    assert result is True

    # Verify feature view is no longer listed
    feature_views = sample_feature_view.list_feature_views()
    assert "test_features" not in feature_views

    # Trying to delete again should return False
    result = sample_feature_view.delete_feature_view("test_features")
    assert result is False


def test_multiple_feature_views(feature_store):
    """Test managing multiple feature views."""
    # Register two feature views
    feature_store.register_feature_view(
        feature_view_name="user_features",
        entity_keys=["user_id"],
        features=["login_count", "session_duration"],
    )

    feature_store.register_feature_view(
        feature_view_name="device_features",
        entity_keys=["device_id"],
        features=["battery_level", "signal_strength"],
    )

    # Push features to both
    feature_store.push_features(
        "user_features", "user123", {"login_count": 10, "session_duration": 3600}
    )

    feature_store.push_features(
        "device_features", "device456", {"battery_level": 0.75, "signal_strength": 0.85}
    )

    # Verify both feature views exist
    feature_views = feature_store.list_feature_views()
    assert "user_features" in feature_views
    assert "device_features" in feature_views

    # Verify features can be retrieved from both
    user_features = feature_store.get_online_features("user_features", "user123")
    device_features = feature_store.get_online_features("device_features", "device456")

    assert user_features["login_count"] == 10
    assert device_features["battery_level"] == 0.75
