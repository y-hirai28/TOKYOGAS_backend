from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PointsBalance(BaseModel):
    current_balance: int
    user_id: Optional[int] = None
    last_updated: Optional[datetime] = None


class PointsHistoryItem(BaseModel):
    id: int
    type: str  # "earn" or "redeem"
    points: int
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PointsHistoryResponse(BaseModel):
    history: List[PointsHistoryItem]


class RedeemRequest(BaseModel):
    productId: int
    userId: Optional[int] = None


class RedeemResponse(BaseModel):
    new_balance: int
    redemption_id: int


class EmployeePoints(BaseModel):
    id: int
    name: str
    email: str
    department: Optional[str] = None
    points: int
    rank: int

    class Config:
        from_attributes = True


class EmployeesResponse(BaseModel):
    employees: List[EmployeePoints]
    total: int


class RedemptionResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    points_spent: int
    status: str
    created_at: datetime
    product: Optional[dict] = None

    class Config:
        from_attributes = True


class RedemptionStats(BaseModel):
    total_redemptions: int
    total_points_spent: int
    active_products: int
    period: Optional[str] = None
