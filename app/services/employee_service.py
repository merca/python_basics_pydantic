"""
Employee service for business logic and data operations.
"""

import pandas as pd
import plotly.express as px
from typing import Dict, Any, List, Optional
from datetime import date

from app.services.database_service import get_employee_repository
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from src.models.employee import Employee, EmployeeCreate, EmployeeUpdate, Department, EmploymentStatus


class EmployeeService:
    """Service class for employee-related operations."""
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get dashboard metrics using database aggregations."""
        with get_employee_repository() as (emp_repo, session):
            # Use repository methods for efficient database queries
            salary_stats = emp_repo.get_salary_stats()
            dept_stats = emp_repo.get_department_stats()
            
            # Get counts efficiently using database aggregations
            total_employees = emp_repo.get_total_employees_count()
            active_count = emp_repo.get_active_employees_count()
            
            # Calculate average years of service using database
            avg_years = emp_repo.get_average_years_of_service()
            
            # Count employees with managers
            managers_count = emp_repo.get_employees_with_managers_count()
            
            return {
                'total_employees': total_employees,
                'active_employees': active_count,
                'salary_stats': salary_stats,
                'department_stats': dept_stats,
                'avg_years_of_service': avg_years,
                'employees_with_managers': managers_count
            }
    
    def get_employees_list(self, limit: int = 50, offset: int = 0, 
                          status: Optional[EmploymentStatus] = None) -> Dict[str, Any]:
        """Get paginated list of employees."""
        with get_employee_repository() as (emp_repo, session):
            result = emp_repo.list(limit=limit, skip=offset, status=status)
            # result is now a dictionary, not an object with attributes
            return result
    
    def get_employee_by_id(self, employee_id: int) -> Optional[Employee]:
        """Get employee by database ID."""
        with get_employee_repository() as (emp_repo, session):
            return emp_repo.get(employee_id)
    
    def get_employee_by_employee_id(self, employee_id: str) -> Optional[Employee]:
        """Get employee by employee ID string (e.g., 'EMP001')."""
        with get_employee_repository() as (emp_repo, session):
            return emp_repo.get_by_employee_id(employee_id)
    
    def create_employee(self, employee_data: EmployeeCreate) -> Employee:
        """Create a new employee."""
        with get_employee_repository() as (emp_repo, session):
            return emp_repo.create(employee_data)
    
    def update_employee(self, employee_id: int, employee_data: EmployeeUpdate) -> Optional[Employee]:
        """Update an existing employee."""
        with get_employee_repository() as (emp_repo, session):
            # Validate manager_id if provided
            if hasattr(employee_data, 'manager_id') and employee_data.manager_id is not None:
                # Check if manager exists
                manager = emp_repo.get(employee_data.manager_id)
                if not manager:
                    raise ValueError(f"Manager with ID {employee_data.manager_id} does not exist")
            
            return emp_repo.update(employee_id, employee_data)
    
    def delete_employee(self, employee_id: int) -> bool:
        """Delete an employee."""
        with get_employee_repository() as (emp_repo, session):
            return emp_repo.delete(employee_id)
    
    def get_managers_list(self) -> List[Dict[str, Any]]:
        """Get list of employees who can be managers."""
        with get_employee_repository() as (emp_repo, session):
            result = emp_repo.list(limit=1000)  # Get all employees
            employees = result['items']
            
            # Return managers with their database ID and display name
            managers = []
            for emp in employees:
                managers.append({
                    'id': emp.id,
                    'name': f"{emp.employee_id} - {emp.first_name} {emp.last_name}",
                    'department': emp.department.value if hasattr(emp.department, 'value') else str(emp.department)
                })
            
            return managers
    
    def get_department_chart_data(self) -> Dict[str, Any]:
        """Get data for department distribution chart."""
        with get_employee_repository() as (emp_repo, session):
            dept_stats = emp_repo.get_department_stats()
            
            return {
                'values': list(dept_stats.values()),
                'names': list(dept_stats.keys()),
                'title': "Employee Distribution by Department"
            }
    
    def get_salary_chart_data(self) -> pd.DataFrame:
        """Get data for salary distribution chart."""
        with get_employee_repository() as (emp_repo, session):
            # Get employees for salary analysis
            result = emp_repo.list(limit=1000)  # Get all for chart
            employees = result['items']
            
            dept_salary_data = []
            for emp in employees:
                dept_salary_data.append({
                    'Department': emp.department.value if hasattr(emp.department, 'value') else str(emp.department),
                    'Salary': float(emp.salary)
                })
            
            return pd.DataFrame(dept_salary_data)
    
    def get_years_of_service_data(self) -> List[float]:
        """Get years of service data for histogram."""
        with get_employee_repository() as (emp_repo, session):
            result = emp_repo.list(limit=1000)  # Get all for analysis
            employees = result['items']
            return [emp.years_of_service for emp in employees]
    
    def get_status_distribution_data(self) -> Dict[str, int]:
        """Get status distribution data for bar chart."""
        with get_employee_repository() as (emp_repo, session):
            result = emp_repo.list(limit=1000)  # Get all for analysis
            employees = result['items']
            
            status_data = {}
            for emp in employees:
                status = emp.status.value if hasattr(emp.status, 'value') else str(emp.status)
                status_data[status] = status_data.get(status, 0) + 1
            
            return status_data
