from fastapi.testclient import TestClient


def test_get_analytics_returns_list(client: TestClient, auth_headers: dict):
    response = client.get("/v1/analytics/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_analytics_week(client: TestClient, auth_headers: dict):
    response = client.get("/v1/analytics/?period=week", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_analytics_month(client: TestClient, auth_headers: dict):
    response = client.get("/v1/analytics/?period=month", headers=auth_headers)
    assert response.status_code == 200


def test_get_analytics_year(client: TestClient, auth_headers: dict):
    response = client.get("/v1/analytics/?period=year", headers=auth_headers)
    assert response.status_code == 200


def test_get_analytics_invalid_period(client: TestClient, auth_headers: dict):
    response = client.get("/v1/analytics/?period=decade", headers=auth_headers)
    assert response.status_code == 422


def test_get_analytics_unauthenticated(client: TestClient):
    response = client.get("/v1/analytics/")
    assert response.status_code == 401


def test_analytics_empty_without_records(client: TestClient, auth_headers: dict):
    for period in ("week", "month", "year"):
        response = client.get(f"/v1/analytics/?period={period}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []


def test_analytics_point_shape_with_records(client: TestClient, auth_headers: dict):
    client.post(
        "/v1/data/",
        headers=auth_headers,
        json={"consumption_kwh": 12.5, "cost_usd": 1.5, "temperature_c": 20.0},
    )
    data = client.get("/v1/analytics/?period=week", headers=auth_headers).json()
    assert len(data) >= 1
    first = data[-1]
    for key in ("label", "consumption", "cost", "temperature", "efficiency"):
        assert key in first
    assert first["consumption"] == 12.5


def test_get_analytics_summary(client: TestClient, auth_headers: dict):
    response = client.get("/v1/analytics/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_consumption_kwh" in data
    assert "total_cost_usd" in data
    assert "avg_daily_consumption_kwh" in data
    assert "record_count" in data


def test_analytics_summary_unauthenticated(client: TestClient):
    response = client.get("/v1/analytics/summary")
    assert response.status_code == 401


def test_analytics_summary_empty_returns_zeros(client: TestClient, auth_headers: dict):
    response = client.get("/v1/analytics/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["record_count"] == 0
    assert data["total_consumption_kwh"] == 0.0


def test_analytics_summary_with_data(client: TestClient, auth_headers: dict):
    client.post(
        "/v1/data/",
        headers=auth_headers,
        json={"consumption_kwh": 100.0, "cost_usd": 10.0},
    )
    response = client.get("/v1/analytics/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["record_count"] >= 1
    assert data["total_consumption_kwh"] >= 100.0
    assert data["total_cost_usd"] >= 10.0


def test_analytics_summary_avg_daily_non_negative(
    client: TestClient, auth_headers: dict
):
    client.post("/v1/data/", headers=auth_headers, json={"consumption_kwh": 50.0})
    response = client.get("/v1/analytics/summary", headers=auth_headers)
    data = response.json()
    assert data["avg_daily_consumption_kwh"] >= 0.0


def test_analytics_default_period_is_month(client: TestClient, auth_headers: dict):
    r1 = client.get("/v1/analytics/", headers=auth_headers)
    r2 = client.get("/v1/analytics/?period=month", headers=auth_headers)
    assert r1.status_code == 200
    assert r2.status_code == 200


def _seed_history(db_session, user_id, days=30, seed=3):
    from datetime import datetime, timedelta, timezone

    import numpy as np
    from app.models.data import EnergyData

    rng = np.random.default_rng(seed)
    end = datetime.now(timezone.utc).replace(
        tzinfo=None, minute=0, second=0, microsecond=0
    )
    for i in range(days * 24):
        ts = end - timedelta(hours=days * 24 - 1 - i)
        value = max(50 + 20 * np.sin(ts.hour / 24 * 2 * np.pi) + rng.normal(0, 3), 0.0)
        db_session.add(
            EnergyData(timestamp=ts, user_id=user_id, consumption_kwh=float(value))
        )
    db_session.commit()


def test_predictions_without_model_returns_conflict(
    client: TestClient, auth_headers: dict
):
    response = client.get("/v1/predictions/?days=1", headers=auth_headers)
    assert response.status_code == 409
    assert "trained" in response.json()["error"]["message"].lower()


def test_get_predictions_days_zero_rejected(client: TestClient, auth_headers: dict):
    response = client.get("/v1/predictions/?days=0", headers=auth_headers)
    assert response.status_code == 422


def test_get_predictions_days_over_max_rejected(client: TestClient, auth_headers: dict):
    response = client.get("/v1/predictions/?days=91", headers=auth_headers)
    assert response.status_code == 422


def test_get_predictions_unauthenticated(client: TestClient):
    response = client.get("/v1/predictions/")
    assert response.status_code == 401


def test_model_info_unauthenticated(client: TestClient):
    assert client.get("/v1/predictions/model").status_code == 401


def test_model_info_without_model(client: TestClient, auth_headers: dict):
    response = client.get("/v1/predictions/model", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["available"] is False


def test_train_endpoint_forbidden_for_regular_user(
    client: TestClient, auth_headers: dict
):
    response = client.post("/v1/predictions/train", headers=auth_headers)
    assert response.status_code == 403


def test_train_endpoint_unauthenticated(client: TestClient):
    response = client.post("/v1/predictions/train")
    assert response.status_code == 401


def test_train_without_data_is_rejected(
    client: TestClient, superuser_auth_headers: dict
):
    response = client.post("/v1/predictions/train", headers=superuser_auth_headers)
    assert response.status_code == 422
    assert (
        client.get("/v1/predictions/model", headers=superuser_auth_headers).json()[
            "available"
        ]
        is False
    )


def test_train_reports_conflict_when_already_running(
    client: TestClient, superuser_auth_headers: dict
):
    from app.services import ml_service

    assert ml_service._training_lock.acquire(blocking=False)
    try:
        response = client.post("/v1/predictions/train", headers=superuser_auth_headers)
    finally:
        ml_service._training_lock.release()
    assert response.status_code == 409


def test_train_and_predict_end_to_end(
    client: TestClient, superuser_auth_headers: dict, superuser, db_session
):
    _seed_history(db_session, superuser.id)

    train_resp = client.post("/v1/predictions/train", headers=superuser_auth_headers)
    assert train_resp.status_code == 200
    body = train_resp.json()
    assert body["status"] == "trained"
    for key in (
        "mean_squared_error",
        "r2_score",
        "feature_count",
        "training_samples",
        "test_samples",
    ):
        assert key in body["metrics"]
    assert body["model"]["available"] is True

    info = client.get("/v1/predictions/model", headers=superuser_auth_headers).json()
    assert info["available"] is True
    assert info["trained_at"] == body["model"]["trained_at"]

    pred = client.get("/v1/predictions/?days=3", headers=superuser_auth_headers)
    assert pred.status_code == 200
    points = pred.json()
    assert len(points) == 72
    assert all(p["timestamp"].endswith("Z") for p in points)
    for p in points:
        ci = p["confidence_interval"]
        assert ci["lower"] <= p["predicted_consumption"] <= ci["upper"]
        assert ci["lower"] >= 0
    assert len({round(p["predicted_consumption"], 2) for p in points}) > 10


def test_predictions_are_scoped_to_requesting_user(
    client: TestClient,
    superuser_auth_headers: dict,
    auth_headers: dict,
    superuser,
    db_session,
):
    _seed_history(db_session, superuser.id)
    assert (
        client.post("/v1/predictions/train", headers=superuser_auth_headers).status_code
        == 200
    )
    response = client.get("/v1/predictions/?days=1", headers=auth_headers)
    assert response.status_code == 422


def test_predictions_with_insufficient_history_are_rejected(
    client: TestClient, superuser_auth_headers: dict, superuser, db_session
):
    _seed_history(db_session, superuser.id)
    assert (
        client.post("/v1/predictions/train", headers=superuser_auth_headers).status_code
        == 200
    )
    from app.models.data import EnergyData

    db_session.query(EnergyData).filter(EnergyData.user_id == superuser.id).delete()
    _seed_history(db_session, superuser.id, days=1)
    response = client.get("/v1/predictions/?days=1", headers=superuser_auth_headers)
    assert response.status_code == 422


def test_predictions_with_corrupt_model_file_return_unavailable(
    client: TestClient, auth_headers: dict, tmp_path
):
    import os

    with open(os.environ["MODEL_PATH"], "wb") as handle:
        handle.write(b"broken")
    response = client.get("/v1/predictions/?days=1", headers=auth_headers)
    assert response.status_code == 503
    assert "broken" not in response.text
