"""
Analytics Module
Provides data analytics and insights for traffic violations
"""

from typing import Dict, List
from datetime import datetime, timedelta
import sys
sys.path.append('..')

from database.db_connection import get_db


class AnalyticsEngine:
    """
    Analytics engine for generating insights and reports
    """
    
    def __init__(self):
        """Initialize analytics engine with database connection"""
        self.db = get_db()
    
    def get_violations_by_area(self) -> List[Dict]:
        """
        Get violation count and total fines by area
        
        Returns:
            List of areas with violation statistics
        """
        query = """
            SELECT 
                a.area_name,
                a.city,
                COUNT(v.violation_id) AS violation_count,
                SUM(v.fine_amount) AS total_fines,
                SUM(CASE WHEN v.status = 'paid' THEN v.fine_amount ELSE 0 END) AS collected_fines
            FROM areas a
            LEFT JOIN violations v ON a.area_id = v.area_id
            GROUP BY a.area_id, a.area_name, a.city
            HAVING violation_count > 0
            ORDER BY violation_count DESC
        """
        
        return self.db.fetch_all(query)
    
    def get_violations_by_type(self) -> List[Dict]:
        """
        Get violation count and statistics by violation type
        
        Returns:
            List of violation types with occurrence statistics
        """
        query = """
            SELECT 
                vt.type_name,
                vt.base_fine,
                COUNT(v.violation_id) AS occurrence_count,
                SUM(v.fine_amount) AS total_fines_collected,
                ROUND(AVG(v.fine_amount), 2) AS avg_fine
            FROM violation_types vt
            LEFT JOIN violations v ON vt.type_id = v.type_id
            GROUP BY vt.type_id, vt.type_name, vt.base_fine
            HAVING occurrence_count > 0
            ORDER BY occurrence_count DESC
        """
        
        return self.db.fetch_all(query)
    
    def get_payment_status_summary(self) -> List[Dict]:
        """
        Get summary of violations by payment status
        
        Returns:
            List with counts and amounts by status
        """
        query = """
            SELECT 
                status,
                COUNT(*) AS count,
                SUM(fine_amount) AS total_amount,
                ROUND(AVG(fine_amount), 2) AS avg_amount
            FROM violations
            GROUP BY status
            ORDER BY count DESC
        """
        
        return self.db.fetch_all(query)
    
    def get_monthly_trends(self, months: int = 12) -> List[Dict]:
        """
        Get monthly violation trends
        
        Args:
            months: Number of months to analyze
        Returns:
            List of monthly statistics
        """
        query = """
            SELECT 
                strftime('%Y-%m', violation_date) AS month,
                COUNT(*) AS total_violations,
                SUM(fine_amount) AS total_fines,
                SUM(CASE WHEN status = 'paid' THEN fine_amount ELSE 0 END) AS collected_amount,
                COUNT(CASE WHEN status = 'paid' THEN 1 END) AS paid_count,
                COUNT(CASE WHEN status = 'unpaid' THEN 1 END) AS unpaid_count
            FROM violations
            WHERE violation_date >= date('now', '-' || %s || ' months')
            GROUP BY strftime('%Y-%m', violation_date)
            ORDER BY month DESC
        """
        
        return self.db.fetch_all(query, (months,))
    
    def get_officer_performance(self) -> List[Dict]:
        """
        Get performance statistics for each officer
        
        Returns:
            List of officers with their violation registration stats
        """
        query = """
            SELECT 
                u.full_name AS officer_name,
                u.email,
                COUNT(v.violation_id) AS violations_registered,
                SUM(v.fine_amount) AS total_fines_imposed,
                SUM(CASE WHEN v.status = 'paid' THEN 1 ELSE 0 END) AS paid_count,
                SUM(CASE WHEN v.status = 'unpaid' THEN 1 ELSE 0 END) AS unpaid_count,
                ROUND(
                    (CAST(SUM(CASE WHEN v.status = 'paid' THEN 1 ELSE 0 END) AS FLOAT) / 
                     NULLIF(COUNT(v.violation_id), 0)) * 100, 2
                ) AS collection_rate
            FROM users u
            LEFT JOIN violations v ON u.user_id = v.officer_id
            WHERE u.role = 'officer'
            GROUP BY u.user_id, u.full_name, u.email
            HAVING violations_registered > 0
            ORDER BY violations_registered DESC
        """
        
        return self.db.fetch_all(query)
    
    def get_top_violators(self, limit: int = 10) -> List[Dict]:
        """
        Get top violators by number of violations
        
        Args:
            limit: Number of top violators to return
        Returns:
            List of top violators
        """
        query = """
            SELECT 
                v.vehicle_number,
                u.full_name AS owner_name,
                COUNT(v.violation_id) AS violation_count,
                SUM(v.fine_amount) AS total_fines,
                SUM(CASE WHEN v.status = 'paid' THEN v.fine_amount ELSE 0 END) AS paid_amount,
                SUM(CASE WHEN v.status = 'unpaid' THEN v.fine_amount ELSE 0 END) AS unpaid_amount
            FROM violations v
            LEFT JOIN users u ON v.user_id = u.user_id
            GROUP BY v.vehicle_number, u.full_name
            HAVING violation_count > 1
            ORDER BY violation_count DESC, total_fines DESC
            LIMIT %s
        """
        
        return self.db.fetch_all(query, (limit,))
    
    def get_daily_violations(self, days: int = 30) -> List[Dict]:
        """
        Get daily violation counts for the last N days
        
        Args:
            days: Number of days to analyze
        Returns:
            List of daily violation counts
        """
        query = """
            SELECT 
                DATE(violation_date) AS date,
                COUNT(*) AS violation_count,
                SUM(fine_amount) AS total_fines
            FROM violations
            WHERE violation_date >= date('now', '-' || %s || ' days')
            GROUP BY DATE(violation_date)
            ORDER BY date DESC
        """
        
        return self.db.fetch_all(query, (days,))
    
    def get_collection_efficiency(self) -> Dict:
        """
        Calculate overall collection efficiency metrics
        
        Returns:
            Dictionary with collection efficiency metrics
        """
        query = """
            SELECT 
                COUNT(*) AS total_violations,
                COUNT(CASE WHEN status = 'paid' THEN 1 END) AS paid_violations,
                COUNT(CASE WHEN status = 'unpaid' THEN 1 END) AS unpaid_violations,
                SUM(fine_amount) AS total_fines,
                SUM(CASE WHEN status = 'paid' THEN fine_amount ELSE 0 END) AS collected_amount,
                SUM(CASE WHEN status = 'unpaid' THEN fine_amount ELSE 0 END) AS pending_amount,
                ROUND(
                    (CAST(SUM(CASE WHEN status = 'paid' THEN fine_amount ELSE 0 END) AS FLOAT) / 
                     NULLIF(SUM(fine_amount), 0)) * 100, 2
                ) AS collection_percentage
            FROM violations
        """
        
        result = self.db.fetch_one(query)
        
        if result:
            return {
                'total_violations': result.get('total_violations', 0),
                'paid_violations': result.get('paid_violations', 0),
                'unpaid_violations': result.get('unpaid_violations', 0),
                'total_fines': float(result.get('total_fines', 0) or 0),
                'collected_amount': float(result.get('collected_amount', 0) or 0),
                'pending_amount': float(result.get('pending_amount', 0) or 0),
                'collection_percentage': float(result.get('collection_percentage', 0) or 0)
            }
        return {}
    
    def get_peak_violation_hours(self) -> List[Dict]:
        """
        Get violation distribution by hour of day
        
        Returns:
            List of hours with violation counts
        """
        query = """
            SELECT 
                CAST(strftime('%H', violation_date) AS INTEGER) AS hour,
                COUNT(*) AS violation_count
            FROM violations
            GROUP BY CAST(strftime('%H', violation_date) AS INTEGER)
            ORDER BY hour
        """
        
        return self.db.fetch_all(query)
    
    def generate_summary_report(self) -> Dict:
        """
        Generate a comprehensive summary report
        
        Returns:
            Dictionary containing summary statistics
        """
        return {
            'collection_efficiency': self.get_collection_efficiency(),
            'payment_status': self.get_payment_status_summary(),
            'top_areas': self.get_violations_by_area()[:5],
            'top_violation_types': self.get_violations_by_type()[:5],
            'recent_trends': self.get_monthly_trends(3)
        }
    
    def export_analytics_data(self, analytics_type: str) -> List[Dict]:
        """
        Export analytics data based on type
        
        Args:
            analytics_type: Type of analytics to export
        Returns:
            List of data records
        """
        analytics_map = {
            'by_area': self.get_violations_by_area,
            'by_type': self.get_violations_by_type,
            'monthly_trends': self.get_monthly_trends,
            'officer_performance': self.get_officer_performance,
            'top_violators': self.get_top_violators
        }
        
        if analytics_type in analytics_map:
            return analytics_map[analytics_type]()
        return []