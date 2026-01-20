"""
Payment Manager
Handles all payment-related business logic and database operations
"""

from typing import List, Optional, Dict
from datetime import datetime
import sys
sys.path.append('..')

from models.payment import Payment
from database.db_connection import get_db


class PaymentManager:
    """
    Manager class for payment operations
    Handles CRUD operations and payment processing
    """
    
    def __init__(self):
        """Initialize payment manager with database connection"""
        self.db = get_db()
    
    def create_payment(self, payment: Payment) -> Optional[int]:
        """
        Record a new payment
        
        Args:
            payment: Payment object to create
        Returns:
            Payment ID if successful, None otherwise
        """
        # Start transaction
        try:
            # Insert payment record
            query = """
                INSERT INTO payments 
                (violation_id, payment_date, amount_paid, payment_method, transaction_id)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            params = (
                payment.violation_id,
                payment.payment_date.strftime('%Y-%m-%d %H:%M:%S'),
                payment.amount_paid,
                payment.payment_method,
                payment.transaction_id
            )
            
            if self.db.execute_query(query, params):
                payment_id = self.db.get_last_insert_id()
                
                # Update violation status to paid
                update_query = """
                    UPDATE violations 
                    SET status = 'paid'
                    WHERE violation_id = %s
                """
                
                if self.db.execute_query(update_query, (payment.violation_id,)):
                    return payment_id
            
            return None
            
        except Exception as e:
            print(f"Error creating payment: {e}")
            return None
    
    def get_payment_by_id(self, payment_id: int) -> Optional[Payment]:
        """
        Get payment by ID
        
        Args:
            payment_id: Payment ID to retrieve
        Returns:
            Payment object if found, None otherwise
        """
        query = """
            SELECT * FROM payments WHERE payment_id = %s
        """
        
        result = self.db.fetch_one(query, (payment_id,))
        
        if result:
            return Payment.from_dict(result)
        return None
    
    def get_payment_by_violation(self, violation_id: int) -> Optional[Payment]:
        """
        Get payment for a specific violation
        
        Args:
            violation_id: Violation ID
        Returns:
            Payment object if found, None otherwise
        """
        query = """
            SELECT * FROM payments 
            WHERE violation_id = %s
            ORDER BY payment_date DESC
            LIMIT 1
        """
        
        result = self.db.fetch_one(query, (violation_id,))
        
        if result:
            return Payment.from_dict(result)
        return None
    
    def get_all_payments(self, limit: int = 100) -> List[Dict]:
        """
        Get all payments with violation details
        
        Args:
            limit: Maximum number of records to return
        Returns:
            List of payment dictionaries with joined data
        """
        query = """
            SELECT 
                p.payment_id,
                p.violation_id,
                v.vehicle_number,
                u.full_name AS owner_name,
                p.payment_date,
                p.amount_paid,
                p.payment_method,
                p.transaction_id,
                vt.type_name
            FROM payments p
            JOIN violations v ON p.violation_id = v.violation_id
            LEFT JOIN users u ON v.user_id = u.user_id
            JOIN violation_types vt ON v.type_id = vt.type_id
            ORDER BY p.payment_date DESC
            LIMIT %s
        """
        
        return self.db.fetch_all(query, (limit,))
    
    def get_payments_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Get payments within a date range
        
        Args:
            start_date: Start date
            end_date: End date
        Returns:
            List of payments in the date range
        """
        query = """
            SELECT 
                p.payment_id,
                p.violation_id,
                v.vehicle_number,
                p.payment_date,
                p.amount_paid,
                p.payment_method,
                p.transaction_id
            FROM payments p
            JOIN violations v ON p.violation_id = v.violation_id
            WHERE p.payment_date BETWEEN %s AND %s
            ORDER BY p.payment_date DESC
        """
        
        return self.db.fetch_all(query, (
            start_date.strftime('%Y-%m-%d %H:%M:%S'),
            end_date.strftime('%Y-%m-%d %H:%M:%S')
        ))
    
    def get_payments_by_method(self, payment_method: str) -> List[Dict]:
        """
        Get all payments by payment method
        
        Args:
            payment_method: Payment method (cash/card/online/cheque)
        Returns:
            List of payments with specified method
        """
        query = """
            SELECT 
                p.payment_id,
                p.violation_id,
                v.vehicle_number,
                p.payment_date,
                p.amount_paid,
                p.payment_method,
                p.transaction_id
            FROM payments p
            JOIN violations v ON p.violation_id = v.violation_id
            WHERE p.payment_method = %s
            ORDER BY p.payment_date DESC
        """
        
        return self.db.fetch_all(query, (payment_method,))
    
    def get_daily_collections(self, days: int = 30) -> List[Dict]:
        """
        Get daily collection totals
        
        Args:
            days: Number of days to analyze
        Returns:
            List of daily collection amounts
        """
        query = """
            SELECT 
                DATE(payment_date) as date,
                COUNT(*) as payment_count,
                SUM(amount_paid) as total_collected,
                ROUND(AVG(amount_paid), 2) as avg_amount
            FROM payments
            WHERE payment_date >= date('now', '-' || %s || ' days')
            GROUP BY DATE(payment_date)
            ORDER BY date DESC
        """
        
        return self.db.fetch_all(query, (days,))
    
    def get_payment_method_distribution(self) -> List[Dict]:
        """
        Get distribution of payments by method
        
        Returns:
            List with counts and totals by payment method
        """
        query = """
            SELECT 
                payment_method,
                COUNT(*) as count,
                SUM(amount_paid) as total_amount,
                ROUND(AVG(amount_paid), 2) as avg_amount
            FROM payments
            GROUP BY payment_method
            ORDER BY total_amount DESC
        """
        
        return self.db.fetch_all(query)
    
    def calculate_total_collections(self, start_date: Optional[datetime] = None, 
                                   end_date: Optional[datetime] = None) -> Dict:
        """
        Calculate total collection statistics
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
        Returns:
            Dictionary with collection statistics
        """
        if start_date and end_date:
            query = """
                SELECT 
                    COUNT(*) as total_payments,
                    SUM(amount_paid) as total_collected,
                    ROUND(AVG(amount_paid), 2) as avg_payment,
                    MIN(amount_paid) as min_payment,
                    MAX(amount_paid) as max_payment
                FROM payments
                WHERE payment_date BETWEEN %s AND %s
            """
            result = self.db.fetch_one(query, (
                start_date.strftime('%Y-%m-%d %H:%M:%S'),
                end_date.strftime('%Y-%m-%d %H:%M:%S')
            ))
        else:
            query = """
                SELECT 
                    COUNT(*) as total_payments,
                    SUM(amount_paid) as total_collected,
                    ROUND(AVG(amount_paid), 2) as avg_payment,
                    MIN(amount_paid) as min_payment,
                    MAX(amount_paid) as max_payment
                FROM payments
            """
            result = self.db.fetch_one(query)
        
        if result:
            return {
                'total_payments': result.get('total_payments', 0),
                'total_collected': float(result.get('total_collected', 0) or 0),
                'avg_payment': float(result.get('avg_payment', 0) or 0),
                'min_payment': float(result.get('min_payment', 0) or 0),
                'max_payment': float(result.get('max_payment', 0) or 0)
            }
        return {
            'total_payments': 0,
            'total_collected': 0.0,
            'avg_payment': 0.0,
            'min_payment': 0.0,
            'max_payment': 0.0
        }
    
    def process_payment(self, violation_id: int, amount: float, 
                       payment_method: str = 'cash') -> Optional[int]:
        """
        Process a payment for a violation
        
        Args:
            violation_id: Violation ID to pay
            amount: Amount being paid
            payment_method: Method of payment
        Returns:
            Payment ID if successful, None otherwise
        """
        # Verify violation exists and get fine amount
        check_query = """
            SELECT violation_id, fine_amount, status 
            FROM violations 
            WHERE violation_id = %s
        """
        
        violation = self.db.fetch_one(check_query, (violation_id,))
        
        if not violation:
            print("Violation not found")
            return None
        
        if violation['status'] == 'paid':
            print("Violation already paid")
            return None
        
        # Create payment object
        payment = Payment(
            violation_id=violation_id,
            payment_date=datetime.now(),
            amount_paid=amount,
            payment_method=payment_method,
            transaction_id=self._generate_transaction_id()
        )
        
        return self.create_payment(payment)
    
    def _generate_transaction_id(self) -> str:
        """
        Generate a unique transaction ID
        
        Returns:
            Transaction ID string
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"TXN{timestamp}"
    
    def get_recent_payments(self, limit: int = 10) -> List[Dict]:
        """
        Get most recent payments
        
        Args:
            limit: Number of payments to return
        Returns:
            List of recent payments
        """
        query = """
            SELECT 
                p.payment_id,
                p.violation_id,
                v.vehicle_number,
                u.full_name AS owner_name,
                p.payment_date,
                p.amount_paid,
                p.payment_method,
                p.transaction_id
            FROM payments p
            JOIN violations v ON p.violation_id = v.violation_id
            LEFT JOIN users u ON v.user_id = u.user_id
            ORDER BY p.payment_date DESC
            LIMIT %s
        """
        
        return self.db.fetch_all(query, (limit,))
    
    def verify_transaction(self, transaction_id: str) -> Optional[Dict]:
        """
        Verify a payment transaction
        
        Args:
            transaction_id: Transaction ID to verify
        Returns:
            Payment details if found, None otherwise
        """
        query = """
            SELECT 
                p.*,
                v.vehicle_number,
                v.fine_amount
            FROM payments p
            JOIN violations v ON p.violation_id = v.violation_id
            WHERE p.transaction_id = %s
        """
        
        return self.db.fetch_one(query, (transaction_id,))
    
    def get_payment_history_for_user(self, user_id: int) -> List[Dict]:
        """
        Get payment history for a specific user
        
        Args:
            user_id: User ID
        Returns:
            List of user's payments
        """
        query = """
            SELECT 
                p.payment_id,
                p.violation_id,
                v.vehicle_number,
                vt.type_name,
                p.payment_date,
                p.amount_paid,
                p.payment_method,
                p.transaction_id
            FROM payments p
            JOIN violations v ON p.violation_id = v.violation_id
            JOIN violation_types vt ON v.type_id = vt.type_id
            WHERE v.user_id = %s
            ORDER BY p.payment_date DESC
        """
        
        return self.db.fetch_all(query, (user_id,))
    
    def get_monthly_collections(self, months: int = 12) -> List[Dict]:
        """
        Get monthly collection totals
        
        Args:
            months: Number of months to analyze
        Returns:
            List of monthly collection amounts
        """
        query = """
            SELECT 
                strftime('%Y-%m', payment_date) as month,
                COUNT(*) as payment_count,
                SUM(amount_paid) as total_collected,
                ROUND(AVG(amount_paid), 2) as avg_amount
            FROM payments
            WHERE payment_date >= date('now', '-' || %s || ' months')
            GROUP BY strftime('%Y-%m', payment_date)
            ORDER BY month DESC
        """
        
        return self.db.fetch_all(query, (months,))
    
    def refund_payment(self, payment_id: int) -> bool:
        """
        Process a payment refund (deletes payment and updates violation status)
        
        Args:
            payment_id: Payment ID to refund
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get payment details
            payment = self.get_payment_by_id(payment_id)
            
            if not payment:
                return False
            
            # Delete payment record
            delete_query = "DELETE FROM payments WHERE payment_id = %s"
            if not self.db.execute_query(delete_query, (payment_id,)):
                return False
            
            # Update violation status back to unpaid
            update_query = """
                UPDATE violations 
                SET status = 'unpaid'
                WHERE violation_id = %s
            """
            
            return self.db.execute_query(update_query, (payment.violation_id,))
            
        except Exception as e:
            print(f"Error refunding payment: {e}")
            return False