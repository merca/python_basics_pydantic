"""
Validation Response Models

This module provides standardized models for handling validation errors
and API responses, ensuring consistent error reporting across the application.
"""

from typing import List, Any, Optional, Dict
from pydantic import Field

from .base import BaseModel


class ErrorDetail(BaseModel):
    """
    Individual error detail model.
    
    Used to represent a single validation error or issue.
    """
    field: Optional[str] = Field(
        default=None,
        description="The field that caused the error, if applicable"
    )
    message: str = Field(
        description="Human-readable error message"
    )
    error_code: Optional[str] = Field(
        default=None,
        description="Machine-readable error code"
    )
    error_type: Optional[str] = Field(
        default=None,
        description="Type of error (validation, business_logic, system, etc.)"
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context about the error"
    )


class ValidationResponse(BaseModel):
    """
    Standard response model for validation operations.
    
    Provides consistent structure for API responses including
    success/failure status, data, and error information.
    """
    success: bool = Field(
        description="Whether the operation was successful"
    )
    message: Optional[str] = Field(
        default=None,
        description="Overall message about the operation"
    )
    data: Optional[Any] = Field(
        default=None,
        description="The actual response data when successful"
    )
    errors: List[ErrorDetail] = Field(
        default_factory=list,
        description="List of errors that occurred during validation"
    )
    warnings: List[ErrorDetail] = Field(
        default_factory=list,
        description="List of warnings (non-blocking issues)"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata about the response"
    )
    
    @classmethod
    def success_response(
        cls, 
        data: Any = None, 
        message: str = "Operation completed successfully",
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'ValidationResponse':
        """Create a successful validation response."""
        return cls(
            success=True,
            message=message,
            data=data,
            metadata=metadata
        )
    
    @classmethod
    def error_response(
        cls, 
        errors: List[ErrorDetail], 
        message: str = "Validation failed",
        data: Any = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'ValidationResponse':
        """Create an error validation response."""
        return cls(
            success=False,
            message=message,
            data=data,
            errors=errors,
            metadata=metadata
        )
    
    @classmethod
    def from_pydantic_error(
        cls, 
        error: Exception, 
        message: str = "Validation error occurred"
    ) -> 'ValidationResponse':
        """Create validation response from Pydantic validation error."""
        errors = []
        
        if hasattr(error, 'errors'):
            # Handle Pydantic ValidationError
            for err in error.errors():
                field_path = '.'.join(str(loc) for loc in err.get('loc', []))
                errors.append(ErrorDetail(
                    field=field_path if field_path else None,
                    message=err.get('msg', str(error)),
                    error_code=err.get('type'),
                    error_type="validation",
                    context=err.get('ctx', {})
                ))
        else:
            # Handle generic exceptions
            errors.append(ErrorDetail(
                message=str(error),
                error_type="validation"
            ))
        
        return cls.error_response(errors=errors, message=message)
    
    def add_error(
        self, 
        message: str, 
        field: Optional[str] = None,
        error_code: Optional[str] = None,
        error_type: str = "validation",
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add an error to the response."""
        self.errors.append(ErrorDetail(
            field=field,
            message=message,
            error_code=error_code,
            error_type=error_type,
            context=context
        ))
        self.success = False
    
    def add_warning(
        self, 
        message: str, 
        field: Optional[str] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a warning to the response."""
        self.warnings.append(ErrorDetail(
            field=field,
            message=message,
            error_code=error_code,
            error_type="warning",
            context=context
        ))
    
    def has_errors(self) -> bool:
        """Check if response has any errors."""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if response has any warnings."""
        return len(self.warnings) > 0
    
    def error_count(self) -> int:
        """Get total number of errors."""
        return len(self.errors)
    
    def warning_count(self) -> int:
        """Get total number of warnings."""
        return len(self.warnings)
    
    def get_errors_by_field(self, field: str) -> List[ErrorDetail]:
        """Get all errors for a specific field."""
        return [error for error in self.errors if error.field == field]
    
    def get_error_messages(self) -> List[str]:
        """Get list of all error messages."""
        return [error.message for error in self.errors]
    
    def get_warning_messages(self) -> List[str]:
        """Get list of all warning messages."""
        return [warning.message for warning in self.warnings]


class PaginatedResponse(BaseModel):
    """
    Response model for paginated data.
    
    Provides consistent structure for paginated API responses.
    """
    items: List[Any] = Field(
        description="List of items in current page"
    )
    total_count: int = Field(
        ge=0,
        description="Total number of items across all pages"
    )
    page: int = Field(
        ge=1,
        description="Current page number (1-based)"
    )
    page_size: int = Field(
        ge=1,
        description="Number of items per page"
    )
    total_pages: int = Field(
        ge=1,
        description="Total number of pages"
    )
    has_next: bool = Field(
        description="Whether there is a next page"
    )
    has_previous: bool = Field(
        description="Whether there is a previous page"
    )
    
    @classmethod
    def create(
        cls,
        items: List[Any],
        total_count: int,
        page: int,
        page_size: int
    ) -> 'PaginatedResponse':
        """Create a paginated response from data."""
        total_pages = max(1, (total_count + page_size - 1) // page_size)
        
        return cls(
            items=items,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )


class BulkOperationResponse(BaseModel):
    """
    Response model for bulk operations.
    
    Provides detailed results for operations that process multiple items.
    """
    total_processed: int = Field(
        ge=0,
        description="Total number of items processed"
    )
    successful_count: int = Field(
        ge=0,
        description="Number of items processed successfully"
    )
    failed_count: int = Field(
        ge=0,
        description="Number of items that failed processing"
    )
    successful_items: List[Any] = Field(
        default_factory=list,
        description="Items that were processed successfully"
    )
    failed_items: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Items that failed with their error details"
    )
    warnings: List[ErrorDetail] = Field(
        default_factory=list,
        description="Warnings generated during bulk operation"
    )
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_processed == 0:
            return 0.0
        return (self.successful_count / self.total_processed) * 100
    
    @property
    def is_fully_successful(self) -> bool:
        """Check if all items were processed successfully."""
        return self.failed_count == 0
    
    @property
    def is_partially_successful(self) -> bool:
        """Check if some (but not all) items were processed successfully."""
        return 0 < self.successful_count < self.total_processed
    
    def add_successful_item(self, item: Any) -> None:
        """Add a successfully processed item."""
        self.successful_items.append(item)
        self.successful_count += 1
        self.total_processed += 1
    
    def add_failed_item(self, item: Any, errors: List[ErrorDetail]) -> None:
        """Add a failed item with its errors."""
        self.failed_items.append({
            'item': item,
            'errors': [error.model_dump() for error in errors]
        })
        self.failed_count += 1
        self.total_processed += 1
    
    def add_warning(self, warning: ErrorDetail) -> None:
        """Add a warning to the bulk operation."""
        self.warnings.append(warning)


# Example factory functions for common responses
def create_not_found_response(resource: str, identifier: str) -> ValidationResponse:
    """Create a standard not found response."""
    return ValidationResponse.error_response(
        errors=[ErrorDetail(
            message=f"{resource} with identifier '{identifier}' was not found",
            error_code="NOT_FOUND",
            error_type="business_logic",
            context={"resource": resource, "identifier": identifier}
        )],
        message="Resource not found"
    )


def create_duplicate_error_response(field: str, value: str) -> ValidationResponse:
    """Create a standard duplicate error response."""
    return ValidationResponse.error_response(
        errors=[ErrorDetail(
            field=field,
            message=f"A record with {field} '{value}' already exists",
            error_code="DUPLICATE_VALUE",
            error_type="business_logic",
            context={"field": field, "value": value}
        )],
        message="Duplicate value detected"
    )


def create_unauthorized_response() -> ValidationResponse:
    """Create a standard unauthorized response."""
    return ValidationResponse.error_response(
        errors=[ErrorDetail(
            message="You are not authorized to perform this action",
            error_code="UNAUTHORIZED",
            error_type="authorization"
        )],
        message="Unauthorized access"
    )