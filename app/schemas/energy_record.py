from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EnergyRecordBase(BaseModel):
    timestamp: datetime
    energy_produced: Optional[float] = None
    energy_consumed: Optional[float] = None
    energy_stored: Optional[float] = None
    grid_import: Optional[float] = None
    grid_export: Optional[float] = None
    voltage: Optional[float] = None
    current: Optional[float] = None
    power: Optional[float] = None
    temperature: Optional[float] = None
    efficiency: Optional[float] = None
    status: Optional[str] = None
    gas_usage: Optional[float] = None
    co2_reduction: Optional[float] = None


class EnergyRecordCreate(EnergyRecordBase):
    device_id: int


class EnergyRecordUpdate(BaseModel):
    timestamp: Optional[datetime] = None
    energy_produced: Optional[float] = None
    energy_consumed: Optional[float] = None
    energy_stored: Optional[float] = None
    grid_import: Optional[float] = None
    grid_export: Optional[float] = None
    voltage: Optional[float] = None
    current: Optional[float] = None
    power: Optional[float] = None
    temperature: Optional[float] = None
    efficiency: Optional[float] = None
    status: Optional[str] = None
    gas_usage: Optional[float] = None
    co2_reduction: Optional[float] = None
    device_id: Optional[int] = None


class EnergyRecordResponse(EnergyRecordBase):
    id: int
    device_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class DailySummary(BaseModel):
    date: str
    total_energy_consumed: float
    total_energy_produced: float
    total_gas_usage: float
    total_co2_reduction: float
    record_count: int
