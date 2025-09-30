"""
User Models

This module demonstrates user authentication and authorization models,
including password handling and user management.
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import (
    Field, 
    EmailStr, 
    field_validator,
    computed_field
)

from .base import DatabaseModel


class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    HR_MANAGER = "hr_manager"
    MANAGER = "manager"
    EMPLOYEE = "employee"
    READONLY = "readonly"


class UserStatus(str, Enum):
    """User status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_ACTIVATION = "pending_activation"


class User(DatabaseModel):
    """
    Complete user model for authentication and authorization.
    """
    # Basic Information
    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r'^[a-zA-Z0-9_]+$',
        description="Unique username for login"
    )
    email: EmailStr = Field(
        description="User's email address"
    )
    first_name: str = Field(
        min_length=1,
        max_length=50,
        description="User's first name"
    )
    last_name: str = Field(
        min_length=1,
        max_length=50,
        description="User's last name"
    )
    
    # Password (hashed)
    password_hash: str = Field(
        description="Hashed password"
    )
    
    # Authorization
    role: UserRole = Field(
        default=UserRole.EMPLOYEE,
        description="User's role in the system"
    )
    permissions: List[str] = Field(
        default_factory=list,
        description="Additional permissions granted to user"
    )
    
    # Status and tracking
    status: UserStatus = Field(
        default=UserStatus.PENDING_ACTIVATION,
        description="Current user status"
    )
    last_login: Optional[datetime] = Field(
        default=None,
        description="Last login timestamp"
    )
    login_attempts: int = Field(
        default=0,
        ge=0,
        description="Number of failed login attempts"
    )
    
    # Profile
    profile_picture_url: Optional[str] = Field(
        default=None,
        description="URL to user's profile picture"
    )
    timezone: str = Field(
        default="UTC",
        description="User's preferred timezone"
    )
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format and reserved names."""
        v = v.lower().strip()
        
        # Check for reserved usernames
        reserved = {'admin', 'root', 'system', 'api', 'support'}
        if v in reserved:
            raise ValueError(f'Username "{v}" is reserved')
        
        return v
    
    @field_validator('permissions')
    @classmethod
    def validate_permissions(cls, v: List[str]) -> List[str]:
        """Validate and normalize permissions."""
        if not v:
            return v
        
        # Normalize permissions (lowercase, unique)
        normalized = list(set(perm.lower().strip() for perm in v if perm.strip()))
        return normalized
    
    @computed_field
    @property
    def full_name(self) -> str:
        """Computed full name property."""
        return f"{self.first_name} {self.last_name}"
    
    @computed_field
    @property
    def is_active(self) -> bool:
        """Check if user is active."""
        return self.status == UserStatus.ACTIVE
    
    @computed_field
    @property
    def is_admin(self) -> bool:
        """Check if user has admin privileges."""
        return self.role == UserRole.ADMIN
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission."""
        return permission.lower() in [p.lower() for p in self.permissions]
    
    def add_permission(self, permission: str) -> None:
        """Add a permission to the user."""
        permission = permission.lower().strip()
        if permission and not self.has_permission(permission):
            self.permissions.append(permission)
            self.update_timestamp()
    
    def remove_permission(self, permission: str) -> None:
        """Remove a permission from the user."""
        permission = permission.lower().strip()
        self.permissions = [p for p in self.permissions if p.lower() != permission]
        self.update_timestamp()
    
    def activate(self) -> None:
        """Activate the user account."""
        self.status = UserStatus.ACTIVE
        self.update_timestamp()
    
    def suspend(self) -> None:
        """Suspend the user account."""
        self.status = UserStatus.SUSPENDED
        self.update_timestamp()
    
    def record_login(self) -> None:
        """Record successful login."""
        self.last_login = datetime.now()
        self.login_attempts = 0
        self.update_timestamp()
    
    def record_failed_login(self) -> None:
        """Record failed login attempt."""
        self.login_attempts += 1
        self.update_timestamp()


