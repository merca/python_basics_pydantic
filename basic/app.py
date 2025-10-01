"""
🏢 Basic Employee Management with Pydantic

This is the BASIC version demonstrating core Pydantic features:
- Data validation and type safety
- Enums and constraints
- JSON serialization
- Error handling
- Simple Streamlit integration

Learning Objectives:
✅ Understand Pydantic BaseModel
✅ Learn field validation and constraints
✅ Practice with enums and types
✅ See real-time validation in action
✅ JSON import/export capabilities

Run with: streamlit run basic/app.py
"""

import streamlit as st
import json
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, ValidationError, field_validator


# ========================================================================
# 1. PYDANTIC MODELS - Core Learning Focus
# ========================================================================

class Department(str, Enum):
    """Employee department options."""
    ENGINEERING = "engineering"
    MARKETING = "marketing"
    SALES = "sales"
    HR = "hr"
    FINANCE = "finance"
    OPERATIONS = "operations"


class EmploymentStatus(str, Enum):
    """Employment status options."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TERMINATED = "terminated"
    ON_LEAVE = "on_leave"


class Employee(BaseModel):
    """
    Employee model demonstrating Pydantic fundamentals.
    
    Key Learning Points:
    - Type hints with validation
    - Field constraints (min_length, max_length, ge)
    - Optional fields with defaults
    - Email validation
    - Date validation
    - Custom validators
    - Computed properties
    """
    
    # Basic Information
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
        description="Valid email address"
    )
    
    # Optional Information
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
    
    # Employment Information
    employee_id: str = Field(
        min_length=3,
        max_length=10,
        pattern=r'^[A-Z0-9]+$',
        description="Employee ID (uppercase letters and numbers)"
    )
    department: Department
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
    
    # Additional Information
    skills: List[str] = Field(
        default_factory=list,
        description="List of skills"
    )
    
    # Custom Validators - Key Learning Feature
    @field_validator('birth_date')
    @classmethod
    def validate_birth_date(cls, v: Optional[date]) -> Optional[date]:
        """Custom validator: ensure employee is at least 16 years old."""
        if v is None:
            return v
        
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        
        if age < 16:
            raise ValueError(f'Employee must be at least 16 years old (age: {age})')
        if age > 100:
            raise ValueError(f'Age seems unrealistic (age: {age})')
        
        return v
    
    @field_validator('hire_date')
    @classmethod
    def validate_hire_date(cls, v: date) -> date:
        """Custom validator: hire date cannot be in the future."""
        if v > date.today():
            raise ValueError('Hire date cannot be in the future')
        return v
    
    @field_validator('skills')
    @classmethod
    def validate_skills(cls, v: List[str]) -> List[str]:
        """Custom validator: ensure skills are unique and non-empty."""
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
    
    # Computed Properties - Another Key Learning Feature
    @property
    def full_name(self) -> str:
        """Computed property: full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self) -> Optional[int]:
        """Computed property: age in years."""
        if self.birth_date is None:
            return None
        
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )
    
    @property
    def years_of_service(self) -> float:
        """Computed property: years of service."""
        today = date.today()
        delta = today - self.hire_date
        return round(delta.days / 365.25, 1)


# ========================================================================
# 2. IN-MEMORY STORAGE - Simple Data Management
# ========================================================================

def init_session_state():
    """Initialize session state for storing employees."""
    if 'employees' not in st.session_state:
        st.session_state.employees = []
        # Add some sample data for demonstration
        sample_employees = [
            {
                "first_name": "John",
                "last_name": "Doe", 
                "email": "john.doe@company.com",
                "phone": "+1-555-123-4567",
                "birth_date": date(1985, 6, 15),
                "employee_id": "EMP001",
                "department": Department.ENGINEERING,
                "position": "Senior Developer",
                "hire_date": date(2020, 3, 15),
                "salary": Decimal("85000.00"),
                "status": EmploymentStatus.ACTIVE,
                "skills": ["Python", "JavaScript", "SQL"]
            },
            {
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane.smith@company.com", 
                "employee_id": "EMP002",
                "department": Department.MARKETING,
                "position": "Marketing Manager",
                "hire_date": date(2019, 8, 20),
                "salary": Decimal("75000.00"),
                "skills": ["Digital Marketing", "Analytics", "SEO"]
            }
        ]
        
        for emp_data in sample_employees:
            try:
                employee = Employee(**emp_data)
                st.session_state.employees.append(employee)
            except ValidationError as e:
                st.error(f"Error creating sample employee: {e}")


