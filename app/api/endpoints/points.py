from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.product import Product
from app.models.points import PointsHistory, Redemption
from app.schemas.points import (
    PointsBalance,
    PointsHistoryItem,
    PointsHistoryResponse,
    RedeemRequest,
    RedeemResponse,
    EmployeePoints,
    EmployeesResponse,
    RedemptionResponse,
)

router = APIRouter()


# Mobile Points API
@router.get("/mobile/points/balance", response_model=PointsBalance)
async def get_points_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's points balance"""
    return PointsBalance(
        current_balance=current_user.points_balance or 0,
        user_id=current_user.id,
        last_updated=current_user.updated_at
    )


@router.get("/mobile/points/history", response_model=PointsHistoryResponse)
async def get_points_history(
    userId: Optional[int] = None,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get points history for current user"""
    user_id = userId if userId and current_user.is_superuser else current_user.id

    history = db.query(PointsHistory).filter(
        PointsHistory.user_id == user_id
    ).order_by(desc(PointsHistory.created_at)).limit(limit).all()

    return PointsHistoryResponse(
        history=[PointsHistoryItem.model_validate(h) for h in history]
    )


@router.post("/mobile/redeem", response_model=RedeemResponse)
async def redeem_product(
    redeem_request: RedeemRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Redeem a product with points"""
    # Get the product
    product = db.query(Product).filter(
        Product.id == redeem_request.productId,
        Product.active == True
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or inactive"
        )

    if product.stock <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product out of stock"
        )

    if current_user.points_balance < product.points_required:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient points"
        )

    # Deduct points
    current_user.points_balance -= product.points_required
    product.stock -= 1

    # Create redemption record
    redemption = Redemption(
        user_id=current_user.id,
        product_id=product.id,
        points_spent=product.points_required,
        status="completed"
    )

    # Create points history
    history = PointsHistory(
        user_id=current_user.id,
        type="redeem",
        points=-product.points_required,
        description=f"Redeemed: {product.title}"
    )

    db.add(redemption)
    db.add(history)
    db.commit()
    db.refresh(redemption)

    return RedeemResponse(
        new_balance=current_user.points_balance,
        redemption_id=redemption.id
    )


# Admin Points API
@router.get("/admin/points/employees", response_model=EmployeesResponse)
async def get_employees_points(
    sort_by: str = Query("points", enum=["points", "name", "department"]),
    sort_order: str = Query("desc", enum=["asc", "desc"]),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all employees with their points (admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    query = db.query(User).filter(User.is_active == True)

    # Apply sorting
    if sort_by == "points":
        order_col = User.points_balance
    elif sort_by == "name":
        order_col = User.full_name
    else:
        order_col = User.department

    if sort_order == "desc":
        query = query.order_by(desc(order_col))
    else:
        query = query.order_by(order_col)

    users = query.all()

    # Add ranking
    employees = []
    for rank, user in enumerate(users, 1):
        employees.append(EmployeePoints(
            id=user.id,
            name=user.full_name or user.email,
            email=user.email,
            department=user.department,
            points=user.points_balance or 0,
            rank=rank
        ))

    return EmployeesResponse(
        employees=employees,
        total=len(employees)
    )


# User redemptions
@router.get("/rewards/my-redemptions", response_model=List[RedemptionResponse])
async def get_my_redemptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's redemption history"""
    redemptions = db.query(Redemption).filter(
        Redemption.user_id == current_user.id
    ).order_by(desc(Redemption.created_at)).all()

    result = []
    for r in redemptions:
        product = db.query(Product).filter(Product.id == r.product_id).first()
        result.append(RedemptionResponse(
            id=r.id,
            user_id=r.user_id,
            product_id=r.product_id,
            points_spent=r.points_spent,
            status=r.status,
            created_at=r.created_at,
            product={
                "id": product.id,
                "title": product.title,
                "category": product.category
            } if product else None
        ))

    return result
