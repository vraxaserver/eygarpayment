from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, Enum as SQLEnum, JSON
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class TransactionStatus(str, enum.Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    PAID = "paid"
    FAILED = "failed"
    CANCELED = "canceled"
    REFUNDED = "refunded"


class PaymentProvider(str, enum.Enum):
    """Payment provider enumeration."""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    SQUARE = "square"
    RAZORPAY = "razorpay"
    OTHER = "other"


class Transaction(Base):
    """Transaction model for storing payment transactions."""
    
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Payment Gateway Information
    checkout_session_id = Column(String(255), unique=True, index=True, nullable=True)
    payment_id = Column(String(255), unique=True, index=True, nullable=False)
    payment_method_id = Column(String(255), nullable=True)
    payment_method_type = Column(String(100), nullable=True) 
    
    # Payment Status and Details
    payment_status = Column(
        SQLEnum(TransactionStatus),
        default=TransactionStatus.PENDING,
        nullable=False,
        index=True
    )
    currency = Column(String(3), nullable=False, default="USD")  # ISO 4217 currency code
    amount_total = Column(Numeric(10, 2), nullable=False)  # Total amount in specified currency
    
    # Customer Information
    customer_id = Column(String(255), nullable=True, index=True)
    customer_email = Column(String(255), nullable=True, index=True)
    
    # Related Entities
    booking_id = Column(String(255), nullable=True, index=True)
    property_id = Column(String(255), nullable=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)  # User who made the payment
    
    # Provider Information
    provider = Column(
        SQLEnum(PaymentProvider),
        default=PaymentProvider.STRIPE,
        nullable=False
    )
    
    # Metadata
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, payment_id={self.payment_id}, status={self.payment_status})>"