# ========================================================================
# 3. STREAMLIT UI COMPONENTS
# ========================================================================

def render_employee_form():
    """Render form for adding new employees."""
    st.subheader("➕ Add New Employee")
    
    with st.form("add_employee_form", clear_on_submit=True):
        # Basic Information
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name*", max_chars=50)
            email = st.text_input("Email*", help="Must be a valid email address")
            birth_date = st.date_input(
                "Birth Date (Optional)", 
                value=None,
                min_value=date(1920, 1, 1),
                max_value=date.today()
            )
            department = st.selectbox(
                "Department*",
                options=list(Department),
                format_func=lambda x: x.value.title()
            )
            hire_date = st.date_input(
                "Hire Date*",
                value=date.today(),
                max_value=date.today()
            )
        
        with col2:
            last_name = st.text_input("Last Name*", max_chars=50)
            phone = st.text_input("Phone (Optional)")
            employee_id = st.text_input(
                "Employee ID*", 
                help="Use uppercase letters and numbers (e.g., EMP001)",
                max_chars=10
            )
            position = st.text_input("Position*", max_chars=100)
            salary = st.number_input(
                "Salary*", 
                min_value=0.0,
                max_value=1000000.0,
                step=1000.0,
                format="%.2f"
            )
        
        # Status and Skills
        status = st.selectbox(
            "Status",
            options=list(EmploymentStatus),
            format_func=lambda x: x.value.title()
        )
        
        skills_input = st.text_input(
            "Skills (Optional)",
            help="Enter skills separated by commas (e.g., Python, SQL, Docker)"
        )
        skills = [skill.strip() for skill in skills_input.split(",") if skill.strip()] if skills_input else []
        
        # Submit button
        if st.form_submit_button("Add Employee", type="primary"):
            try:
                # Create employee data dictionary
                employee_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "employee_id": employee_id,
                    "department": department,
                    "position": position,
                    "hire_date": hire_date,
                    "salary": Decimal(str(salary)),
                    "status": status,
                    "skills": skills
                }
                
                # Add optional fields if provided
                if phone:
                    employee_data["phone"] = phone
                if birth_date:
                    employee_data["birth_date"] = birth_date
                
                # Create Employee instance (this triggers validation)
                employee = Employee(**employee_data)
                
                # Check for duplicate employee ID
                existing_ids = [emp.employee_id for emp in st.session_state.employees]
                if employee.employee_id in existing_ids:
                    st.error(f"❌ Employee ID '{employee.employee_id}' already exists!")
                    return
                
                # Add to session state
                st.session_state.employees.append(employee)
                st.success(f"✅ Employee '{employee.full_name}' added successfully!")
                st.rerun()
                
            except ValidationError as e:
                st.error("❌ Validation Error:")
                for error in e.errors():
                    field = error['loc'][0] if error['loc'] else 'Unknown'
                    message = error['msg']
                    st.error(f"**{field}**: {message}")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")


