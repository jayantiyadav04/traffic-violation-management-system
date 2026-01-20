"""
User Model
Represents a user in the system (Admin, Officer, Citizen)
"""

from typing import Optional, Dict
from datetime import datetime


class User:
    """
    User class representing system users
    Supports three roles: admin, officer, citizen
    """
    
    VALID_ROLES = ['admin', 'officer', 'citizen']
    
    def __init__(
        self,
        user_id: Optional[int] = None,
        username: str = '',
        password: str = '',
        full_name: str = '',
        role: str = 'citizen',
        email: str = '',
        phone: str = '',
        created_at: Optional[datetime] = None
    ):
        """
        Initialize User object
        
        Args:
            user_id: Unique user identifier
            username: Login username
            password: User password (should be hashed in production)
            full_name: Full name of the user
            role: User role (admin/officer/citizen)
            email: User email address
            phone: Contact phone number
            created_at: Account creation timestamp
        """
        self._user_id = user_id
        self._username = username
        self._password = password
        self._full_name = full_name
        self._role = role if role in self.VALID_ROLES else 'citizen'
        self._email = email
        self._phone = phone
        self._created_at = created_at or datetime.now()
    
    # Getters
    @property
    def user_id(self) -> Optional[int]:
        return self._user_id
    
    @property
    def username(self) -> str:
        return self._username
    
    @property
    def password(self) -> str:
        return self._password
    
    @property
    def full_name(self) -> str:
        return self._full_name
    
    @property
    def role(self) -> str:
        return self._role
    
    @property
    def email(self) -> str:
        return self._email
    
    @property
    def phone(self) -> str:
        return self._phone
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    # Setters
    @user_id.setter
    def user_id(self, value: int):
        self._user_id = value
    
    @username.setter
    def username(self, value: str):
        if value and len(value) >= 3:
            self._username = value
        else:
            raise ValueError("Username must be at least 3 characters")
    
    @password.setter
    def password(self, value: str):
        if value and len(value) >= 6:
            self._password = value
        else:
            raise ValueError("Password must be at least 6 characters")
    
    @full_name.setter
    def full_name(self, value: str):
        if value and len(value) >= 2:
            self._full_name = value
        else:
            raise ValueError("Full name must be at least 2 characters")
    
    @role.setter
    def role(self, value: str):
        if value in self.VALID_ROLES:
            self._role = value
        else:
            raise ValueError(f"Role must be one of {self.VALID_ROLES}")
    
    @email.setter
    def email(self, value: str):
        if '@' in value and '.' in value:
            self._email = value
        else:
            raise ValueError("Invalid email format")
    
    @phone.setter
    def phone(self, value: str):
        self._phone = value
    
    # Methods
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self._role == 'admin'
    
    def is_officer(self) -> bool:
        """Check if user is officer"""
        return self._role == 'officer'
    
    def is_citizen(self) -> bool:
        """Check if user is citizen"""
        return self._role == 'citizen'
    
    def verify_password(self, password: str) -> bool:
        """
        Verify user password
        In production, use proper password hashing (bcrypt, etc.)
        """
        return self._password == password
    
    def to_dict(self) -> Dict:
        """Convert user object to dictionary"""
        return {
            'user_id': self._user_id,
            'username': self._username,
            'full_name': self._full_name,
            'role': self._role,
            'email': self._email,
            'phone': self._phone,
            'created_at': self._created_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(self._created_at, datetime) else str(self._created_at)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """
        Create User object from dictionary
        
        Args:
            data: Dictionary containing user data
        Returns:
            User object
        """
        return cls(
            user_id=data.get('user_id'),
            username=data.get('username', ''),
            password=data.get('password', ''),
            full_name=data.get('full_name', ''),
            role=data.get('role', 'citizen'),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            created_at=data.get('created_at')
        )
    
    def __str__(self) -> str:
        """String representation of User"""
        return f"User(id={self._user_id}, username={self._username}, role={self._role})"
    
    def __repr__(self) -> str:
        """Developer representation of User"""
        return self.__str__()