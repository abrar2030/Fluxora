from fastapi import APIRouter
from src.utils.monitoring import check_feature_store_connection

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "api_status": "ok",
        "feature_store": check_feature_store_connection(),
        "model_cache": check_model_versions(),
        "db_connections": check_database_connections()
    }

@router.get("/ready")
def readiness_probe():
    return {"status": "ready"}
