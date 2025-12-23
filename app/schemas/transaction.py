from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.models.transaction import TransactionStatus, PaymentProvider


class TransactionBase(BaseModel):
    """Base schema for transaction data."""
    # Maps to the session_id in your payload
    checkout_session_id: Optional[str] = Field(None, max_length=255)
    
    payment_id: str = Field(..., max_length=255, description="Unique payment identifier from payment gateway")
    payment_method_id: Optional[str] = Field(None, max_length=255)
    
    payment_method_type: Optional[str] = Field(None, max_length=100)
    
    payment_status: TransactionStatus = Field(default=TransactionStatus.PENDING)
    currency: str = Field(default="USD", max_length=3, description="ISO 4217 currency code")
    
    # Decimal handles the 1350 integer from the payload correctly
    amount_total: Decimal = Field(..., gt=0, decimal_places=2, description="Total amount")
    
    customer_id: Optional[str] = Field(None, max_length=255)
    customer_email: Optional[EmailStr] = None
    booking_id: Optional[str] = Field(None, max_length=255)
    property_id: Optional[str] = Field(None, max_length=255)
    provider: PaymentProvider = Field(default=PaymentProvider.STRIPE)
    description: Optional[str] = None


class TransactionCreate(TransactionBase):
    """Schema for creating a transaction."""
    pass


class TransactionUpdate(BaseModel):
    """Schema for updating a payment."""
    checkout_session_id: Optional[str] = Field(None, max_length=255)
    payment_method_id: Optional[str] = Field(None, max_length=255)
    payment_method_type: Optional[str] = Field(None, max_length=100)
    payment_status: Optional[TransactionStatus] = None
    currency: Optional[str] = Field(None, max_length=3)
    amount_total: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    customer_id: Optional[str] = Field(None, max_length=255)
    customer_email: Optional[EmailStr] = None
    booking_id: Optional[str] = Field(None, max_length=255)
    property_id: Optional[str] = Field(None, max_length=255)
    provider: Optional[PaymentProvider] = None
    description: Optional[str] = None

    model_config = ConfigDict(extra='forbid')


class TransactionResponse(TransactionBase):
    """Schema for transaction response."""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionListResponse(BaseModel):
    """Schema for paginated transaction list response."""
    total: int
    page: int
    page_size: int
    transactions: list[TransactionResponse]

    model_config = ConfigDict(from_attributes=True)


class TransactionStatusUpdate(BaseModel):
    """Schema for updating transaction status."""
    transaction_status: TransactionStatus

    model_config = ConfigDict(extra='forbid')
