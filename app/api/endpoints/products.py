from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.product import Product
from app.models.points import Redemption
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, PopularityItem
from app.schemas.points import RedemptionStats

router = APIRouter()


# Public rewards endpoints
@router.get("/rewards/", response_model=List[ProductResponse])
async def get_rewards(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all active rewards/products"""
    products = db.query(Product).filter(Product.active == True).all()
    return products


@router.get("/rewards/admin/popularity", response_model=List[PopularityItem])
async def get_rewards_popularity(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get product popularity stats (admin)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    # Get redemption counts per product
    results = db.query(
        Redemption.product_id,
        func.count(Redemption.id).label('count'),
        func.sum(Redemption.points_spent).label('total_points')
    ).group_by(Redemption.product_id).all()

    popularity = []
    for r in results:
        product = db.query(Product).filter(Product.id == r.product_id).first()
        if product:
            popularity.append(PopularityItem(
                product_id=product.id,
                title=product.title,
                category=product.category,
                redemption_count=r.count,
                total_points=r.total_points or 0
            ))

    return sorted(popularity, key=lambda x: x.redemption_count, reverse=True)


# Incentives endpoints
@router.get("/incentives/rewards", response_model=List[ProductResponse])
async def get_incentive_rewards(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all incentive rewards"""
    products = db.query(Product).all()
    return products


@router.post("/incentives/rewards", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_incentive_reward(
    product_in: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new incentive reward (admin)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    db_product = Product(**product_in.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product


@router.put("/incentives/rewards/{product_id}", response_model=ProductResponse)
async def update_incentive_reward(
    product_id: int,
    product_update: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an incentive reward (admin)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product


@router.patch("/incentives/rewards/{product_id}/publish", response_model=ProductResponse)
async def publish_incentive_reward(
    product_id: int,
    active: bool = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle product active status (admin)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    product.active = active
    db.commit()
    db.refresh(product)

    return product


@router.get("/incentives/redemptions/summary", response_model=RedemptionStats)
async def get_redemption_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get redemption summary stats"""
    total_redemptions = db.query(func.count(Redemption.id)).scalar() or 0
    total_points = db.query(func.sum(Redemption.points_spent)).scalar() or 0
    active_products = db.query(func.count(Product.id)).filter(Product.active == True).scalar() or 0

    return RedemptionStats(
        total_redemptions=total_redemptions,
        total_points_spent=total_points,
        active_products=active_products
    )


# Admin Incentives endpoints
@router.get("/admin/incentives/products", response_model=List[ProductResponse])
async def get_admin_products(
    search: Optional[str] = None,
    category: Optional[str] = None,
    active: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all products with filters (admin)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    query = db.query(Product)

    if search:
        query = query.filter(Product.title.ilike(f"%{search}%"))
    if category:
        query = query.filter(Product.category == category)
    if active is not None:
        query = query.filter(Product.active == active)

    return query.all()


@router.post("/admin/incentives/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_admin_product(
    product_in: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new product (admin)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    db_product = Product(**product_in.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product


@router.put("/admin/incentives/products/{product_id}", response_model=ProductResponse)
async def update_admin_product(
    product_id: int,
    product_update: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a product (admin)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product


@router.patch("/admin/incentives/products/{product_id}/toggle")
async def toggle_admin_product(
    product_id: int,
    active: bool,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle product active status (admin)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    product.active = active
    db.commit()

    return {"message": "Product status updated", "active": active}


@router.get("/admin/incentives/stats", response_model=RedemptionStats)
async def get_admin_incentive_stats(
    period: str = Query("month", enum=["month", "quarter", "year"]),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get incentive statistics (admin)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    total_redemptions = db.query(func.count(Redemption.id)).scalar() or 0
    total_points = db.query(func.sum(Redemption.points_spent)).scalar() or 0
    active_products = db.query(func.count(Product.id)).filter(Product.active == True).scalar() or 0

    return RedemptionStats(
        total_redemptions=total_redemptions,
        total_points_spent=total_points,
        active_products=active_products,
        period=period
    )


@router.get("/admin/incentives/popularity", response_model=List[PopularityItem])
async def get_admin_popularity(
    period: str = Query("month", enum=["month", "quarter", "year"]),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get product popularity (admin)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    results = db.query(
        Redemption.product_id,
        func.count(Redemption.id).label('count'),
        func.sum(Redemption.points_spent).label('total_points')
    ).group_by(Redemption.product_id).all()

    popularity = []
    for r in results:
        product = db.query(Product).filter(Product.id == r.product_id).first()
        if product:
            popularity.append(PopularityItem(
                product_id=product.id,
                title=product.title,
                category=product.category,
                redemption_count=r.count,
                total_points=r.total_points or 0
            ))

    return sorted(popularity, key=lambda x: x.redemption_count, reverse=True)
