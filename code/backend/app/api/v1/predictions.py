import logging
from typing import Annotated, Any

from app.core.retry import retry
from app.core.security import get_current_active_user, get_current_superuser
from app.db.dependencies import get_db
from app.schemas.prediction import ModelInfo, PredictionPoint, TrainResponse
from app.schemas.user import User
from app.services import ml_service
from fastapi import APIRouter, Depends, HTTPException, Query, status
from ml_core import (
    DataValidationError,
    InsufficientDataError,
    InsufficientHistoryError,
    ModelLoadError,
    ModelNotFoundError,
)
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("/", response_model=list[PredictionPoint])
def get_predictions(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    days: int = Query(default=7, ge=1, le=90),
) -> Any:
    try:
        return ml_service.predict_for_user(db, current_user.id, days)
    except ModelNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "No trained model is available yet. "
                "An administrator must train the model first."
            ),
        )
    except InsufficientHistoryError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        )
    except ModelLoadError as exc:
        logger.error("Model could not be loaded: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The forecasting model is currently unavailable.",
        )


@router.get("/model", response_model=ModelInfo)
def get_model_info(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Any:
    try:
        return ml_service.model_status()
    except ModelLoadError as exc:
        logger.error("Model could not be loaded: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The forecasting model is currently unavailable.",
        )


@retry(max_attempts=2, retry_exceptions=(OSError,), base_delay=0.5, jitter=False)
def _train_with_retry(db: Session) -> dict[str, Any]:
    return ml_service.train_from_database(db)


@router.post("/train", response_model=TrainResponse)
def trigger_training(
    current_user: Annotated[User, Depends(get_current_superuser)],
    db: Annotated[Session, Depends(get_db)],
) -> Any:
    try:
        result = _train_with_retry(db)
    except ml_service.TrainingInProgressError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except (InsufficientDataError, DataValidationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        )
    return {"status": "trained", **result}
