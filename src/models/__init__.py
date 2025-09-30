"""
Pydantic Models Package

This package contains all the Pydantic models used throughout the application,
demonstrating data validation, serialization, and type safety.
"""

from .employee import Employee, EmployeeCreate, EmployeeUpdate
from .base import BaseModel, TimestampMixin

__all__ = [
    "Employee",
    "EmployeeCreate", 
    "EmployeeUpdate",
    "BaseModel",
    "TimestampMixin",
]