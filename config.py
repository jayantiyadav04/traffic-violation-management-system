# config.py
"""
Configuration settings for Traffic Violation Management System
"""

import os
from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).resolve().parent

# Database Configuration
DATABASE_CONFIG = {
    'type': os.getenv('DB_TYPE', 'sqlite'),  # 'sqlite' or 'mysql'
    'sqlite': {
        'database': os.getenv('SQLITE_DB', 'traffic_violations.db')
    },
    'mysql': {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'traffic_violation_db'),
        'port': int(os.getenv('DB_PORT', '3306'))
    }
}

# Application Configuration
APP_CONFIG = {
    'host': os.getenv('APP_HOST', '0.0.0.0'),
    'port': int(os.getenv('APP_PORT', '5000')),
    'debug': os.getenv('DEBUG', 'True').lower() == 'true'
}

# Session Configuration
SESSION_CONFIG = {
    'secret_key': os.getenv('SECRET_KEY', 'your-secret-key-here-change-in-production'),
    'session_lifetime': 3600  # 1 hour in seconds
}

# File Upload Configuration
UPLOAD_CONFIG = {
    'upload_folder': os.path.join(BASE_DIR, 'uploads'),
    'allowed_extensions': {'png', 'jpg', 'jpeg', 'pdf'},
    'max_file_size': 5 * 1024 * 1024  # 5 MB
}

# Pagination Configuration
PAGINATION_CONFIG = {
    'items_per_page': 20,
    'max_items_per_page': 100
}

# Email Configuration (for future implementation)
EMAIL_CONFIG = {
    'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(os.getenv('SMTP_PORT', '587')),
    'sender_email': os.getenv('SENDER_EMAIL', ''),
    'sender_password': os.getenv('SENDER_PASSWORD', ''),
    'use_tls': True
}

# Fine Calculation Rules
FINE_RULES = {
    'late_fee_percentage': 0.05,  # 5% per day
    'max_late_fee_days': 30,  # Maximum days for late fee calculation
    'grace_period_days': 7  # Days before late fee applies
}

# Analytics Configuration
ANALYTICS_CONFIG = {
    'default_months': 6,  # Default months for trend analysis
    'default_top_count': 10  # Default count for top N queries
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    'file': os.path.join(BASE_DIR, 'logs', 'app.log'),
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

# Security Configuration
SECURITY_CONFIG = {
    'password_min_length': 6,
    'max_login_attempts': 5,
    'lockout_duration': 900,  # 15 minutes in seconds
    'require_password_change_days': 90
}
