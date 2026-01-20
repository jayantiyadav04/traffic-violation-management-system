"""
Violation Model
Represents a traffic violation record
"""

from typing import Optional, Dict
from datetime import datetime
from decimal import Decimal


class Violation:
    """
    Violation class representing a traffic violation
    """
    
    VALID_STATUSES = ['unpaid', 'paid', 'disputed']
    
    def __init__(
        self,
        violation_id: Optional[int] = None,
        vehicle_number: str = '',
        user_id: Optional[int] = None,
        type_id: int = 0,
        area_id: int = 0,
        officer_id: int = 0,
        violation_date: Optional[datetime] = None,
        fine_amount: float = 0.0,
        status: str = 'unpaid',
        notes: str = '',
        created_at: Optional[datetime] = None
    ):
        """
        Initialize Violation object
        
        Args:
            violation_id: Unique violation identifier
            vehicle_number: Vehicle registration number
            user_id: Owner user ID (can be null)
            type_id: Violation type ID
            area_id: Area/location ID
            officer_id: Reporting officer's user ID
            violation_date: Date and time of violation
            fine_amount: Fine amount for this violation
            status: Payment status (unpaid/paid/disputed)
            notes: Additional notes
            created_at: Record creation timestamp
        """
        self._violation_id = violation_id
        self._vehicle_number = vehicle_number.upper()
        self._user_id = user_id
        self._type_id = type_id
        self._area_id = area_id
        self._officer_id = officer_id
        self._violation_date = violation_date or datetime.now()
        self._fine_amount = float(fine_amount)
        self._status = status if status in self.VALID_STATUSES else 'unpaid'
        self._notes = notes
        self._created_at = created_at or datetime.now()
    
    # Getters
    @property
    def violation_id(self) -> Optional[int]:
        return self._violation_id
    
    @property
    def vehicle_number(self) -> str:
        return self._vehicle_number
    
    @property
    def user_id(self) -> Optional[int]:
        return self._user_id
    
    @property
    def type_id(self) -> int:
        return self._type_id
    
    @property
    def area_id(self) -> int:
        return self._area_id
    
    @property
    def officer_id(self) -> int:
        return self._officer_id
    
    @property
    def violation_date(self) -> datetime:
        return self._violation_date
    
    @property
    def fine_amount(self) -> float:
        return self._fine_amount
    
    @property
    def status(self) -> str:
        return self._status
    
    @property
    def notes(self) -> str:
        return self._notes
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    # Setters
    @violation_id.setter
    def violation_id(self, value: int):
        self._violation_id = value
    
    @vehicle_number.setter
    def vehicle_number(self, value: str):
        if value and len(value) >= 4:
            self._vehicle_number = value.upper()
        else:
            raise ValueError("Vehicle number must be at least 4 characters")
    
    @user_id.setter
    def user_id(self, value: Optional[int]):
        self._user_id = value
    
    @type_id.setter
    def type_id(self, value: int):
        if value > 0:
            self._type_id = value
        else:
            raise ValueError("Type ID must be positive")
    
    @area_id.setter
    def area_id(self, value: int):
        if value > 0:
            self._area_id = value
        else:
            raise ValueError("Area ID must be positive")
    
    @officer_id.setter
    def officer_id(self, value: int):
        if value > 0:
            self._officer_id = value
        else:
            raise ValueError("Officer ID must be positive")
    
    @violation_date.setter
    def violation_date(self, value: datetime):
        self._violation_date = value
    
    @fine_amount.setter
    def fine_amount(self, value: float):
        if value >= 0:
            self._fine_amount = value
        else:
            raise ValueError("Fine amount cannot be negative")
    
    @status.setter
    def status(self, value: str):
        if value in self.VALID_STATUSES:
            self._status = value
        else:
            raise ValueError(f"Status must be one of {self.VALID_STATUSES}")
    
    @notes.setter
    def notes(self, value: str):
        self._notes = value
    
    # Methods
    def is_paid(self) -> bool:
        """Check if violation is paid"""
        return self._status == 'paid'
    
    def is_unpaid(self) -> bool:
        """Check if violation is unpaid"""
        return self._status == 'unpaid'
    
    def is_disputed(self) -> bool:
        """Check if violation is disputed"""
        return self._status == 'disputed'
    
    def mark_as_paid(self):
        """Mark violation as paid"""
        self._status = 'paid'
    
    def mark_as_disputed(self):
        """Mark violation as disputed"""
        self._status = 'disputed'
    
    def calculate_late_fee(self, days_late: int, late_fee_percent: float = 0.05) -> float:
        """
        Calculate late fee based on days overdue
        
        Args:
            days_late: Number of days past due date
            late_fee_percent: Percentage of fine to add per day
        Returns:
            Additional late fee amount
        """
        if days_late > 0:
            return self._fine_amount * late_fee_percent * days_late
        return 0.0
    
    def to_dict(self) -> Dict:
        """Convert violation object to dictionary"""
        return {
            'violation_id': self._violation_id,
            'vehicle_number': self._vehicle_number,
            'user_id': self._user_id,
            'type_id': self._type_id,
            'area_id': self._area_id,
            'officer_id': self._officer_id,
            'violation_date': self._violation_date.strftime('%Y-%m-%d %H:%M:%S') if isinstance(self._violation_date, datetime) else str(self._violation_date),
            'fine_amount': self._fine_amount,
            'status': self._status,
            'notes': self._notes,
            'created_at': self._created_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(self._created_at, datetime) else str(self._created_at)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Violation':
        """
        Create Violation object from dictionary
        
        Args:
            data: Dictionary containing violation data
        Returns:
            Violation object
        """
        return cls(
            violation_id=data.get('violation_id'),
            vehicle_number=data.get('vehicle_number', ''),
            user_id=data.get('user_id'),
            type_id=data.get('type_id', 0),
            area_id=data.get('area_id', 0),
            officer_id=data.get('officer_id', 0),
            violation_date=data.get('violation_date'),
            fine_amount=data.get('fine_amount', 0.0),
            status=data.get('status', 'unpaid'),
            notes=data.get('notes', ''),
            created_at=data.get('created_at')
        )
    
    def __str__(self) -> str:
        """String representation of Violation"""
        return f"Violation(id={self._violation_id}, vehicle={self._vehicle_number}, amount={self._fine_amount}, status={self._status})"
    
    def __repr__(self) -> str:
        """Developer representation of Violation"""
        return self.__str__()