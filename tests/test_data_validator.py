"""
Unit tests for the data validation logic using Great Expectations.
"""

import numpy as np
import pandas as pd
import pytest
from fluxora.data.data_validator import validate_raw_data


@pytest.fixture
def valid_data():
    """Create valid test data."""
    return pd.DataFrame(
        {
            "Global_active_power": [1.5, 2.3, 3.1, 0.8, 1.2],
            "Global_reactive_power": [0.2, 0.3, 0.1, 0.4, 0.2],
            "Voltage": [240.1, 238.5, 235.2, 241.3, 239.8],
            "Global_intensity": [6.2, 9.8, 13.2, 3.4, 5.0],
            "Sub_metering_1": [0, 1, 2, 0, 1],
            "Sub_metering_2": [1, 2, 3, 0, 2],
            "Sub_metering_3": [17, 18, 19, 16, 17],
        }
    )


@pytest.fixture
def invalid_data_null():
    """Create test data with null values."""
    return pd.DataFrame(
        {
            "Global_active_power": [1.5, None, 3.1, 0.8, 1.2],
            "Global_reactive_power": [0.2, 0.3, 0.1, 0.4, 0.2],
            "Voltage": [240.1, 238.5, 235.2, 241.3, 239.8],
            "Global_intensity": [6.2, 9.8, 13.2, 3.4, 5.0],
            "Sub_metering_1": [0, 1, 2, 0, 1],
            "Sub_metering_2": [1, 2, 3, 0, 2],
            "Sub_metering_3": [17, 18, 19, 16, 17],
        }
    )


@pytest.fixture
def invalid_data_range():
    """Create test data with values outside valid range."""
    return pd.DataFrame(
        {
            "Global_active_power": [
                1.5,
                25.3,
                3.1,
                0.8,
                1.2,
            ],  # 25.3 is above max of 20
            "Global_reactive_power": [0.2, 0.3, 0.1, 0.4, 0.2],
            "Voltage": [240.1, 238.5, 235.2, 241.3, 239.8],
            "Global_intensity": [6.2, 9.8, 13.2, 3.4, 5.0],
            "Sub_metering_1": [0, 1, 2, 0, 1],
            "Sub_metering_2": [1, 2, 3, 0, 2],
            "Sub_metering_3": [17, 18, 19, 16, 17],
        }
    )


@pytest.fixture
def invalid_data_relationship():
    """Create test data with invalid relationship between columns."""
    return pd.DataFrame(
        {
            "Global_active_power": [1.5, 2.3, 3.1, 0.8, 1.2],
            "Global_reactive_power": [0.2, 0.3, 0.1, 0.4, 0.2],
            "Voltage": [240.1, 238.5, 235.2, 241.3, 239.8],
            "Global_intensity": [260.2, 9.8, 13.2, 3.4, 5.0],  # 260.2 > Voltage (240.1)
            "Sub_metering_1": [0, 1, 2, 0, 1],
            "Sub_metering_2": [1, 2, 3, 0, 2],
            "Sub_metering_3": [17, 18, 19, 16, 17],
        }
    )


def test_validate_raw_data_valid(valid_data):
    """Test validation with valid data."""
    # Should not raise any exceptions
    validate_raw_data(valid_data)


def test_validate_raw_data_null_values(invalid_data_null):
    """Test validation with null values."""
    # Should raise DataValidationError
    with pytest.raises(Exception) as excinfo:
        validate_raw_data(invalid_data_null)
    assert "Data validation failed" in str(excinfo.value)


def test_validate_raw_data_out_of_range(invalid_data_range):
    """Test validation with values outside valid range."""
    # Should raise DataValidationError
    with pytest.raises(Exception) as excinfo:
        validate_raw_data(invalid_data_range)
    assert "Data validation failed" in str(excinfo.value)


def test_validate_raw_data_invalid_relationship(invalid_data_relationship):
    """Test validation with invalid relationship between columns."""
    # Should raise DataValidationError
    with pytest.raises(Exception) as excinfo:
        validate_raw_data(invalid_data_relationship)
    assert "Data validation failed" in str(excinfo.value)


def test_validate_raw_data_empty():
    """Test validation with empty DataFrame."""
    # Should raise DataValidationError
    with pytest.raises(Exception) as excinfo:
        validate_raw_data(pd.DataFrame())
    assert "Data validation failed" in str(excinfo.value)


def test_validate_raw_data_missing_columns():
    """Test validation with missing required columns."""
    # Create data missing Global_active_power
    missing_columns_data = pd.DataFrame(
        {
            "Global_reactive_power": [0.2, 0.3, 0.1, 0.4, 0.2],
            "Voltage": [240.1, 238.5, 235.2, 241.3, 239.8],
            "Global_intensity": [6.2, 9.8, 13.2, 3.4, 5.0],
        }
    )

    # Should raise DataValidationError or KeyError
    with pytest.raises(Exception):
        validate_raw_data(missing_columns_data)


def test_validate_raw_data_edge_cases():
    """Test validation with edge case values."""
    edge_case_data = pd.DataFrame(
        {
            # Exactly at min and max boundaries
            "Global_active_power": [0.0, 20.0, 10.0, 5.0, 15.0],
            "Global_reactive_power": [0.2, 0.3, 0.1, 0.4, 0.2],
            # Voltage exactly equal to Global_intensity (edge case for relationship)
            "Voltage": [240.1, 238.5, 235.2, 241.3, 100.0],
            "Global_intensity": [6.2, 9.8, 13.2, 3.4, 100.0],
            "Sub_metering_1": [0, 1, 2, 0, 1],
            "Sub_metering_2": [1, 2, 3, 0, 2],
            "Sub_metering_3": [17, 18, 19, 16, 17],
        }
    )

    # Should raise DataValidationError for the equal values in last row
    with pytest.raises(Exception) as excinfo:
        validate_raw_data(edge_case_data)
    assert "Data validation failed" in str(excinfo.value)
