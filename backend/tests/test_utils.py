import pytest
from datetime import datetime, timedelta
from app.utils import (
    calculate_net_energy,
    calculate_energy_efficiency,
    format_timestamp,
    validate_date_range,
    calculate_statistics,
    calculate_trends,
    calculate_anomalies,
    calculate_forecast_accuracy
)

def test_calculate_net_energy():
    consumption = 100
    production = 80
    net_energy = calculate_net_energy(consumption, production)
    assert net_energy == 20

def test_calculate_net_energy_negative():
    consumption = 80
    production = 100
    net_energy = calculate_net_energy(consumption, production)
    assert net_energy == -20

def test_calculate_energy_efficiency():
    consumption = 100
    production = 80
    efficiency = calculate_energy_efficiency(consumption, production)
    assert efficiency == 0.8

def test_calculate_energy_efficiency_zero_consumption():
    with pytest.raises(ValueError):
        calculate_energy_efficiency(0, 80)

def test_format_timestamp():
    timestamp = datetime(2024, 1, 1, 12, 0, 0)
    formatted = format_timestamp(timestamp)
    assert formatted == "2024-01-01T12:00:00"

def test_format_timestamp_with_timezone():
    timestamp = datetime(2024, 1, 1, 12, 0, 0)
    formatted = format_timestamp(timestamp, include_timezone=True)
    assert "Z" in formatted or "+" in formatted

def test_validate_date_range():
    start_date = datetime.now()
    end_date = start_date + timedelta(days=1)
    assert validate_date_range(start_date, end_date) is True

def test_validate_date_range_invalid():
    start_date = datetime.now()
    end_date = start_date - timedelta(days=1)
    with pytest.raises(ValueError):
        validate_date_range(start_date, end_date)

def test_validate_date_range_same_date():
    date = datetime.now()
    assert validate_date_range(date, date) is True

def test_calculate_statistics():
    data = [100, 120, 110, 130, 115]
    stats = calculate_statistics(data)
    assert "mean" in stats
    assert "median" in stats
    assert "std_dev" in stats
    assert "min" in stats
    assert "max" in stats
    assert stats["mean"] == 115
    assert stats["median"] == 115
    assert stats["min"] == 100
    assert stats["max"] == 130

def test_calculate_statistics_empty():
    with pytest.raises(ValueError):
        calculate_statistics([])

def test_calculate_trends():
    data = [100, 120, 110, 130, 115]
    trends = calculate_trends(data)
    assert "slope" in trends
    assert "intercept" in trends
    assert "r_squared" in trends
    assert isinstance(trends["slope"], float)
    assert isinstance(trends["intercept"], float)
    assert isinstance(trends["r_squared"], float)

def test_calculate_trends_insufficient_data():
    with pytest.raises(ValueError):
        calculate_trends([100])

def test_calculate_anomalies():
    data = [100, 120, 110, 130, 115, 200]  # 200 is an anomaly
    anomalies = calculate_anomalies(data)
    assert len(anomalies) == 1
    assert anomalies[0] == 200

def test_calculate_anomalies_no_anomalies():
    data = [100, 120, 110, 130, 115]
    anomalies = calculate_anomalies(data)
    assert len(anomalies) == 0

def test_calculate_anomalies_empty():
    with pytest.raises(ValueError):
        calculate_anomalies([])

def test_calculate_forecast_accuracy():
    actual = [100, 120, 110, 130, 115]
    forecast = [105, 115, 115, 125, 120]
    accuracy = calculate_forecast_accuracy(actual, forecast)
    assert "mae" in accuracy
    assert "rmse" in accuracy
    assert "mape" in accuracy
    assert isinstance(accuracy["mae"], float)
    assert isinstance(accuracy["rmse"], float)
    assert isinstance(accuracy["mape"], float)

def test_calculate_forecast_accuracy_mismatched_lengths():
    actual = [100, 120, 110]
    forecast = [105, 115]
    with pytest.raises(ValueError):
        calculate_forecast_accuracy(actual, forecast)

def test_calculate_forecast_accuracy_empty():
    with pytest.raises(ValueError):
        calculate_forecast_accuracy([], [])

def test_calculate_forecast_accuracy_zero_actual():
    actual = [0, 120, 110]
    forecast = [5, 115, 115]
    accuracy = calculate_forecast_accuracy(actual, forecast)
    assert "mae" in accuracy
    assert "rmse" in accuracy
    assert "mape" in accuracy
