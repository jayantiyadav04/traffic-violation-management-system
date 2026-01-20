"""
Validators Module
Input validation utilities for the Traffic Violation Management System
Location: backend/utils/validators.py
"""

import re
from datetime import datetime
from typing import Optional, Tuple


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


# ============================================
# Email Validation
# ============================================

def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"
    
    # Basic email regex pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return False, "Invalid email format"
    
    if len(email) > 100:
        return False, "Email too long (max 100 characters)"
    
    return True, None


# ============================================
# Phone Number Validation
# ============================================

def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    """
    Validate phone number (Indian format)
    
    Args:
        phone: Phone number to validate
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not phone:
        return False, "Phone number is required"
    
    # Remove spaces, hyphens, and parentheses
    cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check if it contains only digits and optional + at start
    if not re.match(r'^\+?\d+$', cleaned_phone):
        return False, "Phone number must contain only digits"
    
    # Check length (10 digits for India, or 12-13 with country code)
    if len(cleaned_phone) not in [10, 12, 13]:
        return False, "Phone number must be 10 digits (or 12-13 with country code)"
    
    return True, None


# ============================================
# Vehicle Number Validation
# ============================================

def validate_vehicle_number(vehicle_number: str) -> Tuple[bool, Optional[str]]:
    """
    Validate vehicle registration number (Indian format)
    Format: XX00XX0000 or XX-00-XX-0000
    Example: KA01AB1234 or KA-01-AB-1234
    
    Args:
        vehicle_number: Vehicle number to validate
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not vehicle_number:
        return False, "Vehicle number is required"
    
    # Remove spaces and hyphens
    cleaned = re.sub(r'[\s\-]', '', vehicle_number.upper())
    
    # Indian vehicle number pattern: 2 letters + 2 digits + 1-2 letters + 4 digits
    pattern = r'^[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}$'
    
    if not re.match(pattern, cleaned):
        return False, "Invalid vehicle number format (e.g., KA01AB1234)"
    
    if len(cleaned) < 9 or len(cleaned) > 10:
        return False, "Vehicle number must be 9-10 characters"
    
    return True, None


# ============================================
# Password Validation
# ============================================

def validate_password(password: str, min_length: int = 6) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength
    
    Args:
        password: Password to validate
        min_length: Minimum required length
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters"
    
    if len(password) > 255:
        return False, "Password too long (max 255 characters)"
    
    # Optional: Check for password strength
    # has_upper = any(c.isupper() for c in password)
    # has_lower = any(c.islower() for c in password)
    # has_digit = any(c.isdigit() for c in password)
    
    # if not (has_upper and has_lower and has_digit):
    #     return False, "Password must contain uppercase, lowercase, and digit"
    
    return True, None


# ============================================
# Username Validation
# ============================================

def validate_username(username: str) -> Tuple[bool, Optional[str]]:
    """
    Validate username
    
    Args:
        username: Username to validate
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not username:
        return False, "Username is required"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 50:
        return False, "Username too long (max 50 characters)"
    
    # Only alphanumeric and underscore
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscore"
    
    return True, None


# ============================================
# Amount/Fine Validation
# ============================================

def validate_amount(amount: float, min_amount: float = 0.0, max_amount: float = 100000.0) -> Tuple[bool, Optional[str]]:
    """
    Validate monetary amount
    
    Args:
        amount: Amount to validate
        min_amount: Minimum allowed amount
        max_amount: Maximum allowed amount
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return False, "Invalid amount format"
    
    if amount < min_amount:
        return False, f"Amount must be at least ₹{min_amount}"
    
    if amount > max_amount:
        return False, f"Amount cannot exceed ₹{max_amount}"
    
    # Check for reasonable decimal places (max 2)
    if round(amount, 2) != amount:
        return False, "Amount can have maximum 2 decimal places"
    
    return True, None


# ============================================
# Date Validation
# ============================================

