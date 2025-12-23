from fastapi import APIRouter
from app.api.v1 import payment

api_router = APIRouter()

# Include payment routes
api_router.include_router(payment.router)

__all__ = ["api_router"]
