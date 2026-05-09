from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.energy_record import EnergyRecord
from app.models.points import Redemption
from app.schemas.metrics import (
    KPIResponse,
    MonthlyUsageItem,
    MonthlyUsageResponse,
    Co2TrendPoint,
    Co2TrendResponse,
    YoyUsageResponse,
    YoyUsageData,
    YoyUsageDelta
)

router = APIRouter()


@router.get("/kpi", response_model=KPIResponse)
async def get_kpi(
    company_id: Optional[int] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get KPI metrics"""
    # Parse dates
    start = None
    end = None
    if from_date:
        try:
            start = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
        except ValueError:
            start = datetime.now() - timedelta(days=30)
    else:
        start = datetime.now() - timedelta(days=30)

    if to_date:
        try:
            end = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
        except ValueError:
            end = datetime.now()
    else:
        end = datetime.now()

    # Calculate metrics
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0

    energy_query = db.query(EnergyRecord).filter(
        EnergyRecord.timestamp >= start,
        EnergyRecord.timestamp <= end
    )

    records = energy_query.all()

    electricity_total = sum(r.energy_consumed or 0 for r in records)
    gas_total = sum(r.gas_usage or 0 for r in records)
    co2_total = sum(r.co2_reduction or 0 for r in records)

    total_redemptions = db.query(func.count(Redemption.id)).scalar() or 0
    total_points_spent = db.query(func.sum(Redemption.points_spent)).scalar() or 0

    return KPIResponse(
        company_id=company_id,
        range=f"{start.date()} to {end.date()}",
        active_users=active_users,
        electricity_total_kwh=electricity_total,
        gas_total_m3=gas_total,
        co2_reduction_total_kg=co2_total,
        total_redemptions=total_redemptions,
        total_points_spent=total_points_spent or 0
    )


@router.get("/monthly-usage", response_model=MonthlyUsageResponse)
async def get_monthly_usage(
    company_id: Optional[int] = None,
    year: int = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monthly energy usage"""
    target_year = year or datetime.now().year

    months = []
    for month in range(1, 13):
        start_date = datetime(target_year, month, 1)
        if month == 12:
            end_date = datetime(target_year + 1, 1, 1)
        else:
            end_date = datetime(target_year, month + 1, 1)

        records = db.query(EnergyRecord).filter(
            EnergyRecord.timestamp >= start_date,
            EnergyRecord.timestamp < end_date
        ).all()

        electricity = sum(r.energy_consumed or 0 for r in records)
        gas = sum(r.gas_usage or 0 for r in records)

        months.append(MonthlyUsageItem(
            month=f"{target_year}-{month:02d}",
            electricity_kwh=electricity,
            gas_m3=gas
        ))

    return MonthlyUsageResponse(
        company_id=company_id,
        year=target_year,
        months=months
    )


@router.get("/co2-trend", response_model=Co2TrendResponse)
async def get_co2_trend(
    company_id: Optional[int] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    interval: str = Query("month", enum=["month", "week"]),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get CO2 reduction trend"""
    # Parse dates
    if from_date:
        try:
            start = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
        except ValueError:
            start = datetime.now() - timedelta(days=365)
    else:
        start = datetime.now() - timedelta(days=365)

    if to_date:
        try:
            end = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
        except ValueError:
            end = datetime.now()
    else:
        end = datetime.now()

    points = []

    if interval == "month":
        # Group by month
        current = start.replace(day=1)
        while current <= end:
            month_end = (current.replace(day=28) + timedelta(days=4)).replace(day=1)

            records = db.query(EnergyRecord).filter(
                EnergyRecord.timestamp >= current,
                EnergyRecord.timestamp < month_end
            ).all()

            co2 = sum(r.co2_reduction or 0 for r in records)
            points.append(Co2TrendPoint(
                period=current.strftime("%Y-%m"),
                co2_kg=co2
            ))

            current = month_end
    else:
        # Group by week
        current = start
        while current <= end:
            week_end = current + timedelta(days=7)

            records = db.query(EnergyRecord).filter(
                EnergyRecord.timestamp >= current,
                EnergyRecord.timestamp < week_end
            ).all()

            co2 = sum(r.co2_reduction or 0 for r in records)
            points.append(Co2TrendPoint(
                period=current.strftime("%Y-W%W"),
                co2_kg=co2
            ))

            current = week_end

    return Co2TrendResponse(
        company_id=company_id,
        points=points
    )


@router.get("/yoy-usage", response_model=YoyUsageResponse)
async def get_yoy_usage(
    company_id: Optional[int] = None,
    month: str = Query(..., description="Month in YYYY-MM format"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get year-over-year usage comparison"""
    try:
        year, mon = map(int, month.split("-"))
    except ValueError:
        year = datetime.now().year
        mon = datetime.now().month

    # Current period
    current_start = datetime(year, mon, 1)
    if mon == 12:
        current_end = datetime(year + 1, 1, 1)
    else:
        current_end = datetime(year, mon + 1, 1)

    # Previous year same period
    previous_start = datetime(year - 1, mon, 1)
    if mon == 12:
        previous_end = datetime(year, 1, 1)
    else:
        previous_end = datetime(year - 1, mon + 1, 1)

    # Get current period data
    current_records = db.query(EnergyRecord).filter(
        EnergyRecord.timestamp >= current_start,
        EnergyRecord.timestamp < current_end
    ).all()

    current_electricity = sum(r.energy_consumed or 0 for r in current_records)
    current_gas = sum(r.gas_usage or 0 for r in current_records)

    # Get previous period data
    previous_records = db.query(EnergyRecord).filter(
        EnergyRecord.timestamp >= previous_start,
        EnergyRecord.timestamp < previous_end
    ).all()

    previous_electricity = sum(r.energy_consumed or 0 for r in previous_records)
    previous_gas = sum(r.gas_usage or 0 for r in previous_records)

    return YoyUsageResponse(
        company_id=company_id,
        month=month,
        current=YoyUsageData(
            electricity_kwh=current_electricity,
            gas_m3=current_gas
        ),
        previous=YoyUsageData(
            electricity_kwh=previous_electricity,
            gas_m3=previous_gas
        ),
        delta=YoyUsageDelta(
            electricity_kwh=current_electricity - previous_electricity,
            gas_m3=current_gas - previous_gas
        )
    )
