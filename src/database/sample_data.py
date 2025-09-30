"""
Sample Data Generation

This module provides functions to generate and insert sample data
into the database for testing and demonstration purposes.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List
import random
from faker import Faker

from .connection import DatabaseManager
from .models import EmployeeTable, UserTable
from ..models.employee import Department, EmploymentStatus
from ..models.user import UserRole, UserStatus

# Initialize Faker for generating realistic sample data
fake = Faker()


def create_sample_employees(count: int = 20) -> List[EmployeeTable]:
    """
    Generate sample employee data.
    
    Args:
        count: Number of employees to generate
        
    Returns:
        List of EmployeeTable instances
    """
    employees = []
    departments = list(Department)
    statuses = list(EmploymentStatus)
    
    # Predefined skills for different departments
    skills_by_dept = {
        Department.ENGINEERING: [
            "Python", "JavaScript", "SQL", "Docker", "Kubernetes", 
            "React", "Node.js", "AWS", "Machine Learning", "Git"
        ],
        Department.MARKETING: [
            "SEO", "Content Marketing", "Social Media", "Analytics", 
            "Email Marketing", "Copywriting", "Brand Strategy", "PPC"
        ],
        Department.SALES: [
            "CRM", "Lead Generation", "Negotiation", "Customer Relations",
            "Sales Strategy", "Presentations", "Territory Management"
        ],
        Department.HR: [
            "Recruitment", "Employee Relations", "Performance Management",
            "Benefits Administration", "Training", "Compliance"
        ],
        Department.FINANCE: [
            "Financial Analysis", "Budgeting", "Forecasting", "Excel",
            "SAP", "Accounting", "Risk Management", "Audit"
        ],
        Department.OPERATIONS: [
            "Project Management", "Process Optimization", "Supply Chain",
            "Quality Management", "Vendor Relations", "Logistics"
        ]
    }
    
    for i in range(count):
        dept = random.choice(departments)
        status = random.choices(
            statuses,
            weights=[80, 5, 10, 5],  # Most active, few others
            k=1
        )[0]
        
        # Generate hire date (last 5 years)
        hire_date = fake.date_between(start_date='-5y', end_date='today')
        
        # Generate birth date (ages 22-65)
        birth_date = fake.date_between(start_date='-65y', end_date='-22y')
        
        # Generate salary based on department and experience
        base_salary = {
            Department.ENGINEERING: 75000,
            Department.MARKETING: 60000,
            Department.SALES: 65000,
            Department.HR: 55000,
            Department.FINANCE: 70000,
            Department.OPERATIONS: 60000
        }[dept]
        
        # Adjust salary based on experience (years since hire)
        years_exp = (date.today() - hire_date).days / 365.25
        salary_multiplier = 1 + (years_exp * 0.05) + random.uniform(-0.2, 0.3)
        salary = Decimal(str(round(base_salary * salary_multiplier, 2)))
        
        # Select random skills from department
        dept_skills = skills_by_dept[dept]
        num_skills = random.randint(2, min(6, len(dept_skills)))
        skills = random.sample(dept_skills, num_skills)
        
        employee = EmployeeTable(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.email(),
            phone=fake.phone_number(),
            birth_date=birth_date,
            employee_id=f"EMP{i+1:03d}",
            department=dept,
            position=fake.job(),
            hire_date=hire_date,
            salary=salary,
            status=status,
            skills=skills,
            metadata={
                "performance_rating": random.choice(["excellent", "good", "satisfactory", "needs_improvement"]),
                "remote_eligible": random.choice([True, False]),
                "emergency_contact": fake.name(),
                "notes": fake.sentence() if random.random() < 0.3 else ""
            }
        )
        
        employees.append(employee)
    
    return employees


def create_sample_users(count: int = 10) -> List[UserTable]:
    """
    Generate sample user data.
    
    Args:
        count: Number of users to generate
        
    Returns:
        List of UserTable instances
    """
    users = []
    roles = list(UserRole)
    statuses = list(UserStatus)
    
    # Role distribution weights
    role_weights = {
        UserRole.ADMIN: 1,
        UserRole.HR_MANAGER: 2,
        UserRole.MANAGER: 5,
        UserRole.EMPLOYEE: 15,
        UserRole.READONLY: 2
    }
    
    for i in range(count):
        role = random.choices(
            roles,
            weights=[role_weights[r] for r in roles],
            k=1
        )[0]
        
        status = random.choices(
            statuses,
            weights=[85, 5, 5, 5],  # Most active
            k=1
        )[0]
        
        # Generate permissions based on role
        permissions = {
            UserRole.ADMIN: ["*"],  # All permissions
            UserRole.HR_MANAGER: [
                "read_employees", "create_employees", "update_employees",
                "delete_employees", "read_users", "update_users"
            ],
            UserRole.MANAGER: [
                "read_employees", "update_employees", "read_users"
            ],
            UserRole.EMPLOYEE: [
                "read_employees", "update_own_profile"
            ],
            UserRole.READONLY: [
                "read_employees"
            ]
        }[role]
        
        # Simulate some login activity
        last_login = None
        if status == UserStatus.ACTIVE and random.random() < 0.8:
            last_login = fake.date_time_between(start_date='-30d', end_date='now')
        
        user = UserTable(
            username=fake.unique.user_name(),
            email=fake.unique.email(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
            role=role,
            permissions=permissions,
            status=status,
            last_login=last_login,
            login_attempts=random.randint(0, 2) if status == UserStatus.ACTIVE else 0,
            profile_picture_url=fake.image_url() if random.random() < 0.4 else None,
            timezone=random.choice([
                "UTC", "America/New_York", "America/Los_Angeles", 
                "Europe/London", "Asia/Tokyo", "Australia/Sydney"
            ])
        )
        
        users.append(user)
    
    return users


def assign_managers(employees: List[EmployeeTable], session) -> None:
    """
    Assign managers to employees randomly.
    
    Args:
        employees: List of employees to assign managers to
        session: Database session for querying
    """
    # Get potential managers (employees who could be managers)
    potential_managers = [
        emp for emp in employees 
        if "manager" in emp.position.lower() or "senior" in emp.position.lower()
        or emp.department in [Department.HR, Department.OPERATIONS]
    ]
    
    if not potential_managers:
        potential_managers = random.sample(employees, min(5, len(employees)))
    
    for employee in employees:
        # Don't assign manager to themselves
        available_managers = [m for m in potential_managers if m.id != employee.id]
        
        if available_managers and random.random() < 0.7:  # 70% chance of having a manager
            manager = random.choice(available_managers)
            employee.manager_id = manager.id


def insert_sample_data(db_manager: DatabaseManager, 
                      employee_count: int = 50, 
                      user_count: int = 15) -> dict:
    """
    Insert sample data into the database.
    
    Args:
        db_manager: Database manager instance
        employee_count: Number of sample employees to create
        user_count: Number of sample users to create
        
    Returns:
        Dictionary with insertion results
    """
    with db_manager.session_scope() as session:
        # Clear existing data
        session.query(EmployeeTable).delete()
        session.query(UserTable).delete()
        session.commit()
        
        # Generate and insert employees
        employees = create_sample_employees(employee_count)
        session.add_all(employees)
        session.commit()
        
        # Refresh employees to get their IDs
        for emp in employees:
            session.refresh(emp)
        
        # Assign managers
        assign_managers(employees, session)
        session.commit()
        
        # Generate and insert users
        users = create_sample_users(user_count)
        session.add_all(users)
        session.commit()
        
        return {
            "employees_created": len(employees),
            "users_created": len(users),
            "employees_with_managers": sum(1 for emp in employees if emp.manager_id),
            "departments_represented": len(set(emp.department for emp in employees)),
            "user_roles_created": len(set(user.role for user in users))
        }


def create_demo_data() -> dict:
    """
    Create a small set of demo data with specific, realistic examples.
    
    Returns:
        Dictionary with creation results
    """
    # Predefined demo employees
    demo_employees = [
        {
            "first_name": "Alice",
            "last_name": "Johnson",
            "email": "alice.johnson@company.com",
            "phone": "+1-555-0101",
            "birth_date": date(1988, 3, 15),
            "employee_id": "EMP001",
            "department": Department.ENGINEERING,
            "position": "Senior Software Engineer",
            "hire_date": date(2020, 1, 15),
            "salary": Decimal("95000.00"),
            "skills": ["Python", "React", "Docker", "AWS", "Machine Learning"],
            "metadata": {"performance_rating": "excellent", "remote_eligible": True}
        },
        {
            "first_name": "Bob",
            "last_name": "Smith",
            "email": "bob.smith@company.com",
            "phone": "+1-555-0102",
            "birth_date": date(1985, 7, 22),
            "employee_id": "EMP002",
            "department": Department.MARKETING,
            "position": "Marketing Manager",
            "hire_date": date(2019, 6, 1),
            "salary": Decimal("75000.00"),
            "skills": ["SEO", "Content Marketing", "Analytics", "Email Marketing"],
            "metadata": {"performance_rating": "good", "remote_eligible": True}
        },
        {
            "first_name": "Carol",
            "last_name": "Davis",
            "email": "carol.davis@company.com",
            "phone": "+1-555-0103",
            "birth_date": date(1990, 11, 8),
            "employee_id": "EMP003",
            "department": Department.SALES,
            "position": "Sales Representative",
            "hire_date": date(2021, 3, 10),
            "salary": Decimal("60000.00"),
            "skills": ["CRM", "Lead Generation", "Negotiation", "Customer Relations"],
            "metadata": {"performance_rating": "good", "remote_eligible": False}
        }
    ]
    
    # Predefined demo users
    demo_users = [
        {
            "username": "admin",
            "email": "admin@company.com",
            "first_name": "System",
            "last_name": "Administrator",
            "password_hash": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
            "role": UserRole.ADMIN,
            "permissions": ["*"],
            "status": UserStatus.ACTIVE,
            "timezone": "UTC"
        },
        {
            "username": "alice_j",
            "email": "alice.johnson@company.com", 
            "first_name": "Alice",
            "last_name": "Johnson",
            "password_hash": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
            "role": UserRole.EMPLOYEE,
            "permissions": ["read_employees", "update_own_profile"],
            "status": UserStatus.ACTIVE,
            "timezone": "America/New_York"
        }
    ]
    
    from .connection import get_database_manager
    db_manager = get_database_manager()
    
    with db_manager.session_scope() as session:
        # Insert demo employees
        for emp_data in demo_employees:
            employee = EmployeeTable(**emp_data)
            session.add(employee)
        
        # Insert demo users  
        for user_data in demo_users:
            user = UserTable(**user_data)
            session.add(user)
        
        session.commit()
    
    return {
        "demo_employees_created": len(demo_employees),
        "demo_users_created": len(demo_users),
        "note": "Demo data includes admin user (username: admin, password: secret)"
    }


def reset_with_sample_data(employee_count: int = 20, user_count: int = 8) -> dict:
    """
    Reset database and populate with fresh sample data.
    
    Args:
        employee_count: Number of sample employees
        user_count: Number of sample users
        
    Returns:
        Dictionary with reset and insertion results
    """
    from .connection import get_database_manager
    db_manager = get_database_manager()
    
    # Recreate tables
    db_manager.recreate_tables()
    
    # Insert sample data
    result = insert_sample_data(db_manager, employee_count, user_count)
    result["database_reset"] = True
    
    return result