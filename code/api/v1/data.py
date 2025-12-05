from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from ...backend.dependencies import get_db
from ...backend.security import get_current_active_user
from ...crud.data import create_data_record, get_data_records, get_data_by_time_range
from ...schemas.data import EnergyData, EnergyDataCreate
from ...schemas.user import User

router = APIRouter(
    prefix="/data",
    tags=["data"],
    dependencies=[Depends(get_current_active_user)]
)

@router.post("/", response_model=EnergyData)
def create_record(
    data: EnergyDataCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    return create_data_record(db=db, data=data, user_id=current_user.id)

@router.get("/", response_model=List[EnergyData])
def read_records(
    skip: int = 0,
    limit: int = 100,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    records = get_data_records(db, user_id=current_user.id, skip=skip, limit=limit)
    return records

@router.get("/query", response_model=List[EnergyData])
def query_records(
    start_time: datetime,
    end_time: datetime,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    records = get_data_by_time_range(db, user_id=current_user.id, start_time=start_time, end_time=end_time)
    if not records:
        raise HTTPException(status_code=404, detail="No data found for the specified time range")
    return records