def validate_date(date_string: str, date_format: str = '%Y-%m-%d') -> Tuple[bool, Optional[str]]:
    """
    Validate date string
    
    Args:
        date_string: Date string to validate
        date_format: Expected date format
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not date_string:
        return False, "Date is required"
    
    try:
        datetime.strptime(date_string, date_format)
        return True, None
    except ValueError:
        return False, f"Invalid date format (expected: {date_format})"


def validate_datetime(datetime_string: str, datetime_format: str = '%Y-%m-%d %H:%M:%S') -> Tuple[bool, Optional[str]]:
    """
    Validate datetime string
    
    Args:
        datetime_string: Datetime string to validate
        datetime_format: Expected datetime format
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not datetime_string:
        return False, "Date and time is required"
    
    try:
        datetime.strptime(datetime_string, datetime_format)
        return True, None
    except ValueError:
        return False, f"Invalid datetime format (expected: {datetime_format})"


def validate_future_date(date_obj: datetime) -> Tuple[bool, Optional[str]]:
    """
    Check if date is not in the future
    
    Args:
        date_obj: Date object to validate
    Returns:
        Tuple of (is_valid, error_message)
    """
    if date_obj > datetime.now():
        return False, "Date cannot be in the future"
    
    return True, None


# ============================================
# Text Field Validation
# ============================================

def validate_name(name: str, min_length: int = 2, max_length: int = 100) -> Tuple[bool, Optional[str]]:
    """
    Validate person name
    
    Args:
        name: Name to validate
        min_length: Minimum name length
        max_length: Maximum name length
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, "Name is required"
    
    name = name.strip()
    
    if len(name) < min_length:
        return False, f"Name must be at least {min_length} characters"
    
    if len(name) > max_length:
        return False, f"Name too long (max {max_length} characters)"
    
    # Only letters, spaces, and common punctuation
    if not re.match(r"^[a-zA-Z\s\.\-']+$", name):
        return False, "Name can only contain letters, spaces, and basic punctuation"
    
    return True, None


def validate_text_field(text: str, field_name: str, min_length: int = 0, max_length: int = 255, required: bool = True) -> Tuple[bool, Optional[str]]:
    """
    General text field validation
    
    Args:
        text: Text to validate
        field_name: Name of the field (for error messages)
        min_length: Minimum length
        max_length: Maximum length
        required: Whether field is required
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text or not text.strip():
        if required:
            return False, f"{field_name} is required"
        else:
            return True, None
    
    text = text.strip()
    
    if len(text) < min_length:
        return False, f"{field_name} must be at least {min_length} characters"
    
    if len(text) > max_length:
        return False, f"{field_name} too long (max {max_length} characters)"
    
    return True, None


# ============================================
# Role Validation
# ============================================

def validate_role(role: str) -> Tuple[bool, Optional[str]]:
    """
    Validate user role
    
    Args:
        role: Role to validate
    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_roles = ['admin', 'officer', 'citizen']
    
    if not role:
        return False, "Role is required"
    
    if role.lower() not in valid_roles:
        return False, f"Invalid role. Must be one of: {', '.join(valid_roles)}"
    
    return True, None


# ============================================
# Payment Method Validation
# ============================================

def validate_payment_method(method: str) -> Tuple[bool, Optional[str]]:
    """
    Validate payment method
    
    Args:
        method: Payment method to validate
    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_methods = ['cash', 'card', 'online', 'cheque']
    
    if not method:
        return False, "Payment method is required"
    
    if method.lower() not in valid_methods:
        return False, f"Invalid payment method. Must be one of: {', '.join(valid_methods)}"
    
    return True, None


# ============================================
# Status Validation
# ============================================

