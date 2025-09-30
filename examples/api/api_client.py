#!/usr/bin/env python3
"""
FastAPI Client Example

This module demonstrates how to interact with the Employee Management API
using both synchronous (requests) and asynchronous (httpx) HTTP clients.

Features:
- Complete CRUD operations for employees
- Error handling and response validation
- Pagination support
- Bulk operations
- Statistics retrieval

Usage:
    python examples/api/api_client.py

Make sure the API server is running:
    uvicorn examples.api.employee_api:app --reload
"""

import asyncio
import sys
import os
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal

import httpx
import requests
from pydantic import ValidationError

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "src"))

from src.models.employee import (
    EmployeeCreate, EmployeeUpdate, Department, EmploymentStatus
)


class EmployeeAPIClient:
    """
    Synchronous client for the Employee Management API using requests.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the API client."""
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health."""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def create_employee(self, employee_data: EmployeeCreate) -> Dict[str, Any]:
        """Create a new employee."""
        response = self.session.post(
            f"{self.base_url}/employees/",
            json=employee_data.model_dump()
        )
        if response.status_code != 201:
            raise Exception(f"Failed to create employee: {response.status_code} - {response.text}")
        return response.json()
    
    def get_employee(self, employee_id: int) -> Dict[str, Any]:
        """Get employee by database ID."""
        response = self.session.get(f"{self.base_url}/employees/{employee_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    
    def get_employee_by_employee_id(self, employee_id: str) -> Dict[str, Any]:
        """Get employee by employee ID (e.g., EMP001)."""
        response = self.session.get(f"{self.base_url}/employees/by-employee-id/{employee_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    
    def list_employees(
        self, 
        skip: int = 0, 
        limit: int = 25,
        department: Optional[Department] = None,
        status: Optional[EmploymentStatus] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """List employees with pagination and filtering."""
        params = {"skip": skip, "limit": limit}
        if department:
            params["department"] = department.value
        if status:
            params["status"] = status.value
        if search:
            params["search"] = search
        
        response = self.session.get(f"{self.base_url}/employees/", params=params)
        response.raise_for_status()
        return response.json()
    
    def update_employee(self, employee_id: int, employee_data: EmployeeUpdate) -> Dict[str, Any]:
        """Update an employee."""
        response = self.session.put(
            f"{self.base_url}/employees/{employee_id}",
            json=employee_data.model_dump(exclude_unset=True)
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    
    def delete_employee(self, employee_id: int) -> bool:
        """Delete an employee."""
        response = self.session.delete(f"{self.base_url}/employees/{employee_id}")
        if response.status_code == 404:
            return False
        response.raise_for_status()
        return True
    
    def get_department_stats(self) -> Dict[str, Any]:
        """Get department statistics."""
        response = self.session.get(f"{self.base_url}/employees/stats/departments")
        response.raise_for_status()
        return response.json()
    
    def get_salary_stats(self) -> Dict[str, Any]:
        """Get salary statistics."""
        response = self.session.get(f"{self.base_url}/employees/stats/salary")
        response.raise_for_status()
        return response.json()
    
    def search_employees(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        department: Optional[Department] = None,
        min_salary: Optional[float] = None,
        max_salary: Optional[float] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search employees with advanced criteria."""
        params = {"limit": limit}
        if name:
            params["name"] = name
        if email:
            params["email"] = email
        if department:
            params["department"] = department.value
        if min_salary is not None:
            params["min_salary"] = min_salary
        if max_salary is not None:
            params["max_salary"] = max_salary
        
        response = self.session.get(f"{self.base_url}/employees/search", params=params)
        response.raise_for_status()
        return response.json()
    
    def bulk_create_employees(self, employees_data: List[EmployeeCreate]) -> Dict[str, Any]:
        """Create multiple employees in bulk."""
        response = self.session.post(
            f"{self.base_url}/employees/bulk",
            json=[emp.model_dump() for emp in employees_data]
        )
        response.raise_for_status()
        return response.json()


