import pytest
from datetime import datetime, timedelta
from app.services import EnergyService, ForecastService, AlertService, RecommendationService
from app.models import EnergyData, Alert, Recommendation

@pytest.fixture
def energy_service(db):
    return EnergyService(db)

@pytest.fixture
def forecast_service(db):
    return ForecastService(db)

@pytest.fixture
def alert_service(db):
    return AlertService(db)

@pytest.fixture
def recommendation_service(db):
    return RecommendationService(db)

@pytest.fixture
def sample_energy_data(db):
    data = [
        EnergyData(
            timestamp=datetime.now() - timedelta(hours=i),
            consumption=100 + i,
            production=80 + i
        )
        for i in range(24)
    ]
    db.add_all(data)
    db.commit()
    return data

def test_get_energy_data(energy_service, sample_energy_data):
    data = energy_service.get_energy_data()
    assert len(data) == 24
    assert all(isinstance(item, EnergyData) for item in data)

def test_get_energy_data_with_date_range(energy_service, sample_energy_data):
    start_date = datetime.now() - timedelta(hours=12)
    end_date = datetime.now()
    
    data = energy_service.get_energy_data(start_date, end_date)
    assert len(data) == 12
    assert all(start_date <= item.timestamp <= end_date for item in data)

def test_get_energy_summary(energy_service, sample_energy_data):
    summary = energy_service.get_energy_summary()
    assert "total_consumption" in summary
    assert "total_production" in summary
    assert "net_energy" in summary
    assert summary["total_consumption"] > 0
    assert summary["total_production"] > 0

def test_create_energy_data(energy_service):
    data = {
        "timestamp": datetime.now(),
        "consumption": 100,
        "production": 80
    }
    
    created_data = energy_service.create_energy_data(data)
    assert created_data.consumption == 100
    assert created_data.production == 80
    assert created_data.net_energy == 20

def test_get_energy_forecast(forecast_service, sample_energy_data):
    forecast = forecast_service.get_forecast()
    assert "forecast" in forecast
    assert "confidence_interval" in forecast
    assert len(forecast["forecast"]) > 0
    assert len(forecast["confidence_interval"]) > 0

def test_get_energy_forecast_with_horizon(forecast_service, sample_energy_data):
    horizon = 48
    forecast = forecast_service.get_forecast(horizon=horizon)
    assert len(forecast["forecast"]) == horizon
    assert len(forecast["confidence_interval"]) == horizon

def test_create_alert(alert_service, sample_energy_data):
    alert_data = {
        "type": "high_consumption",
        "message": "Energy consumption is above threshold",
        "severity": "high",
        "timestamp": datetime.now(),
        "energy_data": sample_energy_data[0]
    }
    
    alert = alert_service.create_alert(alert_data)
    assert alert.type == "high_consumption"
    assert alert.severity == "high"
    assert alert.energy_data == sample_energy_data[0]

def test_get_alerts(alert_service, sample_energy_data):
    # Create some alerts
    for data in sample_energy_data[:3]:
        alert_service.create_alert({
            "type": "high_consumption",
            "message": "Test alert",
            "severity": "high",
            "timestamp": data.timestamp,
            "energy_data": data
        })
    
    alerts = alert_service.get_alerts()
    assert len(alerts) == 3
    assert all(isinstance(alert, Alert) for alert in alerts)

def test_get_alerts_with_severity(alert_service, sample_energy_data):
    # Create alerts with different severities
    alert_service.create_alert({
        "type": "high_consumption",
        "message": "High severity alert",
        "severity": "high",
        "timestamp": datetime.now(),
        "energy_data": sample_energy_data[0]
    })
    
    alert_service.create_alert({
        "type": "low_production",
        "message": "Low severity alert",
        "severity": "low",
        "timestamp": datetime.now(),
        "energy_data": sample_energy_data[1]
    })
    
    high_alerts = alert_service.get_alerts(severity="high")
    assert len(high_alerts) == 1
    assert all(alert.severity == "high" for alert in high_alerts)

def test_create_recommendation(recommendation_service, sample_energy_data):
    recommendation_data = {
        "type": "optimization",
        "message": "Consider adjusting production schedule",
        "impact": "high",
        "implementation_difficulty": "medium",
        "energy_data": sample_energy_data[0]
    }
    
    recommendation = recommendation_service.create_recommendation(recommendation_data)
    assert recommendation.type == "optimization"
    assert recommendation.impact == "high"
    assert recommendation.implementation_difficulty == "medium"
    assert recommendation.energy_data == sample_energy_data[0]

def test_get_recommendations(recommendation_service, sample_energy_data):
    # Create some recommendations
    for data in sample_energy_data[:3]:
        recommendation_service.create_recommendation({
            "type": "optimization",
            "message": "Test recommendation",
            "impact": "high",
            "implementation_difficulty": "medium",
            "energy_data": data
        })
    
    recommendations = recommendation_service.get_recommendations()
    assert len(recommendations) == 3
    assert all(isinstance(rec, Recommendation) for rec in recommendations)

def test_get_recommendations_with_type(recommendation_service, sample_energy_data):
    # Create recommendations with different types
    recommendation_service.create_recommendation({
        "type": "optimization",
        "message": "Optimization recommendation",
        "impact": "high",
        "implementation_difficulty": "medium",
        "energy_data": sample_energy_data[0]
    })
    
    recommendation_service.create_recommendation({
        "type": "maintenance",
        "message": "Maintenance recommendation",
        "impact": "medium",
        "implementation_difficulty": "low",
        "energy_data": sample_energy_data[1]
    })
    
    optimization_recs = recommendation_service.get_recommendations(type="optimization")
    assert len(optimization_recs) == 1
    assert all(rec.type == "optimization" for rec in optimization_recs) 