import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from app.main import app
from app.models import EnergyData
from app.database import get_db, Base, engine

client = TestClient(app)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def sample_data(db):
    # Create sample energy data
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

def test_get_energy_data(db, sample_data):
    response = client.get("/api/energy/data")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 24
    assert all("timestamp" in item for item in data)
    assert all("consumption" in item for item in data)
    assert all("production" in item for item in data)

def test_get_energy_data_with_date_range(db, sample_data):
    start_date = (datetime.now() - timedelta(hours=12)).isoformat()
    end_date = datetime.now().isoformat()
    
    response = client.get(f"/api/energy/data?start_date={start_date}&end_date={end_date}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 12

def test_get_energy_data_invalid_date_range():
    response = client.get("/api/energy/data?start_date=invalid&end_date=invalid")
    assert response.status_code == 422

def test_get_energy_summary(db, sample_data):
    response = client.get("/api/energy/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_consumption" in data
    assert "total_production" in data
    assert "net_energy" in data

def test_get_energy_summary_with_date_range(db, sample_data):
    start_date = (datetime.now() - timedelta(hours=12)).isoformat()
    end_date = datetime.now().isoformat()
    
    response = client.get(f"/api/energy/summary?start_date={start_date}&end_date={end_date}")
    assert response.status_code == 200
    data = response.json()
    assert "total_consumption" in data
    assert "total_production" in data
    assert "net_energy" in data

def test_get_energy_summary_invalid_date_range():
    response = client.get("/api/energy/summary?start_date=invalid&end_date=invalid")
    assert response.status_code == 422

def test_post_energy_data(db):
    data = {
        "timestamp": datetime.now().isoformat(),
        "consumption": 100,
        "production": 80
    }
    response = client.post("/api/energy/data", json=data)
    assert response.status_code == 201
    assert response.json()["consumption"] == 100
    assert response.json()["production"] == 80

def test_post_energy_data_invalid_data():
    data = {
        "timestamp": "invalid",
        "consumption": "invalid",
        "production": "invalid"
    }
    response = client.post("/api/energy/data", json=data)
    assert response.status_code == 422

def test_get_energy_forecast(db, sample_data):
    response = client.get("/api/energy/forecast")
    assert response.status_code == 200
    data = response.json()
    assert "forecast" in data
    assert "confidence_interval" in data

def test_get_energy_forecast_with_horizon(db, sample_data):
    response = client.get("/api/energy/forecast?horizon=48")
    assert response.status_code == 200
    data = response.json()
    assert len(data["forecast"]) == 48

def test_get_energy_forecast_invalid_horizon():
    response = client.get("/api/energy/forecast?horizon=invalid")
    assert response.status_code == 422

def test_get_energy_alerts(db, sample_data):
    response = client.get("/api/energy/alerts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all("type" in alert for alert in data)
    assert all("message" in alert for alert in data)
    assert all("timestamp" in alert for alert in data)

def test_get_energy_alerts_with_severity(db, sample_data):
    response = client.get("/api/energy/alerts?severity=high")
    assert response.status_code == 200
    data = response.json()
    assert all(alert["severity"] == "high" for alert in data)

def test_get_energy_alerts_invalid_severity():
    response = client.get("/api/energy/alerts?severity=invalid")
    assert response.status_code == 422

def test_get_energy_recommendations(db, sample_data):
    response = client.get("/api/energy/recommendations")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all("type" in rec for rec in data)
    assert all("message" in rec for rec in data)
    assert all("impact" in rec for rec in data)

def test_get_energy_recommendations_with_type(db, sample_data):
    response = client.get("/api/energy/recommendations?type=optimization")
    assert response.status_code == 200
    data = response.json()
    assert all(rec["type"] == "optimization" for rec in data)

def test_get_energy_recommendations_invalid_type():
    response = client.get("/api/energy/recommendations?type=invalid")
    assert response.status_code == 422
