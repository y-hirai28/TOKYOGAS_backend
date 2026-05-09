from app.schemas.user import UserCreate, UserUpdate, UserResponse, Token, TokenData
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceResponse
from app.schemas.energy_record import (
    EnergyRecordCreate,
    EnergyRecordUpdate,
    EnergyRecordResponse,
    DailySummary,
)
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, PopularityItem
from app.schemas.points import (
    PointsBalance,
    PointsHistoryItem,
    PointsHistoryResponse,
    RedeemRequest,
    RedeemResponse,
    EmployeePoints,
    EmployeesResponse,
    RedemptionResponse,
    RedemptionStats,
)
from app.schemas.metrics import (
    KPIResponse,
    MonthlyUsageItem,
    MonthlyUsageResponse,
    Co2TrendPoint,
    Co2TrendResponse,
    YoyUsageResponse,
)
from app.schemas.report import (
    AutoReportRequest,
    AutoReportPreview,
    AutoReportResponse,
    AutoReportStatus,
)

__all__ = [
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "Token",
    "TokenData",
    "DeviceCreate",
    "DeviceUpdate",
    "DeviceResponse",
    "EnergyRecordCreate",
    "EnergyRecordUpdate",
    "EnergyRecordResponse",
    "DailySummary",
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "PopularityItem",
    "PointsBalance",
    "PointsHistoryItem",
    "PointsHistoryResponse",
    "RedeemRequest",
    "RedeemResponse",
    "EmployeePoints",
    "EmployeesResponse",
    "RedemptionResponse",
    "RedemptionStats",
    "KPIResponse",
    "MonthlyUsageItem",
    "MonthlyUsageResponse",
    "Co2TrendPoint",
    "Co2TrendResponse",
    "YoyUsageResponse",
    "AutoReportRequest",
    "AutoReportPreview",
    "AutoReportResponse",
    "AutoReportStatus",
]
