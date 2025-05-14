import pytest
from datetime import datetime
from app.models import EnergyData, Alert, Recommendation
from sqlalchemy.exc import IntegrityError

def test_energy_data_creation():
    timestamp = datetime.now()
    data = EnergyData(
        timestamp=timestamp,
        consumption=100.5,
        production=80.3
    )
    
    assert data.timestamp == timestamp
    assert data.consumption == 100.5
    assert data.production == 80.3
    assert data.net_energy == 20.2

def test_energy_data_validation():
    with pytest.raises(ValueError):
        EnergyData(
            timestamp=datetime.now(),
            consumption=-100,
            production=80
        )
    
    with pytest.raises(ValueError):
        EnergyData(
            timestamp=datetime.now(),
            consumption=100,
            production=-80
        )

def test_energy_data_required_fields():
    with pytest.raises(IntegrityError):
        EnergyData(
            consumption=100,
            production=80
        )

def test_alert_creation():
    timestamp = datetime.now()
    alert = Alert(
        type="high_consumption",
        message="Energy consumption is above threshold",
        severity="high",
        timestamp=timestamp
    )
    
    assert alert.type == "high_consumption"
    assert alert.message == "Energy consumption is above threshold"
    assert alert.severity == "high"
    assert alert.timestamp == timestamp

def test_alert_validation():
    with pytest.raises(ValueError):
        Alert(
            type="invalid_type",
            message="Test message",
            severity="high",
            timestamp=datetime.now()
        )
    
    with pytest.raises(ValueError):
        Alert(
            type="high_consumption",
            message="Test message",
            severity="invalid_severity",
            timestamp=datetime.now()
        )

def test_alert_required_fields():
    with pytest.raises(IntegrityError):
        Alert(
            type="high_consumption",
            severity="high"
        )

def test_recommendation_creation():
    recommendation = Recommendation(
        type="optimization",
        message="Consider adjusting production schedule",
        impact="high",
        implementation_difficulty="medium"
    )
    
    assert recommendation.type == "optimization"
    assert recommendation.message == "Consider adjusting production schedule"
    assert recommendation.impact == "high"
    assert recommendation.implementation_difficulty == "medium"

def test_recommendation_validation():
    with pytest.raises(ValueError):
        Recommendation(
            type="invalid_type",
            message="Test message",
            impact="high",
            implementation_difficulty="medium"
        )
    
    with pytest.raises(ValueError):
        Recommendation(
            type="optimization",
            message="Test message",
            impact="invalid_impact",
            implementation_difficulty="medium"
        )
    
    with pytest.raises(ValueError):
        Recommendation(
            type="optimization",
            message="Test message",
            impact="high",
            implementation_difficulty="invalid_difficulty"
        )

def test_recommendation_required_fields():
    with pytest.raises(IntegrityError):
        Recommendation(
            type="optimization",
            impact="high"
        )

def test_energy_data_relationships(db):
    timestamp = datetime.now()
    data = EnergyData(
        timestamp=timestamp,
        consumption=100,
        production=80
    )
    db.add(data)
    
    alert = Alert(
        type="high_consumption",
        message="Test alert",
        severity="high",
        timestamp=timestamp,
        energy_data=data
    )
    db.add(alert)
    
    recommendation = Recommendation(
        type="optimization",
        message="Test recommendation",
        impact="high",
        implementation_difficulty="medium",
        energy_data=data
    )
    db.add(recommendation)
    
    db.commit()
    
    assert data.alerts[0] == alert
    assert data.recommendations[0] == recommendation
    assert alert.energy_data == data
    assert recommendation.energy_data == data 