from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class KPIResponse(BaseModel):
    company_id: Optional[int] = None
    range: Optional[str] = None
    active_users: int
    electricity_total_kwh: float
    gas_total_m3: float
    co2_reduction_total_kg: float
    total_redemptions: int
    total_points_spent: int


class MonthlyUsageItem(BaseModel):
    month: str
    electricity_kwh: float
    gas_m3: float


class MonthlyUsageResponse(BaseModel):
    company_id: Optional[int] = None
    year: int
    months: List[MonthlyUsageItem]


class Co2TrendPoint(BaseModel):
    period: str
    co2_kg: float


class Co2TrendResponse(BaseModel):
    company_id: Optional[int] = None
    points: List[Co2TrendPoint]


class YoyUsageDelta(BaseModel):
    electricity_kwh: float
    gas_m3: float


class YoyUsageData(BaseModel):
    electricity_kwh: float
    gas_m3: float


class YoyUsageResponse(BaseModel):
    company_id: Optional[int] = None
    month: str
    current: YoyUsageData
    previous: YoyUsageData
    delta: YoyUsageDelta
