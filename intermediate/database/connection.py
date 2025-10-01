"""
Database Connection Management for Intermediate Version

This module demonstrates:
- SQLAlchemy engine and session management
- Database initialization and cleanup
- Connection configuration
- Simple transaction management

Learning Focus:
- Database connection patterns
- Session lifecycle management
- SQLite configuration for development
- Basic database operations
"""

import os
from pathlib import Path
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine

from .models import Base, EmployeeTable


class DatabaseManager:
    """
    Simple database manager for learning SQLAlchemy basics.
    
    This is intentionally simpler than the advanced version to focus
    on core database concepts rather than production concerns.
    """
    
    def __init__(self, database_url: str = None):
        """Initialize database manager."""
        if database_url is None:
            # Create data directory if it doesn't exist
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            database_url = f"sqlite:///data/employees.db"
        
        self.database_url = database_url
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Initialize database tables
        self.create_tables()
    
    def _create_engine(self) -> Engine:
        """Create SQLAlchemy engine with SQLite configuration."""
        engine = create_engine(
            self.database_url,
            # SQLite specific settings for development
            connect_args={"check_same_thread": False},
            echo=False  # Set to True to see SQL queries (great for learning!)
        )
        
        # Configure SQLite pragmas for better performance and constraints
        from sqlalchemy import event
        
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.close()
        
        return engine
    
    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)
        print("✅ Database tables created successfully")
    
    def drop_tables(self):
        """Drop all database tables (useful for resetting)."""
        Base.metadata.drop_all(bind=self.engine)
        print("❌ Database tables dropped")
    
    def recreate_tables(self):
        """Drop and recreate all tables (fresh start)."""
        self.drop_tables()
        self.create_tables()
    
    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions.
        
        This is a key pattern for managing database transactions:
        - Automatically commits successful operations
        - Rolls back on exceptions
        - Always closes the session
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"❌ Database error: {e}")
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.session_scope() as session:
                session.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def get_info(self) -> dict:
        """Get database information for debugging."""
        info = {
            "database_url": self.database_url,
            "engine": str(self.engine),
            "connection_test": self.test_connection()
        }
        
        try:
            with self.session_scope() as session:
                # Get table information
                tables = Base.metadata.tables.keys()
                info["tables"] = list(tables)
                
                # Get employee count
                employee_count = session.query(EmployeeTable).count()
                info["employee_count"] = employee_count
                
        except Exception as e:
            info["error"] = str(e)
        
        return info


# Global database manager instance for the application
_db_manager = None


