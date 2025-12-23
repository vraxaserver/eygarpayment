from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.transaction import Transaction, TransactionStatus
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionListResponse,
    TransactionStatusUpdate,
)
from app.repositories.transaction_repository import TransactionRepository


class TransactionService:
    """Service layer for transaction business logic."""
    
    def __init__(self, db: AsyncSession):
        self.repository = TransactionRepository(db)
    
    async def create_transaction(
        self,
        transaction_data: TransactionCreate,
        user_id: str
    ) -> TransactionResponse:
        """
        Create a new transaction.
        
        Args:
            transaction_data: Transaction creation data
            user_id: User ID from JWT token
            
        Returns:
            TransactionResponse: Created transaction
            
        Raises:
            HTTPException: If payment_id already exists
        """
        # Check if payment_id already exists
        exists = await self.repository.exists_by_payment_id(transaction_data.payment_id)
        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment with payment_id '{transaction_data.payment_id}' already exists"
            )
        
        transaction = await self.repository.create(transaction_data, user_id)
        return TransactionResponse.model_validate(transaction)
    
    async def get_transaction_by_id(
        self,
        transaction_id: int,
        user_id: str
    ) -> TransactionResponse:
        """
        Get transaction by ID.
        
        Args:
            transaction_id: Transaction ID
            user_id: User ID from JWT token
            
        Returns:
            TransactionResponse: Transaction details
            
        Raises:
            HTTPException: If transaction not found or unauthorized
        """
        transaction = await self.repository.get_by_id(transaction_id)
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        # Check if user owns this transaction
        if transaction.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this transaction"
            )
        
        return TransactionResponse.model_validate(transaction)
    
    async def get_transaction_by_payment_id(
        self,
        payment_id: str,
        user_id: str
    ) -> TransactionResponse:
        """
        Get transaction by payment gateway payment_id.
        
        Args:
            payment_id: Payment gateway payment ID
            user_id: User ID from JWT token
            
        Returns:
            TransactionResponse: Transaction details
            
        Raises:
            HTTPException: If transaction not found or unauthorized
        """
        transaction = await self.repository.get_by_payment_id(payment_id)
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        if transaction.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this transaction"
            )
        
        return TransactionResponse.model_validate(transaction)
    
    async def get_user_transactions(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 10,
        status: Optional[TransactionStatus] = None
    ) -> TransactionListResponse:
        """
        Get all transactions for a user with pagination.
        
        Args:
            user_id: User ID from JWT token
            page: Page number (1-indexed)
            page_size: Number of items per page
            status: Optional payment status filter
            
        Returns:
            TransactionListResponse: Paginated transaction list
        """
        skip = (page - 1) * page_size
        transactions, total = await self.repository.get_by_user_id(
            user_id=user_id,
            skip=skip,
            limit=page_size,
            status=status
        )
        
        return TransactionListResponse(
            total=total,
            page=page,
            page_size=page_size,
            transactions=[TransactionResponse.model_validate(p) for p in transactions]
        )
    
    async def get_booking_transactions(
        self,
        booking_id: int,
        user_id: int
    ) -> List[TransactionResponse]:
        """
        Get all transactions for a booking.
        
        Args:
            booking_id: Booking ID
            user_id: User ID from JWT token
            
        Returns:
            List[TransactionResponse]: List of transactions
            
        Raises:
            HTTPException: If no transactions found or unauthorized
        """
        transactions = await self.repository.get_by_booking_id(booking_id)
        
        if not transactions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No transactions found for this booking"
            )
        
        # Check if user owns any of these transactions
        if not any(p.user_id == user_id for p in transactions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access these transactions"
            )
        
        # Filter only transactions belonging to this user
        user_transactions = [p for p in transactions if p.user_id == user_id]
        return [TransactionResponse.model_validate(p) for p in user_transactions]
    
    async def update_transaction(
        self,
        transaction_id: int,
        transaction_data: TransactionUpdate,
        user_id: int
    ) -> TransactionResponse:
        """
        Update transaction details.
        
        Args:
            transaction_id: Transaction ID
            transaction_data: Transaction update data
            user_id: User ID from JWT token
            
        Returns:
            TransactionResponse: Updated transaction
            
        Raises:
            HTTPException: If transaction not found or unauthorized
        """
        # Check if transaction exists and user owns it
        transaction = await self.repository.get_by_id(transaction_id)
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        if transaction.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this transaction"
            )
        
        updated_transaction = await self.repository.update(transaction_id, transaction_data)
        return TransactionResponse.model_validate(updated_transaction)
    
    async def update_transaction_status(
        self,
        transaction_id: int,
        status_data: TransactionStatusUpdate,
        user_id: str
    ) -> TransactionResponse:
        """
        Update transaction status.
        
        Args:
            transaction_id: Transaction ID
            status_data: New status
            user_id: User ID from JWT token
            
        Returns:
            TransactionResponse: Updated transaction
            
        Raises:
            HTTPException: If transaction not found or unauthorized
        """
        transaction = await self.repository.get_by_id(transaction_id)
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        if transaction.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this transaction"
            )
        
        updated_transaction = await self.repository.update_status(
            transaction_id,
            status_data.transaction_status
        )
        return TransactionResponse.model_validate(updated_transaction)
    
    async def delete_transaction(
        self,
        transaction_id: int,
        user_id: str
    ) -> Dict[str, str]:
        """
        Delete (cancel) a transaction.
        
        Args:
            transaction_id: Transaction ID
            user_id: User ID from JWT token
            
        Returns:
            Dict: Success message
            
        Raises:
            HTTPException: If transaction not found or unauthorized
        """
        transaction = await self.repository.get_by_id(transaction_id)
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        if transaction.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this transaction"
            )
        
        success = await self.repository.delete(transaction_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete transaction"
            )
        
        return {"message": "Transaction successfully canceled"}
    
    async def get_all_transactions(
        self,
        page: int = 1,
        page_size: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> TransactionListResponse:
        """
        Get all transactions with pagination and filters (admin function).
        Note: This should be protected with admin role in production.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            filters: Optional filters dictionary
            
        Returns:
            TransactionListResponse: Paginated transaction list
        """
        skip = (page - 1) * page_size
        transactions, total = await self.repository.get_all(
            skip=skip,
            limit=page_size,
            filters=filters
        )
        
        return TransactionListResponse(
            total=total,
            page=page,
            page_size=page_size,
            transactions=[TransactionResponse.model_validate(p) for p in transactions]
        )
