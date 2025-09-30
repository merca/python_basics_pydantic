"""
SQLAlchemy Database Models

This module defines the database schema using SQLAlchemy ORM models
that correspond to our Pydantic models for data validation.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Date, 
    Numeric, ForeignKey, JSON, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func

from ..models.employee import Department, EmploymentStatus

# Create base class for all models
Base = declarative_base()


class TimestampMixin:
    """Mixin to add timestamp columns to models."""
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class EmployeeTable(Base, TimestampMixin):
    """
    SQLAlchemy model for employees table.
    
    This corresponds to our Pydantic Employee model and provides
    the database schema for employee data.
    """
    __tablename__ = "employees"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Personal Information
    first_name = Column(String(50), nullable=False, index=True)
    last_name = Column(String(50), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(20), nullable=True)
    birth_date = Column(Date, nullable=True)

    # Employment Information
    employee_id = Column(String(10), nullable=False, unique=True, index=True)
    department = Column(SQLEnum(Department), nullable=False, index=True)
    position = Column(String(100), nullable=False)
    hire_date = Column(Date, nullable=False, index=True)
    salary = Column(Numeric(10, 2), nullable=False)
    status = Column(
        SQLEnum(EmploymentStatus), 
        nullable=False, 
        default=EmploymentStatus.ACTIVE,
        index=True
    )

    # Manager relationship (self-referential)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    manager = relationship("EmployeeTable", remote_side=[id], backref="direct_reports")

    # Additional data stored as JSON
    skills = Column(JSON, nullable=True, default=list)
    additional_metadata = Column(JSON, nullable=True, default=dict)

    def __repr__(self) -> str:
        """String representation of Employee."""
        return f"<Employee(id={self.id}, name='{self.first_name} {self.last_name}', dept='{self.department}')>"

    @property
    def full_name(self) -> str:
        """Get full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def years_of_service(self) -> float:
        """Calculate years of service."""
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




# Database utility functions
def create_tables(engine):
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def drop_tables(engine):
    """Drop all database tables."""
    Base.metadata.drop_all(bind=engine)


def get_table_info(session: Session) -> dict:
    """
    Get information about all database tables.
    
    Args:
        session: SQLAlchemy session
        
    Returns:
        Dictionary with table information
    """
    tables = {}
    
    for table_name, table in Base.metadata.tables.items():
        # Get row count
        try:
            count = session.query(
                getattr(globals()[f"{table_name.title().rstrip('s')}Table"], 'id')
            ).count()
        except (KeyError, AttributeError):
            # Handle tables that don't follow naming convention
            count = 0
        
        tables[table_name] = {
            'columns': [col.name for col in table.columns],
            'row_count': count,
            'indexes': [idx.name for idx in table.indexes],
            'foreign_keys': [fk.column.key for fk in table.foreign_keys]
        }
    
    return tables


def create_sample_employee(session: Session) -> EmployeeTable:
    """Create and save a sample employee."""
    employee = EmployeeTable(
        first_name="John",
        last_name="Doe",
        email="john.doe@company.com",
        phone="+1-555-123-4567",
        birth_date=date(1985, 6, 15),
        employee_id="EMP001",
        department=Department.ENGINEERING,
        position="Senior Software Engineer",
        hire_date=date(2020, 3, 15),
        salary=Decimal("95000.00"),
        status=EmploymentStatus.ACTIVE,
        skills=["Python", "SQL", "Machine Learning", "Docker"],
        additional_metadata={"performance_rating": "excellent", "remote_eligible": True}
    )
    
    session.add(employee)
    session.commit()
    session.refresh(employee)
    return employee

