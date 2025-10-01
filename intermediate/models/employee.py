"""
Employee Models for Intermediate Version

This module demonstrates:
- Pydantic models for data validation
- Different model variants (Create/Update/Response)
- Database relationships
- Advanced validation patterns

Learning Focus:
- Model inheritance and composition
- Database-ready model design  
- Cross-field validation
- Response models for APIs
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator


class Department(str, Enum):
    """Employee department choices."""
    ENGINEERING = "engineering"
    MARKETING = "marketing"
    SALES = "sales"
    HR = "hr"
    FINANCE = "finance"
    OPERATIONS = "operations"


class EmploymentStatus(str, Enum):
    """Employment status choices."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TERMINATED = "terminated"
    ON_LEAVE = "on_leave"


class BaseEmployee(BaseModel):
    """
    Base employee model with common fields.
    
    This demonstrates model inheritance - a key intermediate concept.
    """
    first_name: str = Field(
        min_length=2,
        max_length=50,
        description="Employee's first name"
    )
    last_name: str = Field(
        min_length=2,
        max_length=50,
        description="Employee's last name"
    )
    email: EmailStr = Field(
        description="Employee's work email address"
    )
    phone: Optional[str] = Field(
        default=None,
        min_length=10,
        max_length=20,
        description="Phone number (optional)"
    )
    birth_date: Optional[date] = Field(
        default=None,
        description="Birth date (optional)"
    )
    
    # Computed properties available to all models
    @property
    def full_name(self) -> str:
        """Get employee's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self) -> Optional[int]:
        """Calculate age from birth date."""
        if self.birth_date is None:
            return None
        
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )
    
    # Shared validators
    @field_validator('birth_date')
    @classmethod
    def validate_birth_date(cls, v: Optional[date]) -> Optional[date]:
        """Validate birth date - shared across all employee models."""
        if v is None:
            return v
        
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        
        if age < 16:
            raise ValueError(f'Employee must be at least 16 years old (current age: {age})')
        if age > 100:
            raise ValueError(f'Age seems unrealistic (current age: {age})')
        
        return v


class EmployeeCreate(BaseEmployee):
    """
    Model for creating new employees.
    
    Learning Points:
    - Model inheritance from BaseEmployee
    - Required fields for creation
    - Default values and auto-generation
    - Business validation
    """
    
    # Employment Information
    employee_id: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=10,
        pattern=r'^[A-Z0-9]+$',
        description="Employee ID (auto-generated if not provided)"
    )
    department: Department = Field(
        description="Employee's department"
    )
    position: str = Field(
        min_length=2,
        max_length=100,
        description="Job position"
    )
    hire_date: date = Field(
        default_factory=date.today,
        description="Date of hiring"
    )
    salary: Decimal = Field(
        ge=0,
        le=1000000,
        decimal_places=2,
        description="Annual salary"
    )
    status: EmploymentStatus = Field(
        default=EmploymentStatus.ACTIVE,
        description="Employment status"
    )
    
    # Optional manager relationship
    manager_id: Optional[int] = Field(
        default=None,
        description="ID of the employee's manager"
    )
    
    # Skills and notes
    skills: List[str] = Field(
        default_factory=list,
        description="List of employee skills"
    )
    notes: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Additional notes about the employee"
    )
    
    # Additional validators for creation
    @field_validator('hire_date')
    @classmethod
    def validate_hire_date(cls, v: date) -> date:
        """Validate hire date cannot be in the future."""
        if v > date.today():
            raise ValueError('Hire date cannot be in the future')
        return v
    
    @field_validator('skills')
    @classmethod
    def validate_skills(cls, v: List[str]) -> List[str]:
        """Ensure skills are unique and non-empty."""
        if not v:
            return v
        
        # Remove duplicates and empty strings
        unique_skills = []
        seen = set()
        for skill in v:
            skill = skill.strip()
            if skill and skill.lower() not in seen:
                seen.add(skill.lower())
                unique_skills.append(skill)
        
        return unique_skills
    
    @model_validator(mode='after')
    def validate_age_and_hire_date(self):
        """Cross-field validation: check age at hire date."""
        if self.birth_date and self.hire_date:
            hire_age = self.hire_date.year - self.birth_date.year - (
                (self.hire_date.month, self.hire_date.day) < (self.birth_date.month, self.birth_date.day)
            )
            
            if hire_age < 16:
                raise ValueError(f'Employee was too young when hired (age at hire: {hire_age})')
        
        return self


class EmployeeUpdate(BaseModel):
    """
    Model for updating existing employees.
    
    Learning Points:
    - All fields optional for partial updates
    - Separate validation for updates vs creation
    - Flexible update patterns
    """
    
    # Personal information (all optional)
    first_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=50
    )
    last_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=50
    )
    email: Optional[EmailStr] = Field(default=None)
    phone: Optional[str] = Field(
        default=None,
        min_length=10,
        max_length=20
    )
    birth_date: Optional[date] = Field(default=None)
    
    # Employment information (all optional)
    department: Optional[Department] = Field(default=None)
    position: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100
    )
    salary: Optional[Decimal] = Field(
        default=None,
        ge=0,
        le=1000000,
        decimal_places=2
    )
    status: Optional[EmploymentStatus] = Field(default=None)
    manager_id: Optional[int] = Field(default=None)
    skills: Optional[List[str]] = Field(default=None)
    notes: Optional[str] = Field(
        default=None,
        max_length=500
    )
    
    # Validation for updates
    @field_validator('birth_date')
    @classmethod
    def validate_birth_date(cls, v: Optional[date]) -> Optional[date]:
        """Validate birth date for updates."""
        if v is None:
            return v
        
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        
        if age < 16:
            raise ValueError(f'Employee must be at least 16 years old')
        if age > 100:
            raise ValueError(f'Age seems unrealistic')
        
        return v
    
    @field_validator('skills')
    @classmethod 
    def validate_skills(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate skills for updates."""
        if v is None:
            return v
        
        # Remove duplicates and empty strings
        unique_skills = []
        seen = set()
        for skill in v:
            skill = skill.strip()
            if skill and skill.lower() not in seen:
                seen.add(skill.lower())
                unique_skills.append(skill)
        
        return unique_skills


