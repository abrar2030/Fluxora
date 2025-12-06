from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime


class EnergyData(Base):
    __tablename__ = "energy_data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Core data fields
    consumption_kwh = Column(Float, nullable=False)
    generation_kwh = Column(Float, nullable=True)  # e.g., solar generation
    cost_usd = Column(Float, nullable=True)

    # Contextual data fields
    temperature_c = Column(Float, nullable=True)
    humidity_percent = Column(Float, nullable=True)

    # Relationship to the User model
    owner = relationship("User")

    def __repr__(self):
        return f"<EnergyData(id={self.id}, timestamp='{self.timestamp}', consumption={self.consumption_kwh})>"
