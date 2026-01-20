"""
User Manager
Handles all user-related business logic and database operations
"""

from typing import List, Optional, Dict
from datetime import datetime
import sys
sys.path.append('..')

from models.user import User
from database.db_connection import get_db


class UserManager:
    """
    Manager class for user operations
    Handles CRUD operations and authentication for users
    """
    
    def __init__(self):
        """Initialize user manager with database connection"""
        self.db = get_db()
    
    def create_user(self, user: User) -> Optional[int]:
        """
        Create a new user account
        
        Args:
            user: User object to create
        Returns:
            User ID if successful, None otherwise
        """
        query = """
            INSERT INTO users 
            (username, password, full_name, role, email, phone)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        params = (
            user.username,
            user.password,  # In production, hash this password!
            user.full_name,
            user.role,
            user.email,
            user.phone
        )
        
        if self.db.execute_query(query, params):
            user_id = self.db.get_last_insert_id()
            return user_id
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User ID to retrieve
        Returns:
            User object if found, None otherwise
        """
        query = """
            SELECT * FROM users WHERE user_id = %s
        """
        
        result = self.db.fetch_one(query, (user_id,))
        
        if result:
            return User.from_dict(result)
        return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username
        
        Args:
            username: Username to search for
        Returns:
            User object if found, None otherwise
        """
        query = """
            SELECT * FROM users WHERE username = %s
        """
        
        result = self.db.fetch_one(query, (username,))
        
        if result:
            return User.from_dict(result)
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email
        
        Args:
            email: Email address to search for
        Returns:
            User object if found, None otherwise
        """
        query = """
            SELECT * FROM users WHERE email = %s
        """
        
        result = self.db.fetch_one(query, (email,))
        
        if result:
            return User.from_dict(result)
        return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username and password
        
        Args:
            username: Username
            password: Password (plain text - should be hashed in production)
        Returns:
            User object if authentication successful, None otherwise
        """
        user = self.get_user_by_username(username)
        
        if user and user.verify_password(password):
            return user
        return None
    
    def get_all_users(self, role: Optional[str] = None) -> List[Dict]:
        """
        Get all users or users by role
        
        Args:
            role: Optional role filter (admin/officer/citizen)
        Returns:
            List of user dictionaries
        """
        if role:
            query = """
                SELECT user_id, username, full_name, role, email, phone, created_at
                FROM users
                WHERE role = %s
                ORDER BY full_name
            """
            return self.db.fetch_all(query, (role,))
        else:
            query = """
                SELECT user_id, username, full_name, role, email, phone, created_at
                FROM users
                ORDER BY role, full_name
            """
            return self.db.fetch_all(query)
    
    def get_officers(self) -> List[Dict]:
        """
        Get all officers
        
        Returns:
            List of officer users
        """
        return self.get_all_users(role='officer')
    
    def get_citizens(self) -> List[Dict]:
        """
        Get all citizens
        
        Returns:
            List of citizen users
        """
        return self.get_all_users(role='citizen')
    
    def update_user(self, user_id: int, updates: Dict) -> bool:
        """
        Update user information
        
        Args:
            user_id: User ID to update
            updates: Dictionary of fields to update
        Returns:
            True if successful, False otherwise
        """
        # Build dynamic update query
        allowed_fields = ['full_name', 'email', 'phone', 'password']
        update_parts = []
        params = []
        
        for field, value in updates.items():
            if field in allowed_fields:
                update_parts.append(f"{field} = %s")
                params.append(value)
        
        if not update_parts:
            return False
        
        params.append(user_id)
        query = f"""
            UPDATE users 
            SET {', '.join(update_parts)}
            WHERE user_id = %s
        """
        
        return self.db.execute_query(query, tuple(params))
    
    def update_password(self, user_id: int, new_password: str) -> bool:
        """
        Update user password
        
        Args:
            user_id: User ID
            new_password: New password (should be hashed in production)
        Returns:
            True if successful, False otherwise
        """
        query = """
            UPDATE users 
            SET password = %s
            WHERE user_id = %s
        """
        
        return self.db.execute_query(query, (new_password, user_id))
    
    def delete_user(self, user_id: int) -> bool:
        """
        Delete a user account
        Note: This will set user_id to NULL in violations (ON DELETE SET NULL)
        
        Args:
            user_id: User ID to delete
        Returns:
            True if successful, False otherwise
        """
        query = """
            DELETE FROM users WHERE user_id = %s
        """
        
        return self.db.execute_query(query, (user_id,))
    
    def username_exists(self, username: str) -> bool:
        """
        Check if username already exists
        
        Args:
            username: Username to check
        Returns:
            True if exists, False otherwise
        """
        query = """
            SELECT COUNT(*) as count FROM users WHERE username = %s
        """
        
        result = self.db.fetch_one(query, (username,))
        return result and result.get('count', 0) > 0
    
    def email_exists(self, email: str) -> bool:
        """
        Check if email already exists
        
        Args:
            email: Email to check
        Returns:
            True if exists, False otherwise
        """
        query = """
            SELECT COUNT(*) as count FROM users WHERE email = %s
        """
        
        result = self.db.fetch_one(query, (email,))
        return result and result.get('count', 0) > 0
    
    def get_user_statistics(self, user_id: int) -> Dict:
        """
        Get statistics for a specific user (for citizens)
        
        Args:
            user_id: User ID
        Returns:
            Dictionary with user statistics
        """
        query = """
            SELECT 
                COUNT(*) as total_violations,
                SUM(fine_amount) as total_fines,
                SUM(CASE WHEN status = 'paid' THEN fine_amount ELSE 0 END) as paid_amount,
                SUM(CASE WHEN status = 'unpaid' THEN fine_amount ELSE 0 END) as unpaid_amount,
                COUNT(CASE WHEN status = 'paid' THEN 1 END) as paid_count,
                COUNT(CASE WHEN status = 'unpaid' THEN 1 END) as unpaid_count
            FROM violations
            WHERE user_id = %s
        """
        
        result = self.db.fetch_one(query, (user_id,))
        
        if result:
            return {
                'total_violations': result.get('total_violations', 0),
                'total_fines': float(result.get('total_fines', 0) or 0),
                'paid_amount': float(result.get('paid_amount', 0) or 0),
                'unpaid_amount': float(result.get('unpaid_amount', 0) or 0),
                'paid_count': result.get('paid_count', 0),
                'unpaid_count': result.get('unpaid_count', 0)
            }
        return {
            'total_violations': 0,
            'total_fines': 0.0,
            'paid_amount': 0.0,
            'unpaid_amount': 0.0,
            'paid_count': 0,
            'unpaid_count': 0
        }
    
    def search_users(self, search_term: str) -> List[Dict]:
        """
        Search users by name, username, or email
        
        Args:
            search_term: Search term
        Returns:
            List of matching users
        """
        query = """
            SELECT user_id, username, full_name, role, email, phone, created_at
            FROM users
            WHERE username LIKE %s 
               OR full_name LIKE %s 
               OR email LIKE %s
            ORDER BY full_name
        """
        
        search_pattern = f"%{search_term}%"
        return self.db.fetch_all(query, (search_pattern, search_pattern, search_pattern))
    
    def get_user_count_by_role(self) -> Dict:
        """
        Get count of users by role
        
        Returns:
            Dictionary with counts for each role
        """
        query = """
            SELECT 
                role,
                COUNT(*) as count
            FROM users
            GROUP BY role
        """
        
        results = self.db.fetch_all(query)
        
        counts = {'admin': 0, 'officer': 0, 'citizen': 0}
        for result in results:
            counts[result['role']] = result['count']
        
        return counts
    
    def verify_user_credentials(self, username: str, password: str) -> Optional[Dict]:
        """
        Verify user credentials and return user info (for login)
        
        Args:
            username: Username
            password: Password
        Returns:
            User dictionary if valid, None otherwise
        """
        user = self.authenticate_user(username, password)
        
        if user:
            return {
                'user_id': user.user_id,
                'username': user.username,
                'full_name': user.full_name,
                'role': user.role,
                'email': user.email
            }
        return None