class Employee(BaseEmployee):
    """
    Complete employee model with database fields.
    
    Learning Points:
    - Database-ready model with ID and timestamps
    - Computed properties for derived data
    - Full employee representation
    """
    
    # Database fields
    id: Optional[int] = Field(
        default=None,
        description="Database ID (auto-generated)"
    )
    created_at: Optional[datetime] = Field(
        default=None,
        description="Record creation timestamp"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Last update timestamp"
    )
    
    # Employment Information
    employee_id: str = Field(
        min_length=3,
        max_length=10,
        pattern=r'^[A-Z0-9]+$',
        description="Employee ID"
    )
    department: Department
    position: str = Field(
        min_length=2,
        max_length=100
    )
    hire_date: date
    salary: Decimal = Field(
        ge=0,
        le=1000000,
        decimal_places=2
    )
    status: EmploymentStatus = EmploymentStatus.ACTIVE
    
    # Relationships and additional data
    manager_id: Optional[int] = Field(default=None)
    skills: List[str] = Field(default_factory=list)
    notes: Optional[str] = Field(default=None, max_length=500)
    
    # Additional computed properties
    @property
    def years_of_service(self) -> float:
        """Calculate years of service."""
        today = date.today()
        delta = today - self.hire_date
        return round(delta.days / 365.25, 1)
    
    @property
    def is_active(self) -> bool:
        """Check if employee is currently active."""
        return self.status == EmploymentStatus.ACTIVE
    
    @property
    def salary_formatted(self) -> str:
        """Get formatted salary string."""
        return f"${self.salary:,.2f}"
    
    # Model configuration
    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }


class EmployeeResponse(BaseModel):
    """
    Response model for API endpoints.
    
    Learning Points:
    - Separate models for API responses
    - Include computed fields in responses
    - Control what data is exposed
    """
    
    id: int
    employee_id: str
    full_name: str
    email: EmailStr
    phone: Optional[str]
    department: Department
    position: str
    salary: Decimal
    status: EmploymentStatus
    hire_date: date
    years_of_service: float
    age: Optional[int]
    skills: List[str]
    manager_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }


# Department statistics model for analytics
class DepartmentStats(BaseModel):
    """Model for department statistics."""
    department: Department
    employee_count: int
    avg_salary: Decimal
    min_salary: Decimal
    max_salary: Decimal
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


# Company-wide statistics
class CompanyStats(BaseModel):
    """Model for company-wide statistics."""
    total_employees: int
    active_employees: int
    departments: List[DepartmentStats]
    avg_years_of_service: float
    total_payroll: Decimal
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }