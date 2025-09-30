#!/usr/bin/env python3
"""
FastAPI Employee Management API

A comprehensive example demonstrating how to build RESTful APIs using FastAPI
with Pydantic models for request/response validation and SQLite for persistence.

Features:
- Complete CRUD operations for employees
- Automatic API documentation with Swagger/OpenAPI
- Pydantic model validation for requests and responses
- Database integration with SQLAlchemy
- Error handling and proper HTTP status codes
- Pagination and filtering
- Authentication ready structure

Run with: uvicorn examples.api.employee_api:app --reload
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Path, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from sqlalchemy.orm import Session
import sys
import os
from datetime import date

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "src"))

# Import our modules
from src.models.employee import (
    Employee, EmployeeCreate, EmployeeUpdate, EmployeeResponse,
    Department, EmploymentStatus
)
from src.models.validation import ValidationResponse, PaginatedResponse
from src.database.connection import get_database_manager, initialize_database
from src.database.repository import EmployeeRepository

# Initialize FastAPI app
app = FastAPI(
    title="Employee Management API",
    description="A comprehensive API for managing employee data with Pydantic validation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    try:
        initialize_database(create_tables=True, sample_data=False)
    except Exception as e:
        print(f"Database initialization failed: {e}")

# Dependency to get database session
def get_db() -> Session:
    """Dependency for database session."""
    db_manager = get_database_manager()
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()

def get_employee_repo(db: Session = Depends(get_db)) -> EmployeeRepository:
    """Dependency for employee repository."""
    return EmployeeRepository(db)

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Employee API is running"}

# Employee endpoints
@app.post(
    "/employees/",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Employees"],
    summary="Create a new employee",
    description="Create a new employee with validation"
)
async def create_employee(
    employee_data: EmployeeCreate,
    repo: EmployeeRepository = Depends(get_employee_repo)
):
    """Create a new employee."""
    try:
        employee = repo.create(employee_data)
        return employee
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.get(
    "/employees/",
    response_model=PaginatedResponse,
    tags=["Employees"],
    summary="List employees",
    description="Get a paginated list of employees with optional filtering"
)
async def list_employees(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(25, ge=1, le=100, description="Number of records to return"),
    department: Optional[Department] = Query(None, description="Filter by department"),
    status: Optional[EmploymentStatus] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in name, email, or employee ID"),
    repo: EmployeeRepository = Depends(get_employee_repo)
):
    """Get a list of employees with pagination and filtering."""
    try:
        employees = repo.list(
            skip=skip,
            limit=limit,
            department=department,
            status=status,
            search=search
        )
        return employees
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.get(
    "/employees/{employee_id}",
    response_model=EmployeeResponse,
    tags=["Employees"],
    summary="Get employee by ID",
    description="Retrieve a specific employee by their database ID"
)
async def get_employee(
    employee_id: int = Path(..., gt=0, description="The ID of the employee to retrieve"),
    repo: EmployeeRepository = Depends(get_employee_repo)
):
    """Get an employee by ID."""
    employee = repo.get(employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found"
        )
    return employee

@app.get(
    "/employees/by-employee-id/{employee_id}",
    response_model=EmployeeResponse,
    tags=["Employees"],
    summary="Get employee by employee ID",
    description="Retrieve a specific employee by their employee ID (e.g., EMP001)"
)
async def get_employee_by_employee_id(
    employee_id: str = Path(..., description="The employee ID to retrieve"),
    repo: EmployeeRepository = Depends(get_employee_repo)
):
    """Get an employee by employee ID."""
    employee = repo.get_by_employee_id(employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with employee ID {employee_id} not found"
        )
    return employee

@app.put(
    "/employees/{employee_id}",
    response_model=EmployeeResponse,
    tags=["Employees"],
    summary="Update employee",
    description="Update an existing employee with partial data"
)
async def update_employee(
    employee_id: int = Path(..., gt=0, description="The ID of the employee to update"),
    employee_data: EmployeeUpdate = None,
    repo: EmployeeRepository = Depends(get_employee_repo)
):
    """Update an employee."""
    try:
        updated_employee = repo.update(employee_id, employee_data)
        if not updated_employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with ID {employee_id} not found"
            )
        return updated_employee
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.delete(
    "/employees/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Employees"],
    summary="Delete employee",
    description="Delete an employee from the system"
)
async def delete_employee(
    employee_id: int = Path(..., gt=0, description="The ID of the employee to delete"),
    repo: EmployeeRepository = Depends(get_employee_repo)
):
    """Delete an employee."""
    success = repo.delete(employee_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found"
        )
    return None

# Statistics endpoints
@app.get(
    "/employees/stats/departments",
    tags=["Statistics"],
    summary="Get department statistics",
    description="Get employee count by department"
)
async def get_department_stats(
    repo: EmployeeRepository = Depends(get_employee_repo)
):
    """Get department statistics."""
    try:
        stats = repo.get_department_stats()
        return {"department_stats": stats}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.get(
    "/employees/stats/salary",
    tags=["Statistics"],
    summary="Get salary statistics",
    description="Get salary statistics (min, max, average)"
)
async def get_salary_stats(
    repo: EmployeeRepository = Depends(get_employee_repo)
):
    """Get salary statistics."""
    try:
        stats = repo.get_salary_stats()
        return {"salary_stats": stats}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.get(
    "/employees/{manager_id}/direct-reports",
    response_model=List[EmployeeResponse],
    tags=["Employees"],
    summary="Get direct reports",
    description="Get all employees who report to a specific manager"
)
async def get_direct_reports(
    manager_id: int = Path(..., gt=0, description="The manager's employee ID"),
    repo: EmployeeRepository = Depends(get_employee_repo)
):
    """Get direct reports for a manager."""
    try:
        employees = repo.get_employees_by_manager(manager_id)
        return employees
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Bulk operations
@app.post(
    "/employees/bulk",
    tags=["Bulk Operations"],
    summary="Create multiple employees",
    description="Create multiple employees in a single request"
)
async def create_employees_bulk(
    employees_data: List[EmployeeCreate],
    repo: EmployeeRepository = Depends(get_employee_repo)
):
    """Create multiple employees."""
    results = {
        "created": [],
        "errors": [],
        "total_processed": len(employees_data)
    }
    
    for i, employee_data in enumerate(employees_data):
        try:
            employee = repo.create(employee_data)
            results["created"].append({
                "index": i,
                "employee": employee
            })
        except Exception as e:
            results["errors"].append({
                "index": i,
                "employee_data": employee_data,
                "error": str(e)
            })
    
    results["created_count"] = len(results["created"])
    results["error_count"] = len(results["errors"])
    
    return results

# Search endpoints
@app.get(
    "/employees/search",
    response_model=List[EmployeeResponse],
    tags=["Search"],
    summary="Search employees",
    description="Advanced employee search with multiple criteria"
)
async def search_employees(
    name: Optional[str] = Query(None, description="Search by name (first or last)"),
    email: Optional[str] = Query(None, description="Search by email"),
    department: Optional[Department] = Query(None, description="Filter by department"),
    min_salary: Optional[float] = Query(None, ge=0, description="Minimum salary"),
    max_salary: Optional[float] = Query(None, ge=0, description="Maximum salary"),
    hire_date_from: Optional[date] = Query(None, description="Hired after this date"),
    hire_date_to: Optional[date] = Query(None, description="Hired before this date"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    repo: EmployeeRepository = Depends(get_employee_repo)
):
    """Advanced employee search."""
    try:
        # Build search query
        search_terms = []
        if name:
            search_terms.append(name)
        if email:
            search_terms.append(email)
        
        search_query = " ".join(search_terms) if search_terms else None
        
        # Get filtered results
        result = repo.list(
            limit=limit,
            department=department,
            search=search_query
        )
        
        employees = result.items
        
        # Additional filtering (in a real app, this would be done at the database level)
        if min_salary is not None:
            employees = [emp for emp in employees if float(emp.salary) >= min_salary]
        if max_salary is not None:
            employees = [emp for emp in employees if float(emp.salary) <= max_salary]
        if hire_date_from:
            employees = [emp for emp in employees if emp.hire_date >= hire_date_from]
        if hire_date_to:
            employees = [emp for emp in employees if emp.hire_date <= hire_date_to]
        
        return employees[:limit]  # Ensure we don't exceed the limit
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "type": "validation_error"}
    )

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found", "type": "not_found"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "employee_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )