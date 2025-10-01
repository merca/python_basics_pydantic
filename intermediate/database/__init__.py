"""
Database package for intermediate version.

This package contains database models, connection management, and utilities.
"""

from .models import Base, EmployeeTable, TimestampMixin, get_database_stats
from .connection import (
    DatabaseManager,
    get_database_manager,
    init_database_with_sample_data,
    get_all_employees,
    get_employee_by_id,
    create_employee,
    delete_employee
)

__all__ = [
    "Base",
    "EmployeeTable", 
    "TimestampMixin",
    "get_database_stats",
    "DatabaseManager",
    "get_database_manager",
    "init_database_with_sample_data",
    "get_all_employees",
    "get_employee_by_id", 
    "create_employee",
    "delete_employee"
]