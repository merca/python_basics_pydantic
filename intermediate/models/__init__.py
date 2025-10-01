"""
Models package for intermediate version.

This package contains all Pydantic models for data validation and serialization.
"""

from .employee import (
    Department,
    EmploymentStatus, 
    BaseEmployee,
    Employee,
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    DepartmentStats,
    CompanyStats
)

__all__ = [
    "Department",
    "EmploymentStatus",
    "BaseEmployee", 
    "Employee",
    "EmployeeCreate",
    "EmployeeUpdate",
    "EmployeeResponse",
    "DepartmentStats",
    "CompanyStats"
]