def get_database_manager() -> DatabaseManager:
    """
    Get or create the global database manager instance.
    
    This singleton pattern ensures we have one database connection
    throughout the application lifecycle.
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def init_database_with_sample_data():
    """
    Initialize database with sample data for learning.
    
    This demonstrates how to populate a database with test data.
    """
    db = get_database_manager()
    
    # Check if we already have data
    with db.session_scope() as session:
        if session.query(EmployeeTable).count() > 0:
            print("📊 Database already has data")
            return
    
    # Create sample employees
    sample_employees = [
        {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@company.com",
            "phone": "+1-555-123-4567",
            "birth_date": "1985-06-15",
            "employee_id": "EMP001",
            "department": "engineering",
            "position": "Senior Developer",
            "hire_date": "2020-03-15",
            "salary": 85000.00,
            "status": "active",
            "skills": ["Python", "JavaScript", "SQL", "Docker"],
            "notes": "Experienced developer with strong problem-solving skills."
        },
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@company.com",
            "phone": "+1-555-987-6543",
            "birth_date": "1988-09-22",
            "employee_id": "EMP002",
            "department": "marketing",
            "position": "Marketing Manager",
            "hire_date": "2019-08-20",
            "salary": 75000.00,
            "status": "active",
            "skills": ["Digital Marketing", "Analytics", "SEO", "Content Strategy"],
            "notes": "Creative marketer with data-driven approach."
        },
        {
            "first_name": "Bob",
            "last_name": "Wilson",
            "email": "bob.wilson@company.com",
            "employee_id": "EMP003",
            "department": "sales",
            "position": "Sales Representative",
            "hire_date": "2021-01-10",
            "salary": 65000.00,
            "status": "active",
            "skills": ["Sales", "Customer Relations", "Negotiation"],
            "notes": "Excellent customer relationship management."
        }
    ]
    
    try:
        with db.session_scope() as session:
            for emp_data in sample_employees:
                # Convert date strings to date objects
                from datetime import datetime
                if isinstance(emp_data.get("birth_date"), str):
                    emp_data["birth_date"] = datetime.strptime(emp_data["birth_date"], "%Y-%m-%d").date()
                if isinstance(emp_data.get("hire_date"), str):
                    emp_data["hire_date"] = datetime.strptime(emp_data["hire_date"], "%Y-%m-%d").date()
                
                employee = EmployeeTable(**emp_data)
                session.add(employee)
            
            print(f"✅ Created {len(sample_employees)} sample employees")
    
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")


# Utility functions for common database operations
def get_all_employees() -> list:
    """Get all employees from database."""
    db = get_database_manager()
    with db.session_scope() as session:
        employees = session.query(EmployeeTable).all()
        return [
            {
                "id": emp.id,
                "employee_id": emp.employee_id,
                "full_name": emp.full_name,
                "email": emp.email,
                "department": emp.department,
                "position": emp.position,
                "salary": float(emp.salary),
                "status": emp.status,
                "years_of_service": emp.years_of_service
            }
            for emp in employees
        ]


def get_employee_by_id(employee_id: int) -> dict:
    """Get employee by database ID."""
    db = get_database_manager()
    with db.session_scope() as session:
        employee = session.query(EmployeeTable).filter(EmployeeTable.id == employee_id).first()
        if not employee:
            return None
        
        return {
            "id": employee.id,
            "employee_id": employee.employee_id,
            "first_name": employee.first_name,
            "last_name": employee.last_name,
            "email": employee.email,
            "phone": employee.phone,
            "birth_date": employee.birth_date,
            "department": employee.department,
            "position": employee.position,
            "hire_date": employee.hire_date,
            "salary": float(employee.salary),
            "status": employee.status,
            "manager_id": employee.manager_id,
            "skills": employee.skills,
            "notes": employee.notes,
            "created_at": employee.created_at,
            "updated_at": employee.updated_at,
            "years_of_service": employee.years_of_service,
            "age": employee.age
        }


def create_employee(employee_data: dict) -> dict:
    """Create a new employee in the database."""
    db = get_database_manager()
    
    # Auto-generate employee_id if not provided
    if not employee_data.get("employee_id"):
        with db.session_scope() as session:
            # Find the highest existing employee ID number
            last_emp = session.query(EmployeeTable).order_by(EmployeeTable.employee_id.desc()).first()
            if last_emp and last_emp.employee_id.startswith("EMP"):
                try:
                    last_num = int(last_emp.employee_id[3:])
                    employee_data["employee_id"] = f"EMP{last_num + 1:03d}"
                except ValueError:
                    employee_data["employee_id"] = "EMP001"
            else:
                employee_data["employee_id"] = "EMP001"
    
    try:
        with db.session_scope() as session:
            employee = EmployeeTable(**employee_data)
            session.add(employee)
            session.flush()  # Get the ID without committing
            
            return {
                "id": employee.id,
                "employee_id": employee.employee_id,
                "full_name": employee.full_name,
                "message": "Employee created successfully"
            }
    
    except Exception as e:
        raise Exception(f"Error creating employee: {str(e)}")


def delete_employee(employee_id: int) -> bool:
    """Delete an employee by ID."""
    db = get_database_manager()
    
    try:
        with db.session_scope() as session:
            employee = session.query(EmployeeTable).filter(EmployeeTable.id == employee_id).first()
            if not employee:
                return False
            
            session.delete(employee)
            return True
    
    except Exception as e:
        print(f"❌ Error deleting employee: {e}")
        return False