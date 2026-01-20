"""
Database Connection Module
Handles database connectivity using MySQL/SQLite
"""

import mysql.connector
from mysql.connector import Error
import sqlite3
from typing import Optional, Any, List, Tuple
import os


class DatabaseConnection:
    """
    Singleton database connection class
    Supports both MySQL and SQLite databases
    """
    
    _instance = None
    _connection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize database configuration"""
        self.db_type = os.getenv('DB_TYPE', 'sqlite')  # 'mysql' or 'sqlite'
        self.config = {
            'mysql': {
                'host': os.getenv('DB_HOST', 'localhost'),
                'user': os.getenv('DB_USER', 'root'),
                'password': os.getenv('DB_PASSWORD', ''),
                'database': os.getenv('DB_NAME', 'traffic_violation_db')
            },
            'sqlite': {
                'database': os.getenv('SQLITE_DB', 'traffic_violations.db')
            }
        }
    
    def connect(self) -> bool:
        """
        Establish database connection
        Returns: True if successful, False otherwise
        """
        try:
            if self.db_type == 'mysql':
                self._connection = mysql.connector.connect(
                    host=self.config['mysql']['host'],
                    user=self.config['mysql']['user'],
                    password=self.config['mysql']['password'],
                    database=self.config['mysql']['database']
                )
            else:  # SQLite
                self._connection = sqlite3.connect(
                    self.config['sqlite']['database'],
                    check_same_thread=False
                )
                self._connection.row_factory = sqlite3.Row
            
            print(f"Successfully connected to {self.db_type} database")
            return True
            
        except Error as e:
            print(f"Error connecting to database: {e}")
            return False
    
    def get_connection(self):
        """
        Get active database connection
        Returns: Database connection object
        """
        if self._connection is None or (
            self.db_type == 'mysql' and not self._connection.is_connected()
        ):
            self.connect()
        return self._connection
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> bool:
        """
        Execute INSERT, UPDATE, DELETE queries
        Args:
            query: SQL query string
            params: Query parameters (tuple)
        Returns: True if successful, False otherwise
        """
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            connection.commit()
            cursor.close()
            return True
            
        except Error as e:
            print(f"Error executing query: {e}")
            return False
    
    def fetch_one(self, query: str, params: Optional[Tuple] = None) -> Optional[Any]:
        """
        Fetch single row from database
        Args:
            query: SQL SELECT query
            params: Query parameters (tuple)
        Returns: Single row result or None
        """
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True) if self.db_type == 'mysql' else connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            result = cursor.fetchone()
            cursor.close()
            
            # Convert sqlite3.Row to dict
            if self.db_type == 'sqlite' and result:
                result = dict(result)
            
            return result
            
        except Error as e:
            print(f"Error fetching data: {e}")
            return None
    
    def fetch_all(self, query: str, params: Optional[Tuple] = None) -> List[Any]:
        """
        Fetch all rows from database
        Args:
            query: SQL SELECT query
            params: Query parameters (tuple)
        Returns: List of rows or empty list
        """
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True) if self.db_type == 'mysql' else connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            cursor.close()
            
            # Convert sqlite3.Row to dict
            if self.db_type == 'sqlite':
                results = [dict(row) for row in results]
            
            return results
            
        except Error as e:
            print(f"Error fetching data: {e}")
            return []
    
    def get_last_insert_id(self) -> Optional[int]:
        """
        Get the ID of the last inserted row
        Returns: Last insert ID or None
        """
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            if self.db_type == 'mysql':
                cursor.execute("SELECT LAST_INSERT_ID()")
                result = cursor.fetchone()
                return result[0] if result else None
            else:  # SQLite
                cursor.execute("SELECT last_insert_rowid()")
                result = cursor.fetchone()
                return result[0] if result else None
                
        except Error as e:
            print(f"Error getting last insert ID: {e}")
            return None
    
    def close(self):
        """Close database connection"""
        if self._connection:
            if self.db_type == 'mysql':
                if self._connection.is_connected():
                    self._connection.close()
            else:
                self._connection.close()
            print("Database connection closed")
    
    def __del__(self):
        """Destructor to ensure connection is closed"""
        self.close()


# Utility function for easy access
def get_db():
    """Get database connection instance"""
    return DatabaseConnection()