def render_employee_list():
    """Render list of employees with details."""
    st.subheader("👥 Employee List")
    
    if not st.session_state.employees:
        st.info("📝 No employees added yet. Use the form above to add employees.")
        return
    
    # Summary metrics
    total_employees = len(st.session_state.employees)
    avg_salary = sum(emp.salary for emp in st.session_state.employees) / total_employees
    departments = {}
    for emp in st.session_state.employees:
        dept = emp.department.value
        departments[dept] = departments.get(dept, 0) + 1
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Employees", total_employees)
    with col2:
        st.metric("Average Salary", f"${avg_salary:,.2f}")
    with col3:
        st.metric("Departments", len(departments))
    
    st.write("**Department Distribution:**", departments)
    
    # Employee table
    st.write("### Employee Details")
    
    for i, employee in enumerate(st.session_state.employees):
        with st.expander(f"👤 {employee.full_name} ({employee.employee_id})", expanded=False):
            # Create two columns for employee details
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Email:** {employee.email}")
                st.write(f"**Phone:** {employee.phone or 'Not provided'}")
                st.write(f"**Department:** {employee.department.value.title()}")
                st.write(f"**Position:** {employee.position}")
                if employee.age:
                    st.write(f"**Age:** {employee.age} years old")
            
            with col2:
                st.write(f"**Hire Date:** {employee.hire_date}")
                st.write(f"**Years of Service:** {employee.years_of_service} years")
                st.write(f"**Salary:** ${employee.salary:,}")
                st.write(f"**Status:** {employee.status.value.title()}")
                if employee.skills:
                    st.write(f"**Skills:** {', '.join(employee.skills)}")
            
            # Action buttons
            col_action1, col_action2 = st.columns(2)
            with col_action1:
                if st.button(f"📊 Show JSON", key=f"json_{i}"):
                    st.json(employee.model_dump(mode='json'), expanded=True)
            
            with col_action2:
                if st.button(f"🗑️ Remove", key=f"remove_{i}", type="secondary"):
                    st.session_state.employees.pop(i)
                    st.success(f"✅ Removed {employee.full_name}")
                    st.rerun()


