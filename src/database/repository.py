"""
Repository Pattern Implementation

This module implements the repository pattern for database operations,
providing a clean interface between our Pydantic models and SQLAlchemy models.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, text
from decimal import Decimal

from .models import EmployeeTable, UserTable, AuditLogTable
from ..models.employee import (
    Employee, EmployeeCreate, EmployeeUpdate, 
    Department, EmploymentStatus
)
from ..models.user import (
    User, UserCreate, UserUpdate, 
    UserRole, UserStatus
)
from ..models.validation import ValidationResponse, PaginatedResponse


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
    ) -> PaginatedResponse:
        """
        List employees with filtering and pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            department: Filter by department
            status: Filter by employment status
            search: Search term for name or email
            
        Returns:
            Paginated response with employees
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
        
        return PaginatedResponse.create(
            items=pydantic_employees,
            total_count=total_count,
            page=page,
            page_size=limit
        )
    
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


class UserRepository(BaseRepository):
    """
    Repository for user database operations.
    
    Provides CRUD operations and business logic for user data.
    """
    
    def create(self, user_data: UserCreate) -> User:
        """
        Create a new user.
        
        Args:
            user_data: User creation data
            
        Returns:
            Created user
            
        Raises:
            ValueError: If username or email already exists
        """
        # Check for duplicates
        existing_username = self.session.query(UserTable).filter(
            UserTable.username == user_data.username
        ).first()
        if existing_username:
            raise ValueError(f"Username {user_data.username} already exists")
        
        existing_email = self.session.query(UserTable).filter(
            UserTable.email == user_data.email
        ).first()
        if existing_email:
            raise ValueError(f"Email {user_data.email} already exists")
        
        # Hash password (in a real app, you'd use proper password hashing)
        user_dict = user_data.model_dump(exclude={'password'})
        user_dict['password_hash'] = f"hashed_{user_data.password}"  # Simplified for demo
        
        # Create SQLAlchemy model
        db_user = UserTable(**user_dict)
        
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        
        # Convert back to Pydantic model
        return self._to_pydantic(db_user)
    
    def get(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User if found, None otherwise
        """
        db_user = self.session.query(UserTable).filter(
            UserTable.id == user_id
        ).first()
        
        return self._to_pydantic(db_user) if db_user else None
    
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username
            
        Returns:
            User if found, None otherwise
        """
        db_user = self.session.query(UserTable).filter(
            UserTable.username == username
        ).first()
        
        return self._to_pydantic(db_user) if db_user else None
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: Email address
            
        Returns:
            User if found, None otherwise
        """
        db_user = self.session.query(UserTable).filter(
            UserTable.email == email
        ).first()
        
        return self._to_pydantic(db_user) if db_user else None
    
    def update(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """
        Update a user.
        
        Args:
            user_id: User ID
            user_data: Updated user data
            
        Returns:
            Updated user if found, None otherwise
        """
        db_user = self.session.query(UserTable).filter(
            UserTable.id == user_id
        ).first()
        
        if not db_user:
            return None
        
        # Update only provided fields
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        self.session.commit()
        self.session.refresh(db_user)
        
        return self._to_pydantic(db_user)
    
    def delete(self, user_id: int) -> bool:
        """
        Delete a user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if deleted, False if not found
        """
        db_user = self.session.query(UserTable).filter(
            UserTable.id == user_id
        ).first()
        
        if not db_user:
            return False
        
        self.session.delete(db_user)
        self.session.commit()
        return True
    
    def list(
        self, 
        skip: int = 0, 
        limit: int = 100,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
        search: Optional[str] = None
    ) -> PaginatedResponse:
        """
        List users with filtering and pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            role: Filter by user role
            status: Filter by user status
            search: Search term for name, username, or email
            
        Returns:
            Paginated response with users
        """
        query = self.session.query(UserTable)
        
        # Apply filters
        if role:
            query = query.filter(UserTable.role == role)
        
        if status:
            query = query.filter(UserTable.status == status)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    UserTable.first_name.ilike(search_term),
                    UserTable.last_name.ilike(search_term),
                    UserTable.username.ilike(search_term),
                    UserTable.email.ilike(search_term)
                )
            )
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        users = query.offset(skip).limit(limit).all()
        
        # Convert to Pydantic models
        pydantic_users = [self._to_pydantic(user) for user in users]
        
        # Calculate pagination info
        page = (skip // limit) + 1
        
        return PaginatedResponse.create(
            items=pydantic_users,
            total_count=total_count,
            page=page,
            page_size=limit
        )
    
    def get_role_stats(self) -> Dict[str, int]:
        """
        Get user count by role.
        
        Returns:
            Dictionary with role counts
        """
        stats = self.session.query(
            UserTable.role,
            func.count(UserTable.id)
        ).group_by(UserTable.role).all()
        
        return {str(role): count for role, count in stats}
    
    def _to_pydantic(self, db_user: UserTable) -> User:
        """Convert SQLAlchemy model to Pydantic model."""
        return User(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            first_name=db_user.first_name,
            last_name=db_user.last_name,
            password_hash=db_user.password_hash,
            role=db_user.role,
            permissions=db_user.permissions or [],
            status=db_user.status,
            last_login=db_user.last_login,
            login_attempts=db_user.login_attempts,
            profile_picture_url=db_user.profile_picture_url,
            timezone=db_user.timezone,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )