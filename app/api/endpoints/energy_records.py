from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.device import Device
from app.models.energy_record import EnergyRecord
from app.schemas.energy_record import (
    EnergyRecordCreate,
    EnergyRecordUpdate,
    EnergyRecordResponse,
    DailySummary
)

router = APIRouter()


@router.get("/", response_model=List[EnergyRecordResponse])
async def get_energy_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    device_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get energy records with optional filters"""
    query = db.query(EnergyRecord).filter(EnergyRecord.user_id == current_user.id)

    if device_id:
        query = query.filter(EnergyRecord.device_id == device_id)

    if start_date:
        try:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(EnergyRecord.timestamp >= start)
        except ValueError:
            pass

    if end_date:
        try:
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(EnergyRecord.timestamp <= end)
        except ValueError:
            pass

    records = query.order_by(EnergyRecord.timestamp.desc()).offset(skip).limit(limit).all()
    return records


@router.get("/daily-summary", response_model=DailySummary)
async def get_daily_summary(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily summary of energy records"""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )

    # Get records for the day
    start_of_day = datetime.combine(target_date, datetime.min.time())
    end_of_day = datetime.combine(target_date, datetime.max.time())

    records = db.query(EnergyRecord).filter(
        EnergyRecord.user_id == current_user.id,
        EnergyRecord.timestamp >= start_of_day,
        EnergyRecord.timestamp <= end_of_day
    ).all()

    total_consumed = sum(r.energy_consumed or 0 for r in records)
    total_produced = sum(r.energy_produced or 0 for r in records)
    total_gas = sum(r.gas_usage or 0 for r in records)
    total_co2 = sum(r.co2_reduction or 0 for r in records)

    return DailySummary(
        date=date,
        total_energy_consumed=total_consumed,
        total_energy_produced=total_produced,
        total_gas_usage=total_gas,
        total_co2_reduction=total_co2,
        record_count=len(records)
    )


@router.get("/{record_id}", response_model=EnergyRecordResponse)
async def get_energy_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific energy record"""
    record = db.query(EnergyRecord).filter(
        EnergyRecord.id == record_id,
        EnergyRecord.user_id == current_user.id
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Energy record not found"
        )
    return record


@router.post("/", response_model=EnergyRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_energy_record(
    record_in: EnergyRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new energy record"""
    # Verify device ownership
    device = db.query(Device).filter(
        Device.id == record_in.device_id,
        Device.owner_id == current_user.id
    ).first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    db_record = EnergyRecord(
        **record_in.model_dump(),
        user_id=current_user.id
    )

    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return db_record


@router.put("/{record_id}", response_model=EnergyRecordResponse)
async def update_energy_record(
    record_id: int,
    record_update: EnergyRecordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an energy record"""
    record = db.query(EnergyRecord).filter(
        EnergyRecord.id == record_id,
        EnergyRecord.user_id == current_user.id
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Energy record not found"
        )

    update_data = record_update.model_dump(exclude_unset=True)

    # If device_id is being updated, verify ownership
    if "device_id" in update_data:
        device = db.query(Device).filter(
            Device.id == update_data["device_id"],
            Device.owner_id == current_user.id
        ).first()
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )

    for field, value in update_data.items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)

    return record


@router.delete("/{record_id}")
async def delete_energy_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an energy record"""
    record = db.query(EnergyRecord).filter(
        EnergyRecord.id == record_id,
        EnergyRecord.user_id == current_user.id
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Energy record not found"
        )

    db.delete(record)
    db.commit()

    return {"message": "Record deleted successfully"}
