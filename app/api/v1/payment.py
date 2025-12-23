from fastapi import APIRouter, Depends, Query, status
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.services.transaction_service import TransactionService
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionListResponse,
    TransactionStatusUpdate,
)
from app.models.transaction import TransactionStatus, PaymentProvider
from app.schemas.common import UserInfo

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post(
    "/",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new payment",
    description="Create a new payment record. Requires authentication."
)
async def create_transaction(
    payment_data: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserInfo = Depends(get_current_user)
):
    """
    Create a new payment.
    
    - **payment_id**: Unique identifier from payment gateway (required)
    - **amount_total**: Payment amount (required)
    - **currency**: Currency code (default: USD)
    - **payment_status**: Payment status (default: pending)
    - **provider**: Payment provider (default: stripe)
    """
    print("current_user =======================", current_user)
    service = TransactionService(db)
    return await service.create_transaction(payment_data, str(current_user.id))


@router.get(
    "/",
    response_model=TransactionListResponse,
    summary="Get user payments",
    description="Get all payments for the authenticated user with pagination."
)
async def get_user_transactions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[TransactionStatus] = Query(None, description="Filter by payment status"),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Get all payments for the authenticated user.
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 10, max: 100)
    - **status**: Optional filter by payment status
    """
    service = TransactionService(db)
    return await service.get_user_transactions(
        user_id=current_user_id,
        page=page,
        page_size=page_size,
        status=status
    )


@router.get(
    "/{payment_id}",
    response_model=TransactionResponse,
    summary="Get payment by ID",
    description="Get a specific payment by its ID. User must own the payment."
)
async def get_payment(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Get payment details by payment ID.
    
    - **payment_id**: The ID of the payment to retrieve
    """
    service = TransactionService(db)
    return await service.get_transaction_by_payment_id(payment_id, current_user_id)


@router.get(
    "/payment-gateway/{payment_id}",
    response_model=TransactionResponse,
    summary="Get payment by gateway payment ID",
    description="Get a specific payment by its payment gateway ID. User must own the payment."
)
async def get_payment_by_gateway_id(
    payment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Get payment details by payment gateway payment_id.
    
    - **payment_id**: The payment gateway payment ID
    """
    service = TransactionService(db)
    return await service.get_transaction_by_payment_id(payment_id, current_user_id)


@router.get(
    "/booking/{booking_id}",
    response_model=list[TransactionResponse],
    summary="Get payments by booking ID",
    description="Get all payments associated with a specific booking."
)
async def get_booking_transactions(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Get all payments for a specific booking.
    
    - **booking_id**: The ID of the booking
    """
    service = TransactionService(db)
    return await service.get_booking_transactions(booking_id, current_user_id)


@router.put(
    "/{payment_id}",
    response_model=TransactionResponse,
    summary="Update payment",
    description="Update payment details. User must own the payment."
)
async def update_payment(
    payment_id: int,
    payment_data: TransactionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Update payment details.
    
    - **payment_id**: The ID of the payment to update
    - Only fields provided in the request body will be updated
    """
    service = TransactionService(db)
    return await service.update_payment(payment_id, payment_data, current_user_id)


@router.patch(
    "/{payment_id}/status",
    response_model=TransactionResponse,
    summary="Update payment status",
    description="Update only the payment status. User must own the payment."
)
async def update_transaction_status(
    payment_id: int,
    status_data: TransactionStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Update payment status.
    
    - **payment_id**: The ID of the payment
    - **payment_status**: New payment status
    """
    service = TransactionService(db)
    return await service.update_transaction_status(payment_id, status_data, current_user_id)


@router.delete(
    "/{payment_id}",
    response_model=Dict[str, str],
    summary="Cancel payment",
    description="Cancel a payment (soft delete by marking as canceled). User must own the payment."
)
async def delete_transaction(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Cancel a payment.
    
    - **payment_id**: The ID of the payment to cancel
    """
    service = TransactionService(db)
    return await service.delete_transaction(payment_id, current_user_id)


# Admin endpoint (should be protected with admin role in production)
@router.get(
    "/admin/all",
    response_model=TransactionListResponse,
    summary="Get all payments (Admin)",
    description="Get all payments with pagination and filters. Should be admin-only."
)
async def get_all_transactions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[TransactionStatus] = Query(None, description="Filter by status"),
    provider: Optional[PaymentProvider] = Query(None, description="Filter by provider"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    booking_id: Optional[int] = Query(None, description="Filter by booking ID"),
    property_id: Optional[int] = Query(None, description="Filter by property ID"),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Get all payments with filters (Admin only).
    
    Note: In production, add admin role verification.
    """
    filters = {}
    if status:
        filters['status'] = status
    if provider:
        filters['provider'] = provider
    if user_id:
        filters['user_id'] = user_id
    if booking_id:
        filters['booking_id'] = booking_id
    if property_id:
        filters['property_id'] = property_id
    
    service = TransactionService(db)
    return await service.get_all_transactions(
        page=page,
        page_size=page_size,
        filters=filters if filters else None
    )
