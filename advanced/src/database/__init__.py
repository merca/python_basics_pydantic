"""
Database Package

This package provides database connectivity, models, and utilities
for working with SQLite in development and production databases.
"""

from .connection import DatabaseManager, get_db
from .models import Base, create_tables, drop_tables
from .repository import EmployeeRepository

__all__ = [
    "DatabaseManager",
    "get_db", 
    "Base",
    "create_tables",
    "drop_tables",
    "EmployeeRepository",
]