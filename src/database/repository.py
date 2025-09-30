"""
Repository Pattern Implementation

This module implements the repository pattern for database operations,
providing a clean interface between our Pydantic models and SQLAlchemy models.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from decimal import Decimal

from .models import EmployeeTable
from ..models.employee import (
    Employee, EmployeeCreate, EmployeeUpdate, 
    Department, EmploymentStatus
)


class BaseRepository:
    """
    Base repository class with common database operations.
    """
    
    def __init__(self, session: Session):
        """Initialize repository with database session."""
        self.session = session
    
    def commit(self) -> None:
        """Commit the current transaction."""
        self.session.commit()
    
    def rollback(self) -> None:
        """Rollback the current transaction."""
        self.session.rollback()
    
    def refresh(self, instance) -> None:
        """Refresh an instance from the database."""
        self.session.refresh(instance)


class EmployeeRepository(BaseRepository):
    """
    Repository for employee database operations.
    
    Provides CRUD operations and business logic for employee data.
    """
    
    def _generate_employee_id(self) -> str:
        """Generate a unique employee ID."""
        # Get the highest existing employee ID
        result = self.session.query(func.max(EmployeeTable.employee_id)).scalar()
        
        if result:
            # Extract number from existing ID (e.g., "EMP001" -> 1)
            import re
            match = re.search(r'EMP(\d+)', result)
            if match:
                next_num = int(match.group(1)) + 1
            else:
                next_num = 1
        else:
            next_num = 1
        
        return f"EMP{next_num:03d}"
    
    def create(self, employee_data: EmployeeCreate) -> Employee:
        """
        Create a new employee.
        
        Args:
            employee_data: Employee creation data
            
        Returns:
            Created employee
            
        Raises:
            ValueError: If employee_id or email already exists
        """
        # Auto-generate employee_id if not provided
        if not employee_data.employee_id:
            employee_data.employee_id = self._generate_employee_id()
        
        # Check for duplicates
        existing_employee_id = self.session.query(EmployeeTable).filter(
            EmployeeTable.employee_id == employee_data.employee_id
        ).first()
        if existing_employee_id:
            raise ValueError(f"Employee ID {employee_data.employee_id} already exists")
        
        existing_email = self.session.query(EmployeeTable).filter(
            EmployeeTable.email == employee_data.email
        ).first()
        if existing_email:
            raise ValueError(f"Email {employee_data.email} already exists")
        
        # Create SQLAlchemy model from Pydantic model
        db_employee = EmployeeTable(**employee_data.model_dump(exclude={'id', 'created_at', 'updated_at'}))
        
        self.session.add(db_employee)
        self.session.commit()
        self.session.refresh(db_employee)
        
        # Convert back to Pydantic model
        return self._to_pydantic(db_employee)
    
    def get(self, employee_id: int) -> Optional[Employee]:
        """
        Get employee by ID.
        
        Args:
            employee_id: Employee ID
            
        Returns:
            Employee if found, None otherwise
        """
        db_employee = self.session.query(EmployeeTable).filter(
            EmployeeTable.id == employee_id
        ).first()
        
        return self._to_pydantic(db_employee) if db_employee else None
    
    def get_by_employee_id(self, employee_id: str) -> Optional[Employee]:
        """
        Get employee by employee_id string.
        
        Args:
            employee_id: Employee ID string (e.g., "EMP001")
            
        Returns:
            Employee if found, None otherwise
        """
        db_employee = self.session.query(EmployeeTable).filter(
            EmployeeTable.employee_id == employee_id
        ).first()
        
        return self._to_pydantic(db_employee) if db_employee else None
    
    def get_by_email(self, email: str) -> Optional[Employee]:
        """
        Get employee by email.
        
        Args:
            email: Employee email
            
        Returns:
            Employee if found, None otherwise
        """
        db_employee = self.session.query(EmployeeTable).filter(
            EmployeeTable.email == email
        ).first()
        
        return self._to_pydantic(db_employee) if db_employee else None
    
    def update(self, employee_id: int, employee_data: EmployeeUpdate) -> Optional[Employee]:
        """
        Update an employee.
        
        Args:
            employee_id: Employee ID
            employee_data: Updated employee data
            
        Returns:
            Updated employee if found, None otherwise
        """
        db_employee = self.session.query(EmployeeTable).filter(
            EmployeeTable.id == employee_id
        ).first()
        
        if not db_employee:
            return None
        
        # Update only provided fields
        update_data = employee_data.model_dump(exclude_unset=True, exclude={'id', 'created_at', 'updated_at'})
        for field, value in update_data.items():
            setattr(db_employee, field, value)
        
        self.session.commit()
        self.session.refresh(db_employee)
        
        return self._to_pydantic(db_employee)
    
    def delete(self, employee_id: int) -> bool:
        """
        Delete an employee.
        
        Args:
            employee_id: Employee ID
            
        Returns:
            True if deleted, False if not found
        """
        db_employee = self.session.query(EmployeeTable).filter(
            EmployeeTable.id == employee_id
        ).first()
        
        if not db_employee:
            return False
        
        self.session.delete(db_employee)
        self.session.commit()
        return True
    
    def list(
        self, 
        skip: int = 0, 
        limit: int = 100,
        department: Optional[Department] = None,
        status: Optional[EmploymentStatus] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List employees with filtering and pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            department: Filter by department
            status: Filter by employment status
            search: Search term for name or email
            
        Returns:
            Dictionary with employees and pagination info
        """
        query = self.session.query(EmployeeTable)
        
        # Apply filters
        if department:
            query = query.filter(EmployeeTable.department == department)
        
        if status:
            query = query.filter(EmployeeTable.status == status)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    EmployeeTable.first_name.ilike(search_term),
                    EmployeeTable.last_name.ilike(search_term),
                    EmployeeTable.email.ilike(search_term),
                    EmployeeTable.employee_id.ilike(search_term)
                )
            )
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        employees = query.offset(skip).limit(limit).all()
        
        # Convert to Pydantic models
        pydantic_employees = [self._to_pydantic(emp) for emp in employees]
        
        # Calculate pagination info
        page = (skip // limit) + 1
        has_next = (skip + limit) < total_count
        has_prev = skip > 0
        
        return {
            'items': pydantic_employees,
            'total_count': total_count,
            'page': page,
            'page_size': limit,
            'has_next': has_next,
            'has_prev': has_prev
        }
    
    def get_department_stats(self) -> Dict[str, int]:
        """
        Get employee count by department.
        
        Returns:
            Dictionary with department counts
        """
        stats = self.session.query(
            EmployeeTable.department,
            func.count(EmployeeTable.id)
        ).group_by(EmployeeTable.department).all()
        
        return {str(dept): count for dept, count in stats}
    
    def get_salary_stats(self) -> Dict[str, float]:
        """
        Get salary statistics.
        
        Returns:
            Dictionary with salary statistics
        """
        result = self.session.query(
            func.avg(EmployeeTable.salary),
            func.min(EmployeeTable.salary),
            func.max(EmployeeTable.salary),
            func.count(EmployeeTable.id)
        ).first()
        
        return {
            "average": float(result[0] or 0),
            "minimum": float(result[1] or 0),
            "maximum": float(result[2] or 0),
            "count": result[3]
        }
    
    def get_employees_by_manager(self, manager_id: int) -> List[Employee]:
        """
        Get all direct reports for a manager.
        
        Args:
            manager_id: Manager's employee ID
            
        Returns:
            List of direct report employees
        """
        employees = self.session.query(EmployeeTable).filter(
            EmployeeTable.manager_id == manager_id
        ).all()
        
        return [self._to_pydantic(emp) for emp in employees]
    
    def get_average_years_of_service(self) -> float:
        """
        Get average years of service by calculating from hire_date.
        
        Returns:
            Average years of service
        """
        # Get all employees and calculate years of service in Python
        # since years_of_service is a computed property, not a database column
        employees = self.session.query(EmployeeTable).all()
        if not employees:
            return 0.0
        
        total_years = sum(emp.years_of_service for emp in employees)
        return round(total_years / len(employees), 1)
    
    def get_employees_with_managers_count(self) -> int:
        """
        Get count of employees who have managers.
        
        Returns:
            Count of employees with managers
        """
        return self.session.query(EmployeeTable).filter(
            EmployeeTable.manager_id.isnot(None)
        ).count()
    
    def get_active_employees_count(self) -> int:
        """
        Get count of active employees using database aggregation.
        
        Returns:
            Count of active employees
        """
        return self.session.query(EmployeeTable).filter(
            EmployeeTable.status == EmploymentStatus.ACTIVE
        ).count()
    
    def get_total_employees_count(self) -> int:
        """
        Get total count of employees using database aggregation.
        
        Returns:
            Total count of employees
        """
        return self.session.query(EmployeeTable).count()
    
    def _to_pydantic(self, db_employee: EmployeeTable) -> Employee:
        """Convert SQLAlchemy model to Pydantic model."""
        from ..models.employee import Department, EmploymentStatus
        
        # Ensure enum values are properly converted
        department = db_employee.department
        if isinstance(department, str):
            department = Department(department)
        
        status = db_employee.status
        if isinstance(status, str):
            status = EmploymentStatus(status)
        
        return Employee(
            id=db_employee.id,
            first_name=db_employee.first_name,
            last_name=db_employee.last_name,
            email=db_employee.email,
            phone=db_employee.phone,
            birth_date=db_employee.birth_date,
            employee_id=db_employee.employee_id,
            department=department,
            position=db_employee.position,
            hire_date=db_employee.hire_date,
            salary=db_employee.salary,
            status=status,
            manager_id=db_employee.manager_id,
            skills=db_employee.skills or [],
            additional_metadata=db_employee.additional_metadata or {},
            created_at=db_employee.created_at,
            updated_at=db_employee.updated_at
        )