def validate_violation_status(status: str) -> Tuple[bool, Optional[str]]:
    """
    Validate violation status
    
    Args:
        status: Status to validate
    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_statuses = ['unpaid', 'paid', 'disputed']
    
    if not status:
        return False, "Status is required"
    
    if status.lower() not in valid_statuses:
        return False, f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
    
    return True, None


# ============================================
# ID Validation
# ============================================

def validate_id(id_value: int, field_name: str = "ID") -> Tuple[bool, Optional[str]]:
    """
    Validate ID (must be positive integer)
    
    Args:
        id_value: ID to validate
        field_name: Name of the field
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        id_value = int(id_value)
    except (ValueError, TypeError):
        return False, f"{field_name} must be a number"
    
    if id_value <= 0:
        return False, f"{field_name} must be a positive number"
    
    return True, None


# ============================================
# Comprehensive Validation Functions
# ============================================

def validate_user_input(data: dict) -> Tuple[bool, dict]:
    """
    Validate user registration/update input
    
    Args:
        data: Dictionary with user data
    Returns:
        Tuple of (is_valid, errors_dict)
    """
    errors = {}
    
    # Validate username
    if 'username' in data:
        is_valid, error = validate_username(data['username'])
        if not is_valid:
            errors['username'] = error
    
    # Validate password
    if 'password' in data:
        is_valid, error = validate_password(data['password'])
        if not is_valid:
            errors['password'] = error
    
    # Validate email
    if 'email' in data:
        is_valid, error = validate_email(data['email'])
        if not is_valid:
            errors['email'] = error
    
    # Validate phone
    if 'phone' in data and data['phone']:
        is_valid, error = validate_phone(data['phone'])
        if not is_valid:
            errors['phone'] = error
    
    # Validate full name
    if 'full_name' in data:
        is_valid, error = validate_name(data['full_name'])
        if not is_valid:
            errors['full_name'] = error
    
    # Validate role
    if 'role' in data:
        is_valid, error = validate_role(data['role'])
        if not is_valid:
            errors['role'] = error
    
    return len(errors) == 0, errors


def validate_violation_input(data: dict) -> Tuple[bool, dict]:
    """
    Validate violation registration input
    
    Args:
        data: Dictionary with violation data
    Returns:
        Tuple of (is_valid, errors_dict)
    """
    errors = {}
    
    # Validate vehicle number
    if 'vehicle_number' in data:
        is_valid, error = validate_vehicle_number(data['vehicle_number'])
        if not is_valid:
            errors['vehicle_number'] = error
    else:
        errors['vehicle_number'] = "Vehicle number is required"
    
    # Validate type_id
    if 'type_id' in data:
        is_valid, error = validate_id(data['type_id'], "Violation type")
        if not is_valid:
            errors['type_id'] = error
    else:
        errors['type_id'] = "Violation type is required"
    
    # Validate area_id
    if 'area_id' in data:
        is_valid, error = validate_id(data['area_id'], "Area")
        if not is_valid:
            errors['area_id'] = error
    else:
        errors['area_id'] = "Area is required"
    
    # Validate fine amount
    if 'fine_amount' in data:
        is_valid, error = validate_amount(data['fine_amount'])
        if not is_valid:
            errors['fine_amount'] = error
    else:
        errors['fine_amount'] = "Fine amount is required"
    
    return len(errors) == 0, errors


def validate_payment_input(data: dict) -> Tuple[bool, dict]:
    """
    Validate payment input
    
    Args:
        data: Dictionary with payment data
    Returns:
        Tuple of (is_valid, errors_dict)
    """
    errors = {}
    
    # Validate violation_id
    if 'violation_id' in data:
        is_valid, error = validate_id(data['violation_id'], "Violation ID")
        if not is_valid:
            errors['violation_id'] = error
    else:
        errors['violation_id'] = "Violation ID is required"
    
    # Validate amount
    if 'amount_paid' in data:
        is_valid, error = validate_amount(data['amount_paid'])
        if not is_valid:
            errors['amount_paid'] = error
    else:
        errors['amount_paid'] = "Payment amount is required"
    
    # Validate payment method
    if 'payment_method' in data:
        is_valid, error = validate_payment_method(data['payment_method'])
        if not is_valid:
            errors['payment_method'] = error
    else:
        errors['payment_method'] = "Payment method is required"
    
    return len(errors) == 0, errors