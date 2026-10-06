from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User


def _utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class EnergyData(Base):
    __tablename__ = "energy_data"
    __table_args__ = (
        Index("ix_energy_data_user_id_timestamp", "user_id", "timestamp"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=_utc_now_naive, index=True, nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    consumption_kwh: Mapped[float] = mapped_column(Float, nullable=False)
    generation_kwh: Mapped[float | None] = mapped_column(Float, nullable=True)
    cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    temperature_c: Mapped[float | None] = mapped_column(Float, nullable=True)
    humidity_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    owner: Mapped["User"] = relationship(back_populates="energy_records")

    def __repr__(self) -> str:
        return (
            f"<EnergyData(id={self.id}, timestamp='{self.timestamp}', "
            f"consumption={self.consumption_kwh})>"
        )
