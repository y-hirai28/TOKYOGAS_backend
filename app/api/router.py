from fastapi import APIRouter

from app.api.endpoints import auth, users, devices, energy_records, points, products, metrics, reports

api_router = APIRouter()

# Auth endpoints (no prefix for login)
api_router.include_router(auth.router, tags=["auth"])

# User endpoints
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Device endpoints
api_router.include_router(devices.router, prefix="/devices", tags=["devices"])

# Energy record endpoints
api_router.include_router(energy_records.router, prefix="/energy-records", tags=["energy-records"])

# Points endpoints (includes mobile and admin)
api_router.include_router(points.router, tags=["points"])

# Products/Rewards endpoints
api_router.include_router(products.router, tags=["products"])

# Metrics endpoints
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])

# Reports endpoints
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