class AsyncEmployeeAPIClient:
    """
    Asynchronous client for the Employee Management API using httpx.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the async API client."""
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check API health."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
    
    async def create_employee(self, employee_data: EmployeeCreate) -> Dict[str, Any]:
        """Create a new employee."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/employees/",
                json=employee_data.model_dump(),
                headers=self.headers
            )
            if response.status_code != 201:
                raise Exception(f"Failed to create employee: {response.status_code} - {response.text}")
            return response.json()
    
    async def list_employees(
        self, 
        skip: int = 0, 
        limit: int = 25,
        department: Optional[Department] = None,
        status: Optional[EmploymentStatus] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """List employees with pagination and filtering."""
        params = {"skip": skip, "limit": limit}
        if department:
            params["department"] = department.value
        if status:
            params["status"] = status.value
        if search:
            params["search"] = search
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/employees/", params=params)
            response.raise_for_status()
            return response.json()
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get both department and salary statistics."""
        async with httpx.AsyncClient() as client:
            dept_response = await client.get(f"{self.base_url}/employees/stats/departments")
            salary_response = await client.get(f"{self.base_url}/employees/stats/salary")
            
            dept_response.raise_for_status()
            salary_response.raise_for_status()
            
            return {
                "department_stats": dept_response.json(),
                "salary_stats": salary_response.json()
            }


def create_sample_employees() -> List[EmployeeCreate]:
    """Create sample employee data for testing."""
    employees = [
        EmployeeCreate(
            first_name="Alice",
            last_name="Johnson",
            email="alice.johnson@company.com",
            phone="+1-555-0101",
            birth_date=date(1988, 3, 15),
            employee_id="EMP001",
            department=Department.ENGINEERING,
            position="Senior Software Engineer",
            hire_date=date(2020, 1, 15),
            salary=Decimal("95000.00"),
            skills=["Python", "React", "Docker", "AWS", "Machine Learning"]
        ),
        EmployeeCreate(
            first_name="Bob",
            last_name="Smith",
            email="bob.smith@company.com",
            phone="+1-555-0102",
            birth_date=date(1985, 7, 22),
            employee_id="EMP002",
            department=Department.MARKETING,
            position="Marketing Manager",
            hire_date=date(2019, 6, 1),
            salary=Decimal("75000.00"),
            skills=["SEO", "Content Marketing", "Analytics", "Email Marketing"]
        ),
        EmployeeCreate(
            first_name="Carol",
            last_name="Davis",
            email="carol.davis@company.com",
            phone="+1-555-0103",
            birth_date=date(1990, 11, 8),
            employee_id="EMP003",
            department=Department.SALES,
            position="Sales Representative",
            hire_date=date(2021, 3, 10),
            salary=Decimal("60000.00"),
            skills=["CRM", "Lead Generation", "Negotiation", "Customer Relations"]
        )
    ]
    return employees


