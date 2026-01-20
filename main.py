"""
Main Application Entry Point
Flask-based REST API for Traffic Violation Management System
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from datetime import datetime
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.database.db_connection import get_db
from backend.models.user import User
from backend.models.violation import Violation
from backend.models.payment import Payment
from backend.managers.violation_manager import ViolationManager
from backend.models.analytics import AnalyticsEngine

app = Flask(__name__, 
            template_folder='templates',
            static_folder='frontend/static')

app.secret_key = 'your-secret-key-change-in-production'
app.config['SESSION_TYPE'] = 'filesystem'

# Initialize managers
violation_manager = ViolationManager()
analytics_engine = AnalyticsEngine()


# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(roles):
    """Decorator to check if user has required role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] not in roles:
                return jsonify({'error': 'Unauthorized access'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ============================================
# Authentication Routes
# ============================================

@app.route('/')
def index():
    """Redirect to dashboard or login"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'GET':
        return render_template('login.html')
    
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        db = get_db()
        query = "SELECT * FROM users WHERE username = %s"
        user_data = db.fetch_one(query, (username,))
        
        if user_data and user_data['password'] == password:
            session['user_id'] = user_data['user_id']
            session['username'] = user_data['username']
            session['full_name'] = user_data['full_name']
            session['role'] = user_data['role']
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user_data['user_id'],
                    'username': user_data['username'],
                    'full_name': user_data['full_name'],
                    'role': user_data['role']
                }
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    return redirect(url_for('login'))


# ============================================
# Dashboard Routes
# ============================================

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')


@app.route('/register-violation')
@login_required
@role_required(['officer', 'admin'])
def register_violation_page():
    """Register violation page"""
    return render_template('register_violation.html')


@app.route('/view-violations')
@login_required
def view_violations_page():
    """View violations page"""
    return render_template('view_violations.html')


@app.route('/analytics')
@login_required
@role_required(['admin'])
def analytics_page():
    """Analytics page"""
    return render_template('analytics.html')


# ============================================
# Violation Routes (API)
# ============================================

@app.route('/api/violations', methods=['GET'])
@login_required
def get_violations():
    """Get all violations or filtered violations"""
    try:
        role = session.get('role')
        user_id = session.get('user_id')
        
        if role == 'citizen':
            violations = violation_manager.get_violations_by_user(user_id)
        else:
            violations = violation_manager.get_all_violations()
        
        return jsonify({'success': True, 'data': violations})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/violations/<int:violation_id>', methods=['GET'])
def get_violation(violation_id):
    """Get specific violation details"""
    try:
        violation = violation_manager.get_violation_by_id(violation_id)
        
        if violation:
            return jsonify({'success': True, 'data': violation.to_dict()})
        else:
            return jsonify({'success': False, 'message': 'Violation not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/violations', methods=['POST'])
@login_required
@role_required(['officer','admin'])
def create_violation():
    """Register a new violation"""
    try:
        data = request.get_json()
        
        # Get officer_id from session, default to 2 if not available
        officer_id = session.get('user_id', 2)
        
        # For now, insert directly with SQL since Violation model doesn't have owner_name
        db = get_db()
        query = """
            INSERT INTO violations
            (vehicle_number, owner_name, user_id, type_id, area_id, officer_id, 
            violation_date, fine_amount, status, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            data['vehicle_number'],
            data.get('owner_name',''),
            data.get('user_id'),
            data['type_id'],
            data['area_id'],
            officer_id,
            data['violation_date'],
            float(data['fine_amount']),
            'unpaid',
            data.get('notes', '')
        )
        if db.execute_query(query, params):
            violation_id = db.get_last_insert_id()
            return jsonify({
                'success': True,
                'message': 'Violation registered successfully',
                'violation_id': violation_id
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to register violation'}), 500
        
        
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/violations/<int:violation_id>/status', methods=['PUT'])
@login_required
@role_required(['officer','admin'])
def update_violation_status(violation_id):
    """Update violation payment status"""
    try:
        data = request.get_json()
        status = data.get('status')
        
        if violation_manager.update_violation_status(violation_id, status):
            return jsonify({'success': True, 'message': 'Status updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to update status'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/violations/search', methods=['GET'])
def search_violations():
    """Search violations"""
    try:
        search_term = request.args.get('q', '')
        
        if search_term:
            violations = violation_manager.search_violations(search_term)
            return jsonify({'success': True, 'data': violations})
        else:
            return jsonify({'success': False, 'message': 'Search term required'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================
# Reference Data Routes
# ============================================

@app.route('/api/violation-types', methods=['GET'])
def get_violation_types():
    """Get all violation types"""
    try:
        types = violation_manager.get_violation_types()
        return jsonify({'success': True, 'data': types})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/areas', methods=['GET'])
def get_areas():
    """Get all areas"""
    try:
        areas = violation_manager.get_areas()
        return jsonify({'success': True, 'data': areas})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================
# Analytics Routes
# ============================================

@app.route('/api/analytics/summary', methods=['GET'])
@login_required
@role_required(['admin'])
def get_analytics_summary():
    """Get analytics summary"""
    try:
        summary = analytics_engine.generate_summary_report()
        return jsonify({'success': True, 'data': summary})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/analytics/by-area', methods=['GET'])
@login_required
@role_required(['admin'])
def get_analytics_by_area():
    """Get violations by area"""
    try:
        data = analytics_engine.get_violations_by_area()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/analytics/by-type', methods=['GET'])
@login_required
@role_required(['admin'])
def get_analytics_by_type():
    """Get violations by type"""
    try:
        data = analytics_engine.get_violations_by_type()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/analytics/trends', methods=['GET'])
@login_required
@role_required(['admin'])
def get_analytics_trends():
    """Get monthly trends"""
    try:
        months = request.args.get('months', 12, type=int)
        data = analytics_engine.get_monthly_trends(months)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/analytics/collection-efficiency', methods=['GET'])
@login_required
@role_required(['admin'])
def get_collection_efficiency():
    """Get collection efficiency metrics"""
    try:
        data = analytics_engine.get_collection_efficiency()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/analytics/top-violators', methods=['GET'])
@login_required
@role_required(['admin'])
def get_top_violators():
    """Get top violators"""
    try:
        limit = request.args.get('limit', 10, type=int)
        data = analytics_engine.get_top_violators(limit)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================
# Statistics Routes
# ============================================

@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """Get general statistics"""
    try:
        role = session.get('role')
        user_id = session.get('user_id')
        
        if role == 'citizen':
            stats = violation_manager.calculate_total_fines(user_id)
        else:
            stats = violation_manager.calculate_total_fines()
        
        return jsonify({'success': True, 'data': stats})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get users by role"""
    try:
        role = request.args.get('role', '')
        
        db = get_db()
        
        if role:
            query = """
                SELECT user_id, username, full_name, email, role 
                FROM users 
                WHERE role = %s
                ORDER BY full_name
            """
            users = db.fetch_all(query, (role,))
        else:
            query = """
                SELECT user_id, username, full_name, email, role 
                FROM users 
                ORDER BY full_name
            """
            users = db.fetch_all(query)
        
        return jsonify({'success': True, 'data': users})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================
# Error Handlers
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ============================================
# Application Startup
# ============================================

def initialize_database():
    """Initialize database with schema"""
    try:
        db = get_db()
        db.connect()
        print("Database initialized successfully")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False


if __name__ == '__main__':
    # Initialize database
    if initialize_database():
        print(f"Starting Traffic Violation Management System...")
        print(f"Server running at http://localhost:5000")
        
        # Run Flask app
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True
        )
    else:
        print("Failed to initialize database. Please check your configuration.")
        sys.exit(1)