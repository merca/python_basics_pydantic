"""
Database Models for Intermediate Version

This module demonstrates:
- SQLAlchemy ORM models
- Database table definitions
- Relationships and constraints
- Integration with Pydantic models

Learning Focus:
- ORM mapping patterns
- Database schema design
- Foreign key relationships
- Timestamps and auto-generation
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Create base class for all database models
Base = declarative_base()


class TimestampMixin:
    """Mixin to add created_at and updated_at to models."""
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        doc="When the record was created"
    )
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
        doc="When the record was last updated"
    )


class EmployeeTable(Base, TimestampMixin):
    """
    SQLAlchemy model for employees table.
    
    Learning Points:
    - Table definition with constraints
    - Column types and validation
    - Indexes for performance
    - Self-referential foreign keys (manager relationship)
    - JSON columns for flexible data
    """
    __tablename__ = "employees"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, doc="Auto-incrementing primary key")
    
    # Personal information
    first_name = Column(
        String(50), 
        nullable=False, 
        index=True,
        doc="Employee's first name"
    )
    last_name = Column(
        String(50), 
        nullable=False, 
        index=True,
        doc="Employee's last name"
    )
    email = Column(
        String(255), 
        nullable=False, 
        unique=True, 
        index=True,
        doc="Employee's unique email address"
    )
    phone = Column(
        String(20), 
        nullable=True,
        doc="Employee's phone number"
    )
    birth_date = Column(
        Date, 
        nullable=True,
        doc="Employee's birth date"
    )
    
    # Employment information
    employee_id = Column(
        String(10), 
        nullable=False, 
        unique=True, 
        index=True,
        doc="Employee's unique identifier (e.g., EMP001)"
    )
    department = Column(
        String(50), 
        nullable=False, 
        index=True,
        doc="Employee's department"
    )
    position = Column(
        String(100), 
        nullable=False,
        doc="Employee's job position"
    )
    hire_date = Column(
        Date, 
        nullable=False, 
        index=True,
        doc="Date when employee was hired"
    )
    salary = Column(
        Numeric(10, 2), 
        nullable=False,
        doc="Employee's annual salary"
    )
    status = Column(
        String(20), 
        nullable=False, 
        default="active",
        index=True,
        doc="Employment status (active, inactive, etc.)"
    )
    
    # Self-referential foreign key for manager relationship
    manager_id = Column(
        Integer, 
        ForeignKey("employees.id"), 
        nullable=True,
        doc="ID of the employee's manager"
    )
    
    # Additional data stored as JSON (demonstrates flexible schemas)
    skills = Column(
        JSON, 
        nullable=True, 
        default=list,
        doc="List of employee skills stored as JSON"
    )
    notes = Column(
        Text, 
        nullable=True,
        doc="Additional notes about the employee"
    )
    
    # Relationships
    manager = relationship(
        "EmployeeTable", 
        remote_side=[id], 
        backref="direct_reports",
        doc="Reference to manager (self-referential)"
    )
    
    def __repr__(self) -> str:
        """String representation of the employee."""
        return f"<Employee(id={self.id}, name='{self.first_name} {self.last_name}', dept='{self.department}')>"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.first_name} {self.last_name} ({self.employee_id})"
    
    @property
    def full_name(self) -> str:
        """Get employee's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def years_of_service(self) -> float:
        """Calculate years of service from hire date."""
        today = date.today()
        delta = today - self.hire_date
        return round(delta.days / 365.25, 1)
    
    @property
    def age(self) -> Optional[int]:
        """Calculate age from birth date."""
        if self.birth_date is None:
            return None
        
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )


# Future tables can be added here for more complex scenarios
class DepartmentTable(Base):
    """
    Example of a separate department table for normalized design.
    
    This is commented out for simplicity in this intermediate version,
    but shows how you might structure related tables.
    """
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    budget = Column(Numeric(12, 2), nullable=True)
    
    # If we were using this table, we'd add a foreign key in EmployeeTable:
    # department_id = Column(Integer, ForeignKey("departments.id"))
    # department = relationship("DepartmentTable")


# Database utility functions for learning
def create_sample_employee(session) -> EmployeeTable:
    """
    Create a sample employee for demonstration.
    
    This shows how to create and save records using SQLAlchemy.
    """
    employee = EmployeeTable(
        first_name="Alice",
        last_name="Johnson",
        email="alice.johnson@company.com",
        phone="+1-555-987-6543",
        birth_date=date(1990, 4, 12),
        employee_id="EMP003",
        department="engineering",
        position="Software Engineer",
        hire_date=date(2021, 9, 1),
        salary=Decimal("80000.00"),
        status="active",
        skills=["Python", "React", "PostgreSQL", "Docker"],
        notes="Joined from university program. Shows strong technical skills."
    )
    
    session.add(employee)
    session.commit()
    session.refresh(employee)
    
    return employee


def get_database_stats(session) -> dict:
    """
    Get statistics about the database for learning purposes.
    
    This demonstrates how to write aggregate queries with SQLAlchemy.
    """
    from sqlalchemy import func, distinct
    
    stats = {}
    
    # Basic counts
    stats['total_employees'] = session.query(EmployeeTable).count()
    stats['active_employees'] = session.query(EmployeeTable).filter(
        EmployeeTable.status == 'active'
    ).count()
    
    # Department distribution
    dept_stats = session.query(
        EmployeeTable.department,
        func.count(EmployeeTable.id).label('count')
    ).group_by(EmployeeTable.department).all()
    
    stats['department_distribution'] = {
        dept: count for dept, count in dept_stats
    }
    
    # Salary statistics
    salary_stats = session.query(
        func.avg(EmployeeTable.salary).label('avg_salary'),
        func.min(EmployeeTable.salary).label('min_salary'),
        func.max(EmployeeTable.salary).label('max_salary'),
        func.sum(EmployeeTable.salary).label('total_payroll')
    ).first()
    
    stats['salary_stats'] = {
        'average': float(salary_stats.avg_salary) if salary_stats.avg_salary else 0,
        'minimum': float(salary_stats.min_salary) if salary_stats.min_salary else 0,
        'maximum': float(salary_stats.max_salary) if salary_stats.max_salary else 0,
        'total_payroll': float(salary_stats.total_payroll) if salary_stats.total_payroll else 0
    }
    
    return stats