def demo_sync_client():
    """Demonstrate synchronous API client usage."""
    print("🔄 Testing Synchronous API Client")
    print("=" * 50)
    
    client = EmployeeAPIClient()
    
    try:
        # Health check
        print("1. Health Check:")
        health = client.health_check()
        print(f"   Status: {health}")
        print()
        
        # Create employees
        print("2. Creating Sample Employees:")
        sample_employees = create_sample_employees()
        created_employees = []
        
        for emp_data in sample_employees:
            try:
                employee = client.create_employee(emp_data)
                created_employees.append(employee)
                print(f"   ✅ Created: {employee['full_name']} (ID: {employee['id']})")
            except Exception as e:
                print(f"   ❌ Failed to create {emp_data.full_name}: {e}")
        print()
        
        # List employees
        print("3. Listing Employees:")
        employees_list = client.list_employees(limit=10)
        print(f"   Total employees: {employees_list['total_count']}")
        print(f"   Current page: {employees_list['page']}")
        for emp in employees_list['items']:
            print(f"   - {emp['full_name']} ({emp['department']}) - ${emp['salary']}")
        print()
        
        # Get specific employee
        if created_employees:
            print("4. Getting Specific Employee:")
            first_employee = created_employees[0]
            employee = client.get_employee(first_employee['id'])
            if employee:
                print(f"   Employee: {employee['full_name']}")
                print(f"   Position: {employee['position']}")
                print(f"   Years of service: {employee['years_of_service']}")
            print()
        
        # Update employee
        if created_employees:
            print("5. Updating Employee:")
            first_employee = created_employees[0]
            update_data = EmployeeUpdate(
                salary=Decimal("100000.00"),
                position="Lead Software Engineer"
            )
            updated_employee = client.update_employee(first_employee['id'], update_data)
            if updated_employee:
                print(f"   Updated salary to: ${updated_employee['salary']}")
                print(f"   Updated position to: {updated_employee['position']}")
            print()
        
        # Search employees
        print("6. Searching Employees:")
        engineering_employees = client.search_employees(
            department=Department.ENGINEERING,
            min_salary=80000.0
        )
        print(f"   Engineering employees with salary >= $80,000:")
        for emp in engineering_employees:
            print(f"   - {emp['full_name']}: ${emp['salary']}")
        print()
        
        # Get statistics
        print("7. Getting Statistics:")
        dept_stats = client.get_department_stats()
        salary_stats = client.get_salary_stats()
        
        print("   Department Statistics:")
        for dept, count in dept_stats['department_stats'].items():
            print(f"   - {dept}: {count} employees")
        
        print("   Salary Statistics:")
        stats = salary_stats['salary_stats']
        print(f"   - Average: ${stats['average']:,.2f}")
        print(f"   - Minimum: ${stats['minimum']:,.2f}")
        print(f"   - Maximum: ${stats['maximum']:,.2f}")
        print()
        
        print("✅ Synchronous client demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in synchronous demo: {e}")


async def demo_async_client():
    """Demonstrate asynchronous API client usage."""
    print("\n🚀 Testing Asynchronous API Client")
    print("=" * 50)
    
    client = AsyncEmployeeAPIClient()
    
    try:
        # Health check
        print("1. Async Health Check:")
        health = await client.health_check()
        print(f"   Status: {health}")
        print()
        
        # List employees
        print("2. Async List Employees:")
        employees_list = await client.list_employees(limit=5)
        print(f"   Found {len(employees_list['items'])} employees")
        for emp in employees_list['items']:
            print(f"   - {emp['full_name']} ({emp['employee_id']})")
        print()
        
        # Get statistics concurrently
        print("3. Async Statistics:")
        stats = await client.get_statistics()
        
        print("   Department Statistics:")
        for dept, count in stats['department_stats']['department_stats'].items():
            print(f"   - {dept}: {count} employees")
        
        print("   Salary Statistics:")
        salary_data = stats['salary_stats']['salary_stats']
        print(f"   - Average: ${salary_data['average']:,.2f}")
        print()
        
        print("✅ Asynchronous client demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in asynchronous demo: {e}")


def main():
    """Run the API client demonstration."""
    print("🌟 Employee Management API Client Demo")
    print("=" * 60)
    print("Make sure the API server is running:")
    print("  uvicorn examples.api.employee_api:app --reload")
    print("=" * 60)
    
    try:
        # Test synchronous client
        demo_sync_client()
        
        # Test asynchronous client
        asyncio.run(demo_async_client())
        
        print("\n🎉 All demos completed successfully!")
        print("\n📖 Next steps:")
        print("- Visit http://localhost:8000/docs for interactive API documentation")
        print("- Try the Streamlit app: streamlit run app.py")
        print("- Explore the source code for more examples")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure the API server is running")
        print("2. Check that the database is properly initialized")
        print("3. Verify network connectivity to localhost:8000")


if __name__ == "__main__":
    main()