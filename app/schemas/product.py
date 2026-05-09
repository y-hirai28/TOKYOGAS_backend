from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str
    points_required: int
    stock: int = 0
    active: Optional[bool] = True
    image_url: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    points_required: Optional[int] = None
    stock: Optional[int] = None
    active: Optional[bool] = None
    image_url: Optional[str] = None


class ProductResponse(ProductBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PopularityItem(BaseModel):
    product_id: int
    title: str
    category: str
    redemption_count: int
    total_points: int
