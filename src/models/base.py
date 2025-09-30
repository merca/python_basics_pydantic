"""
Base Models and Mixins

This module provides base classes and mixins that can be used
across different models to ensure consistency.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel as PydanticBaseModel, Field, ConfigDict


class BaseModel(PydanticBaseModel):
    """
    Base model with common configuration.
    
    Features:
    - Snake case field aliases
    - Validation on assignment
    - Extra fields forbidden
    """
    model_config = ConfigDict(
        # Allow field names to be snake_case in Python but camelCase in JSON
        alias_generator=None,
        # Validate values when they are assigned (not just on creation)
        validate_assignment=True,
        # Use enum values instead of enum names in serialization
        use_enum_values=True,
        # Forbid extra fields
        extra='forbid',
        # Enable JSON schema generation
        json_schema_serialization_defaults_required=True,
    )


class TimestampMixin(PydanticBaseModel):
    """
    Mixin to add timestamp fields to models.
    
    Provides created_at and updated_at fields that can be
    automatically managed by the database or application.
    """
    created_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the record was created"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the record was last updated"
    )
    
    model_config = ConfigDict(
        # Allow None values for optional timestamp fields
        validate_default=True,
    )


class DatabaseModel(BaseModel, TimestampMixin):
    """
    Base model for database entities.
    
    Combines BaseModel configuration with timestamp tracking.
    """
    id: Optional[int] = Field(
        default=None,
        description="Unique identifier for the record"
    )
    
    def dict_for_db(self, exclude_unset: bool = True) -> dict:
        """
        Convert model to dictionary suitable for database operations.
        
        Args:
            exclude_unset: Whether to exclude fields that weren't explicitly set
            
        Returns:
            Dictionary representation excluding None values for database
        """
        data = self.model_dump(exclude_unset=exclude_unset)
        # Remove None values to allow database defaults
        return {k: v for k, v in data.items() if v is not None}
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time."""
        self.updated_at = datetime.now()


# Example of model inheritance
class AuditMixin(PydanticBaseModel):
    """
    Mixin for audit trail functionality.
    
    Tracks who created and modified records.
    """
    created_by: Optional[str] = Field(
        default=None,
        description="User who created the record"
    )
    updated_by: Optional[str] = Field(
        default=None,
        description="User who last updated the record"
    )