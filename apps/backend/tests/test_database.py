import pytest
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from app.database import get_db, Base, engine
from app.models import EnergyData, Alert, Recommendation

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_database_connection(db):
    assert db is not None
    assert db.is_active

def test_energy_data_crud(db):
    # Create
    data = EnergyData(
        timestamp=datetime.now(),
        consumption=100,
        production=80
    )
    db.add(data)
    db.commit()
    db.refresh(data)
    
    assert data.id is not None
    
    # Read
    retrieved_data = db.query(EnergyData).filter_by(id=data.id).first()
    assert retrieved_data is not None
    assert retrieved_data.consumption == 100
    assert retrieved_data.production == 80
    
    # Update
    retrieved_data.consumption = 120
    db.commit()
    db.refresh(retrieved_data)
    
    updated_data = db.query(EnergyData).filter_by(id=data.id).first()
    assert updated_data.consumption == 120
    
    # Delete
    db.delete(updated_data)
    db.commit()
    
    deleted_data = db.query(EnergyData).filter_by(id=data.id).first()
    assert deleted_data is None

def test_alert_crud(db):
    # Create energy data first
    energy_data = EnergyData(
        timestamp=datetime.now(),
        consumption=100,
        production=80
    )
    db.add(energy_data)
    db.commit()
    
    # Create alert
    alert = Alert(
        type="high_consumption",
        message="Energy consumption is above threshold",
        severity="high",
        timestamp=datetime.now(),
        energy_data=energy_data
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    assert alert.id is not None
    
    # Read
    retrieved_alert = db.query(Alert).filter_by(id=alert.id).first()
    assert retrieved_alert is not None
    assert retrieved_alert.type == "high_consumption"
    assert retrieved_alert.severity == "high"
    assert retrieved_alert.energy_data == energy_data
    
    # Update
    retrieved_alert.severity = "medium"
    db.commit()
    db.refresh(retrieved_alert)
    
    updated_alert = db.query(Alert).filter_by(id=alert.id).first()
    assert updated_alert.severity == "medium"
    
    # Delete
    db.delete(updated_alert)
    db.commit()
    
    deleted_alert = db.query(Alert).filter_by(id=alert.id).first()
    assert deleted_alert is None

def test_recommendation_crud(db):
    # Create energy data first
    energy_data = EnergyData(
        timestamp=datetime.now(),
        consumption=100,
        production=80
    )
    db.add(energy_data)
    db.commit()
    
    # Create recommendation
    recommendation = Recommendation(
        type="optimization",
        message="Consider adjusting production schedule",
        impact="high",
        implementation_difficulty="medium",
        energy_data=energy_data
    )
    db.add(recommendation)
    db.commit()
    db.refresh(recommendation)
    
    assert recommendation.id is not None
    
    # Read
    retrieved_recommendation = db.query(Recommendation).filter_by(id=recommendation.id).first()
    assert retrieved_recommendation is not None
    assert retrieved_recommendation.type == "optimization"
    assert retrieved_recommendation.impact == "high"
    assert retrieved_recommendation.energy_data == energy_data
    
    # Update
    retrieved_recommendation.impact = "medium"
    db.commit()
    db.refresh(retrieved_recommendation)
    
    updated_recommendation = db.query(Recommendation).filter_by(id=recommendation.id).first()
    assert updated_recommendation.impact == "medium"
    
    # Delete
    db.delete(updated_recommendation)
    db.commit()
    
    deleted_recommendation = db.query(Recommendation).filter_by(id=recommendation.id).first()
    assert deleted_recommendation is None

def test_energy_data_relationships(db):
    # Create energy data
    energy_data = EnergyData(
        timestamp=datetime.now(),
        consumption=100,
        production=80
    )
    db.add(energy_data)
    db.commit()
    
    # Create alert
    alert = Alert(
        type="high_consumption",
        message="Test alert",
        severity="high",
        timestamp=datetime.now(),
        energy_data=energy_data
    )
    db.add(alert)
    
    # Create recommendation
    recommendation = Recommendation(
        type="optimization",
        message="Test recommendation",
        impact="high",
        implementation_difficulty="medium",
        energy_data=energy_data
    )
    db.add(recommendation)
    
    db.commit()
    
    # Test relationships
    assert len(energy_data.alerts) == 1
    assert len(energy_data.recommendations) == 1
    assert energy_data.alerts[0] == alert
    assert energy_data.recommendations[0] == recommendation
    assert alert.energy_data == energy_data
    assert recommendation.energy_data == energy_data

def test_cascade_delete(db):
    # Create energy data
    energy_data = EnergyData(
        timestamp=datetime.now(),
        consumption=100,
        production=80
    )
    db.add(energy_data)
    db.commit()
    
    # Create alert and recommendation
    alert = Alert(
        type="high_consumption",
        message="Test alert",
        severity="high",
        timestamp=datetime.now(),
        energy_data=energy_data
    )
    recommendation = Recommendation(
        type="optimization",
        message="Test recommendation",
        impact="high",
        implementation_difficulty="medium",
        energy_data=energy_data
    )
    db.add_all([alert, recommendation])
    db.commit()
    
    # Delete energy data
    db.delete(energy_data)
    db.commit()
    
    # Check if related records are deleted
    assert db.query(Alert).filter_by(id=alert.id).first() is None
    assert db.query(Recommendation).filter_by(id=recommendation.id).first() is None

def test_unique_constraints(db):
    # Create energy data
    timestamp = datetime.now()
    data = EnergyData(
        timestamp=timestamp,
        consumption=100,
        production=80
    )
    db.add(data)
    db.commit()
    
    # Try to create another energy data with the same timestamp
    with pytest.raises(IntegrityError):
        duplicate_data = EnergyData(
            timestamp=timestamp,
            consumption=120,
            production=90
        )
        db.add(duplicate_data)
        db.commit()

def test_foreign_key_constraints(db):
    # Try to create alert without energy data
    with pytest.raises(IntegrityError):
        alert = Alert(
            type="high_consumption",
            message="Test alert",
            severity="high",
            timestamp=datetime.now()
        )
        db.add(alert)
        db.commit()
    
    # Try to create recommendation without energy data
    with pytest.raises(IntegrityError):
        recommendation = Recommendation(
            type="optimization",
            message="Test recommendation",
            impact="high",
            implementation_difficulty="medium"
        )
        db.add(recommendation)
        db.commit() 