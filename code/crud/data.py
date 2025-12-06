from sqlalchemy.orm import Session
from ..code.models.data import EnergyData
from ..code.schemas.data import EnergyDataCreate
from datetime import datetime


def get_data_records(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> Any:
    return (
        db.query(EnergyData)
        .filter(EnergyData.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_data_record(db: Session, data: EnergyDataCreate, user_id: int) -> Any:
    db_data = EnergyData(**data.model_dump(), user_id=user_id)
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data


def get_data_by_time_range(
    db: Session, user_id: int, start_time: datetime, end_time: datetime
) -> Any:
    return (
        db.query(EnergyData)
        .filter(
            EnergyData.user_id == user_id,
            EnergyData.timestamp >= start_time,
            EnergyData.timestamp <= end_time,
        )
        .order_by(EnergyData.timestamp)
        .all()
    )