def render_json_operations():
    """Render JSON import/export functionality."""
    st.subheader("📄 JSON Operations")
    st.write("Learn how Pydantic models work with JSON data.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("#### Export to JSON")
        if st.button("📤 Export All Employees"):
            if st.session_state.employees:
                # Convert all employees to JSON
                employees_json = [emp.model_dump(mode='json') for emp in st.session_state.employees]
                json_str = json.dumps(employees_json, indent=2, default=str)
                
                st.download_button(
                    label="💾 Download JSON File",
                    data=json_str,
                    file_name=f"employees_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                
                st.code(json_str, language="json")
            else:
                st.warning("⚠️ No employees to export")
    
    with col2:
        st.write("#### Import from JSON")
        uploaded_file = st.file_uploader("Choose JSON file", type="json")
        
        if uploaded_file is not None:
            try:
                # Read and parse JSON
                json_data = json.loads(uploaded_file.read())
                
                if isinstance(json_data, list):
                    imported_count = 0
                    errors = []
                    
                    for i, emp_data in enumerate(json_data):
                        try:
                            employee = Employee(**emp_data)
                            
                            # Check for duplicates
                            existing_ids = [emp.employee_id for emp in st.session_state.employees]
                            if employee.employee_id not in existing_ids:
                                st.session_state.employees.append(employee)
                                imported_count += 1
                            else:
                                errors.append(f"Employee {employee.employee_id} already exists")
                        except ValidationError as e:
                            errors.append(f"Row {i+1}: {e}")
                    
                    if imported_count > 0:
                        st.success(f"✅ Imported {imported_count} employees")
                        if errors:
                            st.warning("⚠️ Some employees were skipped:")
                            for error in errors:
                                st.write(f"• {error}")
                        st.rerun()
                    else:
                        st.error("❌ No valid employees found in JSON file")
                        for error in errors:
                            st.error(f"• {error}")
                else:
                    st.error("❌ JSON file must contain a list of employees")
                    
            except json.JSONDecodeError as e:
                st.error(f"❌ Invalid JSON file: {e}")
            except Exception as e:
                st.error(f"❌ Error processing file: {e}")


def render_learning_notes():
    """Render learning notes and Pydantic concepts."""
    st.subheader("📚 Learning Notes")
    
    with st.expander("🎯 What You're Learning", expanded=True):
        st.markdown("""
        **This basic version demonstrates:**
        
        ✅ **Pydantic BaseModel**: The foundation of data validation  
        ✅ **Type Hints**: Python typing for better code quality  
        ✅ **Field Constraints**: min_length, max_length, ge (greater or equal)  
        ✅ **Enums**: Type-safe choices for departments and status  
        ✅ **Custom Validators**: Business logic validation (@field_validator)  
        ✅ **Computed Properties**: Derived fields like age and years_of_service  
        ✅ **JSON Serialization**: Converting models to/from JSON  
        ✅ **Error Handling**: ValidationError handling and user feedback  
        """)
    
    with st.expander("🔍 Key Pydantic Features"):
        st.markdown("""
        **1. Automatic Validation**
        ```python
        employee = Employee(
            first_name="John",      # Validated: min_length=2
            email="invalid-email"   # ValidationError: not a valid email
        )
        ```
        
        **2. Type Conversion**
        ```python
        employee = Employee(salary="75000.50")  # String converted to Decimal
        ```
        
        **3. Custom Validators**
        ```python
        @field_validator('birth_date')
        def validate_birth_date(cls, v):
            # Your custom business logic here
            if age < 16:
                raise ValueError('Too young')
            return v
        ```
        
        **4. JSON Operations**
        ```python
        # To JSON
        json_data = employee.model_dump(mode='json')
        
        # From JSON  
        employee = Employee(**json_data)
        ```
        """)
    
    with st.expander("🚀 Next Steps - Intermediate Version"):
        st.markdown("""
        **Ready to level up? The intermediate version adds:**
        
        🗄️ **Database Integration**: SQLite with SQLAlchemy  
        📁 **File Organization**: Proper module structure  
        🔄 **CRUD Operations**: Create, Read, Update, Delete  
        📊 **Data Relationships**: Foreign keys and joins  
        🛡️ **Advanced Validation**: Cross-field validation  
        📈 **Better UI**: More sophisticated Streamlit components  
        
        *Run the intermediate version to explore these concepts!*
        """)


# ========================================================================
# 4. MAIN APPLICATION
# ========================================================================

def main():
    """Main application function."""
    # Page configuration
    st.set_page_config(
        page_title="Basic Employee Management - Pydantic Learning",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Header
    st.title("🏢 Basic Employee Management")
    st.subheader("Learn Pydantic Fundamentals with Streamlit")
    
    # Learning progress indicator
    st.info("📚 **BASIC VERSION** - Focus: Pydantic fundamentals, validation, and JSON operations")
    
    # Sidebar navigation
    st.sidebar.title("🧭 Navigation")
    page = st.sidebar.radio(
        "Choose a section:",
        ["Add Employee", "View Employees", "JSON Operations", "Learning Notes"],
        index=0
    )
    
    # Version navigation
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 Learning Path")
    st.sidebar.markdown("**Current: 🔰 Basic** (You are here)")
    st.sidebar.markdown("Next: 📊 Intermediate")
    st.sidebar.markdown("Advanced: 🚀 Advanced")
    
    # App statistics
    st.sidebar.markdown("---") 
    st.sidebar.markdown("### 📊 App Stats")
    st.sidebar.metric("Total Employees", len(st.session_state.employees))
    st.sidebar.metric("Lines of Code", "~400")
    st.sidebar.metric("Learning Focus", "Pydantic Basics")
    
    # Render selected page
    if page == "Add Employee":
        render_employee_form()
    elif page == "View Employees":
        render_employee_list()
    elif page == "JSON Operations":
        render_json_operations()
    elif page == "Learning Notes":
        render_learning_notes()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
        <p>🐍 Powered by Pydantic v2</p>
        <p>💾 In-Memory Storage</p>
        <p>Built with ❤️ for Learning</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()