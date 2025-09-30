"""
Employee Models

This module demonstrates comprehensive Pydantic modeling for employee data,
including validation, serialization, and different model variants for CRUD operations.
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import (
    Field, 
    EmailStr, 
    field_validator, 
    computed_field,
    model_validator
)

from .base import DatabaseModel


class Department(str, Enum):
    """Employee department enumeration."""
    ENGINEERING = "engineering"
    MARKETING = "marketing"
    SALES = "sales"
    HR = "hr"
    FINANCE = "finance"
    OPERATIONS = "operations"


class EmploymentStatus(str, Enum):
    """Employment status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TERMINATED = "terminated"
    ON_LEAVE = "on_leave"


class Employee(DatabaseModel):
    """
    Complete employee model with all fields and validation.
    
    This model represents a full employee record as stored in the database.
    """
    # Personal Information
    first_name: str = Field(
        min_length=1,
        max_length=50,
        description="Employee's first name"
    )
    last_name: str = Field(
        min_length=1,
        max_length=50,
        description="Employee's last name"
    )
    email: EmailStr = Field(
        description="Employee's work email address"
    )
    phone: Optional[str] = Field(
        default=None,
        pattern=r'^\+?[\d\s\-\(\)]+$',
        min_length=10,
        max_length=20,
        description="Employee's phone number"
    )
    birth_date: Optional[date] = Field(
        default=None,
        description="Employee's birth date"
    )
    
    # Employment Information
    employee_id: str = Field(
        min_length=3,
        max_length=10,
        pattern=r'^[A-Z0-9]+$',
        description="Unique employee identifier"
    )
    department: Department = Field(
        description="Employee's department"
    )
    position: str = Field(
        min_length=1,
        max_length=100,
        description="Employee's job position"
    )
    hire_date: date = Field(
        description="Date when employee was hired"
    )
    salary: Decimal = Field(
        ge=0,
        decimal_places=2,
        description="Employee's annual salary"
    )
    status: EmploymentStatus = Field(
        default=EmploymentStatus.ACTIVE,
        description="Current employment status"
    )
    
    # Manager relationship
    manager_id: Optional[int] = Field(
        default=None,
        description="ID of the employee's manager"
    )
    
    # Additional data
    skills: List[str] = Field(
        default_factory=list,
        description="List of employee skills"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the employee"
    )

    @field_validator('birth_date')
    @classmethod
    def validate_birth_date(cls, v: Optional[date]) -> Optional[date]:
        """Validate that birth date is not in the future and employee is at least 16."""
        if v is None:
            return v
        
        today = date.today()
        if v >= today:
            raise ValueError('Birth date cannot be in the future')
        
        # Calculate age
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 16:
            raise ValueError('Employee must be at least 16 years old')
        
        return v

    @field_validator('hire_date')
    @classmethod
    def validate_hire_date(cls, v: date) -> date:
        """Validate that hire date is not in the future."""
        if v > date.today():
            raise ValueError('Hire date cannot be in the future')
        return v

    @field_validator('salary')
    @classmethod
    def validate_salary(cls, v: Decimal) -> Decimal:
        """Validate salary is within reasonable bounds."""
        if v < 0:
            raise ValueError('Salary cannot be negative')
        if v > Decimal('10000000'):  # 10 million
            raise ValueError('Salary seems unreasonably high')
        return v

    @field_validator('skills')
    @classmethod
    def validate_skills(cls, v: List[str]) -> List[str]:
        """Ensure skills are unique and non-empty."""
        if not v:
            return v
        
        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in v:
            skill = skill.strip()
            if skill and skill.lower() not in seen:
                seen.add(skill.lower())
                unique_skills.append(skill)
        
        return unique_skills

    @model_validator(mode='after')
    def validate_manager_not_self(self):
        """Ensure employee is not their own manager."""
        if self.manager_id is not None and self.id is not None:
            if self.manager_id == self.id:
                raise ValueError('Employee cannot be their own manager')
        return self

    @computed_field
    @property
    def full_name(self) -> str:
        """Computed full name property."""
        return f"{self.first_name} {self.last_name}"

    @computed_field
    @property
    def years_of_service(self) -> float:
        """Calculate years of service based on hire date."""
        today = date.today()
        delta = today - self.hire_date
        return round(delta.days / 365.25, 1)

    @computed_field
    @property
    def age(self) -> Optional[int]:
        """Calculate age from birth date."""
        if self.birth_date is None:
            return None
        
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    def promote(self, new_position: str, new_salary: Decimal) -> None:
        """Promote employee with validation."""
        if new_salary <= self.salary:
            raise ValueError("New salary must be higher than current salary")
        
        self.position = new_position
        self.salary = new_salary
        self.update_timestamp()

    def add_skill(self, skill: str) -> None:
        """Add a skill to the employee's skill set."""
        skill = skill.strip()
        if skill and skill.lower() not in [s.lower() for s in self.skills]:
            self.skills.append(skill)
            self.update_timestamp()


