from typing import Optional, List, Dict, Any
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.transaction import Transaction, TransactionStatus
from app.schemas.transaction import TransactionCreate, TransactionUpdate


class TransactionRepository:
    """Repository for transaction database operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, transaction_data: TransactionCreate, user_id: str) -> Transaction:
        """
        Create a new transaction record.
        
        Args:
            transaction_data: Transaction creation data
            user_id: ID of the user creating the payment
            
        Returns:
            Payment: Created payment object 
        """
        transaction = Transaction(
            **transaction_data.model_dump(),
            user_id=user_id
        )
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction
    
    async def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """
        Get transaction by ID.
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            Optional[Transaction]: Transaction object or None
        """
        result = await self.db.execute(
            select(Transaction).where(Transaction.id == transaction_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_payment_id(self, payment_id: str) -> Optional[Transaction]:
        """
        Get transaction by payment gateway payment_id.
        
        Args:
            payment_id: Payment gateway payment ID
            
        Returns:
            Optional[Transaction]: Transaction object or None
        """
        result = await self.db.execute(
            select(Transaction).where(Transaction.payment_id == payment_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_checkout_session_id(self, checkout_session_id: str) -> Optional[Transaction]:
        """
        Get transaction by checkout session ID.
        
        Args:
            checkout_session_id: Checkout session ID
            
        Returns:
            Optional[Transaction]: Transaction object or None
        """
        result = await self.db.execute(
            select(Transaction).where(Transaction.checkout_session_id == checkout_session_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_user_id(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        status: Optional[TransactionStatus] = None
    ) -> tuple[List[Transaction], int]:
        """
        Get transactions by user ID with pagination.
        
        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Optional payment status filter
            
        Returns:
            tuple: (List of transactions, total count)
        """
        query = select(Transaction).where(Transaction.user_id == user_id)
        
        if status:
            query = query.where(Transaction.payment_status == status)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.order_by(Transaction.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        transactions = result.scalars().all()
        
        return list(transactions), total
    
    async def get_by_booking_id(self, booking_id: int) -> List[Transaction]:
        """
        Get transactions by booking ID.
        
        Args:
            booking_id: Booking ID
            
        Returns:
            List[Transaction]: List of transactions
        """
        result = await self.db.execute(
            select(Transaction)
            .where(Transaction.booking_id == booking_id)
            .order_by(Transaction.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[Transaction], int]:
        """
        Get all transactions with pagination and optional filters.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Optional dictionary of filters
            
        Returns:
            tuple: (List of transactions, total count)
        """
        query = select(Transaction)
        
        if filters:
            conditions = []
            if 'status' in filters:
                conditions.append(Transaction.payment_status == filters['status'])
            if 'provider' in filters:
                conditions.append(Transaction.provider == filters['provider'])
            if 'user_id' in filters:
                conditions.append(Transaction.user_id == filters['user_id'])
            if 'booking_id' in filters:
                conditions.append(Transaction.booking_id == filters['booking_id'])
            if 'property_id' in filters:
                conditions.append(Transaction.property_id == filters['property_id'])
            
            if conditions:
                query = query.where(and_(*conditions))
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.order_by(Transaction.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        transactions = result.scalars().all()
        
        return list(transactions), total
    
    async def update(self, transaction_id: int, transaction_data: TransactionUpdate) -> Optional[Transaction]:
        """
        Update transaction record.
        
        Args:
            transaction_id: Transaction ID
            transaction_data: Transaction update data
            
        Returns:
            Optional[Transaction]: Updated transaction object or None
        """
        transaction = await self.get_by_id(transaction_id)
        if not transaction:
            return None
        
        update_data = transaction_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(transaction, field, value)
        
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction
    
    async def update_status(
        self,
        transaction_id: int,
        status: TransactionStatus
    ) -> Optional[Transaction]:
        """
        Update transaction status.
        
        Args:
            transaction_id: Transaction ID
            status: New transaction status
            
        Returns:
            Optional[Transaction]: Updated transaction object or None
        """
        transaction = await self.get_by_id(transaction_id)
        if not transaction:
            return None
        
        transaction.payment_status = status
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction
    
    async def delete(self, transaction_id: int) -> bool:
        """
        Delete transaction record (soft delete by marking as canceled).
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            bool: True if deleted, False otherwise
        """
        transaction = await self.get_by_id(transaction_id)
        if not transaction:
            return False
        
        # Soft delete by updating status to canceled
        transaction.payment_status = TransactionStatus.CANCELED
        await self.db.commit()
        return True
    
    async def exists_by_payment_id(self, payment_id: str) -> bool:
        """
        Check if transaction exists by payment_id.
        
        Args:
            payment_id: Payment gateway payment ID
            
        Returns:
            bool: True if exists, False otherwise
        """
        result = await self.db.execute(
            select(func.count()).where(Transaction.payment_id == payment_id)
        )
        count = result.scalar()
        return count > 0
