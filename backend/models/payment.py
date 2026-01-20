"""
Payment Model
Represents a payment transaction for a violation
"""

from typing import Optional, Dict
from datetime import datetime


class Payment:
    """
    Payment class representing a violation payment transaction
    """
    
    VALID_METHODS = ['cash', 'card', 'online', 'cheque']
    
    def __init__(
        self,
        payment_id: Optional[int] = None,
        violation_id: int = 0,
        payment_date: Optional[datetime] = None,
        amount_paid: float = 0.0,
        payment_method: str = 'cash',
        transaction_id: str = '',
        created_at: Optional[datetime] = None
    ):
        """
        Initialize Payment object
        
        Args:
            payment_id: Unique payment identifier
            violation_id: Associated violation ID
            payment_date: Date and time of payment
            amount_paid: Amount paid
            payment_method: Method of payment (cash/card/online/cheque)
            transaction_id: Transaction reference ID
            created_at: Record creation timestamp
        """
        self._payment_id = payment_id
        self._violation_id = violation_id
        self._payment_date = payment_date or datetime.now()
        self._amount_paid = float(amount_paid)
        self._payment_method = payment_method if payment_method in self.VALID_METHODS else 'cash'
        self._transaction_id = transaction_id
        self._created_at = created_at or datetime.now()
    
    # Getters
    @property
    def payment_id(self) -> Optional[int]:
        return self._payment_id
    
    @property
    def violation_id(self) -> int:
        return self._violation_id
    
    @property
    def payment_date(self) -> datetime:
        return self._payment_date
    
    @property
    def amount_paid(self) -> float:
        return self._amount_paid
    
    @property
    def payment_method(self) -> str:
        return self._payment_method
    
    @property
    def transaction_id(self) -> str:
        return self._transaction_id
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    # Setters
    @payment_id.setter
    def payment_id(self, value: int):
        self._payment_id = value
    
    @violation_id.setter
    def violation_id(self, value: int):
        if value > 0:
            self._violation_id = value
        else:
            raise ValueError("Violation ID must be positive")
    
    @payment_date.setter
    def payment_date(self, value: datetime):
        self._payment_date = value
    
    @amount_paid.setter
    def amount_paid(self, value: float):
        if value >= 0:
            self._amount_paid = value
        else:
            raise ValueError("Payment amount cannot be negative")
    
    @payment_method.setter
    def payment_method(self, value: str):
        if value in self.VALID_METHODS:
            self._payment_method = value
        else:
            raise ValueError(f"Payment method must be one of {self.VALID_METHODS}")
    
    @transaction_id.setter
    def transaction_id(self, value: str):
        self._transaction_id = value
    
    # Methods
    def generate_transaction_id(self) -> str:
        """
        Generate a unique transaction ID
        Format: TXN + timestamp
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"TXN{timestamp}"
    
    def is_online_payment(self) -> bool:
        """Check if payment was made online"""
        return self._payment_method == 'online'
    
    def is_cash_payment(self) -> bool:
        """Check if payment was made in cash"""
        return self._payment_method == 'cash'
    
    def to_dict(self) -> Dict:
        """Convert payment object to dictionary"""
        return {
            'payment_id': self._payment_id,
            'violation_id': self._violation_id,
            'payment_date': self._payment_date.strftime('%Y-%m-%d %H:%M:%S') if isinstance(self._payment_date, datetime) else str(self._payment_date),
            'amount_paid': self._amount_paid,
            'payment_method': self._payment_method,
            'transaction_id': self._transaction_id,
            'created_at': self._created_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(self._created_at, datetime) else str(self._created_at)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Payment':
        """
        Create Payment object from dictionary
        
        Args:
            data: Dictionary containing payment data
        Returns:
            Payment object
        """
        return cls(
            payment_id=data.get('payment_id'),
            violation_id=data.get('violation_id', 0),
            payment_date=data.get('payment_date'),
            amount_paid=data.get('amount_paid', 0.0),
            payment_method=data.get('payment_method', 'cash'),
            transaction_id=data.get('transaction_id', ''),
            created_at=data.get('created_at')
        )
    
    def __str__(self) -> str:
        """String representation of Payment"""
        return f"Payment(id={self._payment_id}, violation_id={self._violation_id}, amount={self._amount_paid}, method={self._payment_method})"
    
    def __repr__(self) -> str:
        """Developer representation of Payment"""
        return self.__str__()