class EmployeeCreate(DatabaseModel):
    """
    Model for creating new employees.
    
    Excludes auto-generated fields like ID and timestamps.
    """
    # Personal Information
    first_name: str = Field(
        min_length=1,
        max_length=50,
        description="Employee's first name"
    )
    last_name: str = Field(
        min_length=1,
        max_length=50,
        description="Employee's last name"
    )
    email: EmailStr = Field(
        description="Employee's work email address"
    )
    phone: Optional[str] = Field(
        default=None,
        pattern=r'^\+?[\d\s\-\(\)]+$',
        min_length=10,
        max_length=20,
        description="Employee's phone number"
    )
    birth_date: Optional[date] = Field(
        default=None,
        description="Employee's birth date"
    )
    
    # Employment Information
    employee_id: str = Field(
        min_length=3,
        max_length=10,
        pattern=r'^[A-Z0-9]+$',
        description="Unique employee identifier"
    )
    department: Department = Field(
        description="Employee's department"
    )
    position: str = Field(
        min_length=1,
        max_length=100,
        description="Employee's job position"
    )
    hire_date: date = Field(
        default_factory=date.today,
        description="Date when employee was hired"
    )
    salary: Decimal = Field(
        ge=0,
        decimal_places=2,
        description="Employee's annual salary"
    )
    status: EmploymentStatus = Field(
        default=EmploymentStatus.ACTIVE,
        description="Current employment status"
    )
    
    # Manager relationship
    manager_id: Optional[int] = Field(
        default=None,
        description="ID of the employee's manager"
    )
    
    # Additional data
    skills: List[str] = Field(
        default_factory=list,
        description="List of employee skills"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the employee"
    )

    # Reuse validators from Employee model
    validate_birth_date = Employee.validate_birth_date
    validate_hire_date = Employee.validate_hire_date
    validate_salary = Employee.validate_salary
    validate_skills = Employee.validate_skills


class EmployeeUpdate(DatabaseModel):
    """
    Model for updating existing employees.
    
    All fields are optional to support partial updates.
    """
    # Personal Information
    first_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="Employee's first name"
    )
    last_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="Employee's last name"
    )
    email: Optional[EmailStr] = Field(
        default=None,
        description="Employee's work email address"
    )
    phone: Optional[str] = Field(
        default=None,
        pattern=r'^\+?[\d\s\-\(\)]+$',
        min_length=10,
        max_length=20,
        description="Employee's phone number"
    )
    birth_date: Optional[date] = Field(
        default=None,
        description="Employee's birth date"
    )
    
    # Employment Information
    department: Optional[Department] = Field(
        default=None,
        description="Employee's department"
    )
    position: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Employee's job position"
    )
    salary: Optional[Decimal] = Field(
        default=None,
        ge=0,
        decimal_places=2,
        description="Employee's annual salary"
    )
    status: Optional[EmploymentStatus] = Field(
        default=None,
        description="Current employment status"
    )
    
    # Manager relationship
    manager_id: Optional[int] = Field(
        default=None,
        description="ID of the employee's manager"
    )
    
    # Additional data
    skills: Optional[List[str]] = Field(
        default=None,
        description="List of employee skills"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata about the employee"
    )

    # Reuse validators from Employee model
    validate_birth_date = Employee.validate_birth_date
    validate_salary = Employee.validate_salary
    validate_skills = Employee.validate_skills


class EmployeeResponse(Employee):
    """
    Model for employee API responses.
    
    Includes computed fields and excludes sensitive information.
    """
    # Inherit all fields from Employee but could exclude sensitive ones
    # For example, we might exclude salary for certain API endpoints
    
    class Config:
        # This model is primarily for serialization
        from_attributes = True
        
    def to_public_dict(self) -> Dict[str, Any]:
        """Convert to dictionary without sensitive information."""
        data = self.model_dump()
        # Remove sensitive fields for public APIs
        sensitive_fields = ['salary', 'phone', 'birth_date']
        for field in sensitive_fields:
            data.pop(field, None)
        return data


# Example usage and factory functions
def create_sample_employee() -> EmployeeCreate:
    """Create a sample employee for testing."""
    return EmployeeCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@company.com",
        phone="+1-555-123-4567",
        birth_date=date(1985, 6, 15),
        employee_id="EMP001",
        department=Department.ENGINEERING,
        position="Senior Software Engineer",
        salary=Decimal("95000.00"),
        skills=["Python", "SQL", "Machine Learning", "Docker"],
        metadata={"performance_rating": "excellent", "remote_eligible": True}
    )