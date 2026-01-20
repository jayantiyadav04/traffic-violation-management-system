"""
Violation Manager
Handles all violation-related business logic and database operations
"""

from typing import List, Optional, Dict
from datetime import datetime
import sys
sys.path.append('..')

from models.violation import Violation
from database.db_connection import get_db


class ViolationManager:
    """
    Manager class for violation operations
    Handles CRUD operations and business logic for violations
    """
    
    def __init__(self):
        """Initialize violation manager with database connection"""
        self.db = get_db()
    
    def create_violation(self, violation: Violation) -> Optional[int]:
        """
        Create a new violation record
        
        Args:
            violation: Violation object to create
        Returns:
            Violation ID if successful, None otherwise
        """
        query = """
            INSERT INTO violations 
            (vehicle_number, user_id, type_id, area_id, officer_id, 
             violation_date, fine_amount, status, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            violation.vehicle_number,
            violation.user_id,
            violation.type_id,
            violation.area_id,
            violation.officer_id,
            violation.violation_date.strftime('%Y-%m-%d %H:%M:%S'),
            violation.fine_amount,
            violation.status,
            violation.notes
        )
        
        if self.db.execute_query(query, params):
            violation_id = self.db.get_last_insert_id()
            return violation_id
        return None
    
    def get_violation_by_id(self, violation_id: int) -> Optional[Violation]:
        """
        Get violation by ID
        
        Args:
            violation_id: Violation ID to retrieve
        Returns:
            Violation object if found, None otherwise
        """
        query = """
            SELECT * FROM violations WHERE violation_id = %s
        """
        
        result = self.db.fetch_one(query, (violation_id,))
        
        if result:
            return Violation.from_dict(result)
        return None
    
    def get_all_violations(self, limit: int = 100) -> List[Dict]:
        """
        Get all violations with detailed information
        
        Args:
            limit: Maximum number of records to return
        Returns:
            List of violation dictionaries with joined data
        """
        query = """
            SELECT 
                v.violation_id,
                v.vehicle_number,
                u.full_name AS owner_name,
                vt.type_name,
                a.area_name,
                a.city,
                o.full_name AS officer_name,
                v.violation_date,
                v.fine_amount,
                v.status,
                v.notes
            FROM violations v
            LEFT JOIN users u ON v.user_id = u.user_id
            JOIN violation_types vt ON v.type_id = vt.type_id
            JOIN areas a ON v.area_id = a.area_id
            JOIN users o ON v.officer_id = o.user_id
            ORDER BY v.violation_date DESC
            LIMIT %s
        """
        
        return self.db.fetch_all(query, (limit,))
    
    def get_violations_by_vehicle(self, vehicle_number: str) -> List[Dict]:
        """
        Get all violations for a specific vehicle
        
        Args:
            vehicle_number: Vehicle registration number
        Returns:
            List of violations for the vehicle
        """
        query = """
            SELECT 
                v.violation_id,
                v.vehicle_number,
                vt.type_name,
                a.area_name,
                v.violation_date,
                v.fine_amount,
                v.status,
                p.payment_date,
                p.payment_method
            FROM violations v
            JOIN violation_types vt ON v.type_id = vt.type_id
            JOIN areas a ON v.area_id = a.area_id
            LEFT JOIN payments p ON v.violation_id = p.violation_id
            WHERE v.vehicle_number = %s
            ORDER BY v.violation_date DESC
        """
        
        return self.db.fetch_all(query, (vehicle_number.upper(),))
    
    def get_violations_by_user(self, user_id: int) -> List[Dict]:
        """
        Get all violations for a specific user
        
        Args:
            user_id: User ID
        Returns:
            List of user's violations
        """
        query = """
            SELECT 
                v.violation_id,
                v.vehicle_number,
                vt.type_name,
                a.area_name,
                v.violation_date,
                v.fine_amount,
                v.status
            FROM violations v
            JOIN violation_types vt ON v.type_id = vt.type_id
            JOIN areas a ON v.area_id = a.area_id
            WHERE v.user_id = %s
            ORDER BY v.violation_date DESC
        """
        
        return self.db.fetch_all(query, (user_id,))
    
    def get_unpaid_violations(self) -> List[Dict]:
        """
        Get all unpaid violations
        
        Returns:
            List of unpaid violations
        """
        query = """
            SELECT 
                v.violation_id,
                v.vehicle_number,
                u.full_name AS owner_name,
                vt.type_name,
                a.area_name,
                v.violation_date,
                v.fine_amount
            FROM violations v
            LEFT JOIN users u ON v.user_id = u.user_id
            JOIN violation_types vt ON v.type_id = vt.type_id
            JOIN areas a ON v.area_id = a.area_id
            WHERE v.status = 'unpaid'
            ORDER BY v.violation_date DESC
        """
        
        return self.db.fetch_all(query)
    
    def update_violation_status(self, violation_id: int, status: str) -> bool:
        """
        Update violation payment status
        
        Args:
            violation_id: Violation ID to update
            status: New status (paid/unpaid/disputed)
        Returns:
            True if successful, False otherwise
        """
        if status not in Violation.VALID_STATUSES:
            return False
        
        query = """
            UPDATE violations 
            SET status = %s
            WHERE violation_id = %s
        """
        
        return self.db.execute_query(query, (status, violation_id))
    
    def get_violation_types(self) -> List[Dict]:
        """
        Get all violation types
        
        Returns:
            List of violation types with base fines
        """
        query = """
            SELECT type_id, type_name, base_fine, description
            FROM violation_types
            ORDER BY type_name
        """
        
        return self.db.fetch_all(query)
    
    def get_areas(self) -> List[Dict]:
        """
        Get all areas/locations
        
        Returns:
            List of areas
        """
        query = """
            SELECT area_id, area_name, city
            FROM areas
            ORDER BY city, area_name
        """
        
        return self.db.fetch_all(query)
    
    def calculate_total_fines(self, user_id: Optional[int] = None) -> Dict:
        """
        Calculate total, paid, and unpaid fines
        
        Args:
            user_id: Optional user ID to filter by
        Returns:
            Dictionary with total, paid, and unpaid amounts
        """
        if user_id:
            query = """
                SELECT 
                    COUNT(*) as total_count,
                    SUM(fine_amount) as total_amount,
                    SUM(CASE WHEN status = 'paid' THEN fine_amount ELSE 0 END) as paid_amount,
                    SUM(CASE WHEN status = 'unpaid' THEN fine_amount ELSE 0 END) as unpaid_amount
                FROM violations
                WHERE user_id = %s
            """
            result = self.db.fetch_one(query, (user_id,))
        else:
            query = """
                SELECT 
                    COUNT(*) as total_count,
                    SUM(fine_amount) as total_amount,
                    SUM(CASE WHEN status = 'paid' THEN fine_amount ELSE 0 END) as paid_amount,
                    SUM(CASE WHEN status = 'unpaid' THEN fine_amount ELSE 0 END) as unpaid_amount
                FROM violations
            """
            result = self.db.fetch_one(query)
        
        if result:
            return {
                'total_count': result.get('total_count', 0),
                'total_amount': float(result.get('total_amount', 0) or 0),
                'paid_amount': float(result.get('paid_amount', 0) or 0),
                'unpaid_amount': float(result.get('unpaid_amount', 0) or 0)
            }
        return {
            'total_count': 0,
            'total_amount': 0.0,
            'paid_amount': 0.0,
            'unpaid_amount': 0.0
        }
    
    def search_violations(self, search_term: str) -> List[Dict]:
        """
        Search violations by vehicle number or owner name
        
        Args:
            search_term: Search term
        Returns:
            List of matching violations
        """
        query = """
            SELECT 
                v.violation_id,
                v.vehicle_number,
                u.full_name AS owner_name,
                vt.type_name,
                a.area_name,
                v.violation_date,
                v.fine_amount,
                v.status
            FROM violations v
            LEFT JOIN users u ON v.user_id = u.user_id
            JOIN violation_types vt ON v.type_id = vt.type_id
            JOIN areas a ON v.area_id = a.area_id
            WHERE v.vehicle_number LIKE %s OR u.full_name LIKE %s
            ORDER BY v.violation_date DESC
        """
        
        search_pattern = f"%{search_term}%"
        return self.db.fetch_all(query, (search_pattern, search_pattern))