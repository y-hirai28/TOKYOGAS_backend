from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class EnergyRecord(Base):
    __tablename__ = "energy_records"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)

    # Energy metrics
    energy_produced = Column(Float)
    energy_consumed = Column(Float)
    energy_stored = Column(Float)
    grid_import = Column(Float)
    grid_export = Column(Float)

    # Electrical measurements
    voltage = Column(Float)
    current = Column(Float)
    power = Column(Float)

    # Environmental
    temperature = Column(Float)
    efficiency = Column(Float)
    status = Column(String(50))

    # Gas metrics
    gas_usage = Column(Float)

    # CO2
    co2_reduction = Column(Float)

    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    device = relationship("Device", back_populates="energy_records")
    user = relationship("User", back_populates="energy_records")