class UserCreate(DatabaseModel):
    """
    Model for creating new users.
    
    Excludes auto-generated fields and sensitive information.
    """
    # Basic Information
    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r'^[a-zA-Z0-9_]+$',
        description="Unique username for login"
    )
    email: EmailStr = Field(
        description="User's email address"
    )
    first_name: str = Field(
        min_length=1,
        max_length=50,
        description="User's first name"
    )
    last_name: str = Field(
        min_length=1,
        max_length=50,
        description="User's last name"
    )
    
    # Plain password (will be hashed)
    password: str = Field(
        min_length=8,
        max_length=128,
        description="User's password"
    )
    
    # Authorization
    role: UserRole = Field(
        default=UserRole.EMPLOYEE,
        description="User's role in the system"
    )
    permissions: List[str] = Field(
        default_factory=list,
        description="Additional permissions granted to user"
    )
    
    # Profile
    profile_picture_url: Optional[str] = Field(
        default=None,
        description="URL to user's profile picture"
    )
    timezone: str = Field(
        default="UTC",
        description="User's preferred timezone"
    )
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        # Check for basic complexity
        has_lower = any(c.islower() for c in v)
        has_upper = any(c.isupper() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_lower and has_upper and has_digit):
            raise ValueError(
                'Password must contain at least one lowercase letter, '
                'one uppercase letter, and one digit'
            )
        
        return v
    
    # Reuse validators from User model
    validate_username = User.validate_username
    validate_permissions = User.validate_permissions


class UserUpdate(DatabaseModel):
    """
    Model for updating existing users.
    
    All fields are optional to support partial updates.
    """
    # Basic Information
    email: Optional[EmailStr] = Field(
        default=None,
        description="User's email address"
    )
    first_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="User's first name"
    )
    last_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="User's last name"
    )
    
    # Authorization
    role: Optional[UserRole] = Field(
        default=None,
        description="User's role in the system"
    )
    permissions: Optional[List[str]] = Field(
        default=None,
        description="Additional permissions granted to user"
    )
    
    # Status
    status: Optional[UserStatus] = Field(
        default=None,
        description="Current user status"
    )
    
    # Profile
    profile_picture_url: Optional[str] = Field(
        default=None,
        description="URL to user's profile picture"
    )
    timezone: Optional[str] = Field(
        default=None,
        description="User's preferred timezone"
    )
    
    # Reuse validators from User model
    validate_permissions = User.validate_permissions


class UserLogin(DatabaseModel):
    """
    Model for user login credentials.
    """
    username: str = Field(
        min_length=3,
        max_length=50,
        description="Username for login"
    )
    password: str = Field(
        min_length=1,
        max_length=128,
        description="Password for login"
    )
    
    @field_validator('username')
    @classmethod
    def normalize_username(cls, v: str) -> str:
        """Normalize username for login."""
        return v.lower().strip()


class UserResponse(User):
    """
    Model for user API responses.
    
    Excludes sensitive information like password hash.
    """
    # Override to exclude sensitive fields
    password_hash: str = Field(exclude=True)
    
    class Config:
        from_attributes = True
    
    def to_safe_dict(self) -> dict:
        """Convert to dictionary excluding sensitive information."""
        data = self.model_dump()
        # Remove sensitive fields
        sensitive_fields = ['password_hash', 'login_attempts']
        for field in sensitive_fields:
            data.pop(field, None)
        return data


# Example usage and factory functions
def create_sample_user() -> UserCreate:
    """Create a sample user for testing."""
    return UserCreate(
        username="johndoe",
        email="john.doe@company.com",
        first_name="John",
        last_name="Doe",
        password="SecurePass123",
        role=UserRole.EMPLOYEE,
        permissions=["read_employees", "update_own_profile"],
        timezone="America/New_York"
    )


def create_admin_user() -> UserCreate:
    """Create a sample admin user."""
    return UserCreate(
        username="admin",
        email="admin@company.com",
        first_name="System",
        last_name="Administrator",
        password="AdminPass123!",
        role=UserRole.ADMIN,
        permissions=["*"],  # All permissions
        timezone="UTC"
    )