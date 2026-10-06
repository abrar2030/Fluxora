from datetime import datetime, timezone

from pydantic import BaseModel, field_serializer, field_validator


def to_naive_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


class EnergyDataBase(BaseModel):
    consumption_kwh: float
    generation_kwh: float | None = None
    cost_usd: float | None = None
    temperature_c: float | None = None
    humidity_percent: float | None = None

    @field_validator("consumption_kwh")
    @classmethod
    def consumption_must_be_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("consumption_kwh must be non-negative")
        return v

    @field_validator("generation_kwh")
    @classmethod
    def generation_must_be_non_negative(cls, v: float | None) -> float | None:
        if v is not None and v < 0:
            raise ValueError("generation_kwh must be non-negative")
        return v

    @field_validator("cost_usd")
    @classmethod
    def cost_must_be_non_negative(cls, v: float | None) -> float | None:
        if v is not None and v < 0:
            raise ValueError("cost_usd must be non-negative")
        return v

    @field_validator("humidity_percent")
    @classmethod
    def humidity_must_be_in_range(cls, v: float | None) -> float | None:
        if v is not None and not (0.0 <= v <= 100.0):
            raise ValueError("humidity_percent must be between 0 and 100")
        return v

    @field_validator("temperature_c")
    @classmethod
    def temperature_must_be_in_range(cls, v: float | None) -> float | None:
        if v is not None and not (-100.0 <= v <= 100.0):
            raise ValueError("temperature_c must be between -100 and 100")
        return v


class EnergyDataCreate(EnergyDataBase):
    timestamp: datetime | None = None

    @field_validator("timestamp")
    @classmethod
    def normalise_timestamp(cls, v: datetime | None) -> datetime | None:
        return to_naive_utc(v) if v is not None else v


class EnergyDataUpdate(BaseModel):
    consumption_kwh: float | None = None
    generation_kwh: float | None = None
    cost_usd: float | None = None
    temperature_c: float | None = None
    humidity_percent: float | None = None

    @field_validator("consumption_kwh")
    @classmethod
    def consumption_must_be_non_negative(cls, v: float | None) -> float | None:
        if v is not None and v < 0:
            raise ValueError("consumption_kwh must be non-negative")
        return v


class EnergyData(EnergyDataBase):
    id: int
    timestamp: datetime
    user_id: int

    model_config = {"from_attributes": True}

    @field_serializer("timestamp")
    def serialize_timestamp(self, value: datetime) -> str:
        return to_naive_utc(value).strftime("%Y-%m-%dT%H:%M:%SZ")
