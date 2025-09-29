import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, ValidationError, validator
import json

# Configure page
st.set_page_config(
    page_title="Python Basics with Pydantic - Streamlit Demo",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Pydantic Models for the app
class Employee(BaseModel):
    """Employee data model with validation"""
    id: int = Field(gt=0, description="Employee ID must be positive")
    name: str = Field(min_length=2, max_length=100, description="Full name")
    email: str = Field(description="Valid email address")
    department: str = Field(description="Department name")
    salary: float = Field(gt=0, le=1000000, description="Annual salary")
    hire_date: date = Field(description="Date of hire")
    is_active: bool = Field(default=True, description="Employment status")
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v or '.' not in v.split('@')[1]:
            raise ValueError('Please enter a valid email address')
        return v.lower()
    
    @validator('name')
    def validate_name(cls, v):
        if not v.replace(' ', '').replace('-', '').replace("'", '').isalpha():
            raise ValueError('Name should only contain letters, spaces, hyphens, and apostrophes')
        return v.title()

class EmployeeStats(BaseModel):
    """Statistics for employee data"""
    total_employees: int = Field(ge=0)
    avg_salary: float = Field(ge=0)
    departments: List[str]
    active_employees: int = Field(ge=0)
    salary_by_department: dict

def validate_employee_data(data: dict) -> tuple:
    """Validate employee data and return result"""
    try:
        employee = Employee(**data)
        return True, employee, None
    except ValidationError as e:
        errors = []
        for error in e.errors():
            field = error['loc'][0]
            message = error['msg']
            errors.append(f"{field}: {message}")
        return False, None, errors

def calculate_stats(employees: List[Employee]) -> EmployeeStats:
    """Calculate statistics from employee list"""
    if not employees:
        return EmployeeStats(
            total_employees=0,
            avg_salary=0,
            departments=[],
            active_employees=0,
            salary_by_department={}
        )
    
    total = len(employees)
    avg_sal = sum(emp.salary for emp in employees) / total
    depts = list(set(emp.department for emp in employees))
    active = sum(1 for emp in employees if emp.is_active)
    
    # Salary by department
    dept_salaries = {}
    for dept in depts:
        dept_employees = [emp for emp in employees if emp.department == dept]
        dept_salaries[dept] = sum(emp.salary for emp in dept_employees) / len(dept_employees)
    
    return EmployeeStats(
        total_employees=total,
        avg_salary=avg_sal,
        departments=depts,
        active_employees=active,
        salary_by_department=dept_salaries
    )

# Main app
def main():
    st.title("🐍 Python Basics with Pydantic - Interactive Demo")
    st.markdown("### Demonstrating data validation and visualization with Streamlit")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a section:",
        ["Employee Data Entry", "Data Validation Demo", "Analytics Dashboard", "About Pydantic"]
    )
    
    if page == "Employee Data Entry":
        employee_entry_page()
    elif page == "Data Validation Demo":
        validation_demo_page()
    elif page == "Analytics Dashboard":
        analytics_dashboard_page()
    else:
        about_pydantic_page()

def employee_entry_page():
    st.header("👥 Employee Data Entry")
    st.markdown("Enter employee information with real-time Pydantic validation:")
    
    # Initialize session state
    if 'employees' not in st.session_state:
        st.session_state.employees = []
    
    # Form for employee entry
    with st.form("employee_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            emp_id = st.number_input("Employee ID", min_value=1, value=1)
            name = st.text_input("Full Name", placeholder="John Doe")
            email = st.text_input("Email", placeholder="john.doe@company.com")
        
        with col2:
            department = st.selectbox(
                "Department",
                ["Engineering", "Marketing", "Sales", "HR", "Finance"]
            )
            salary = st.number_input("Annual Salary ($)", min_value=0, value=50000)
            hire_date = st.date_input("Hire Date", value=date.today())
        
        is_active = st.checkbox("Active Employee", value=True)
        submit = st.form_submit_button("Add Employee", type="primary")
        
        if submit:
            employee_data = {
                "id": emp_id,
                "name": name,
                "email": email,
                "department": department,
                "salary": salary,
                "hire_date": hire_date,
                "is_active": is_active
            }
            
            is_valid, employee, errors = validate_employee_data(employee_data)
            
            if is_valid:
                # Check for duplicate ID
                existing_ids = [emp.id for emp in st.session_state.employees]
                if emp_id in existing_ids:
                    st.error(f"Employee ID {emp_id} already exists!")
                else:
                    st.session_state.employees.append(employee)
                    st.success(f"✅ Added {employee.name} successfully!")
                    st.balloons()
            else:
                st.error("❌ Validation failed:")
                for error in errors:
                    st.error(f"• {error}")
    
    # Display current employees
    if st.session_state.employees:
        st.subheader("Current Employees")
        
        # Convert to DataFrame for display
        employees_data = []
        for emp in st.session_state.employees:
            employees_data.append({
                "ID": emp.id,
                "Name": emp.name,
                "Email": emp.email,
                "Department": emp.department,
                "Salary": f"${emp.salary:,}",
                "Hire Date": emp.hire_date.strftime("%Y-%m-%d"),
                "Status": "Active" if emp.is_active else "Inactive"
            })
        
        df = pd.DataFrame(employees_data)
        st.dataframe(df, use_container_width=True)
        
        # Clear all button
        if st.button("🗑️ Clear All Employees"):
            st.session_state.employees = []
            st.rerun()

def validation_demo_page():
    st.header("🔍 Data Validation Demo")
    st.markdown("Test Pydantic validation with various invalid inputs:")
    
    # Sample invalid data
    invalid_examples = [
        {
            "name": "Invalid Email",
            "data": {
                "id": 1,
                "name": "John Doe",
                "email": "invalid-email",  # Invalid
                "department": "Engineering",
                "salary": 75000,
                "hire_date": "2023-01-15"
            }
        },
        {
            "name": "Negative Salary",
            "data": {
                "id": 2,
                "name": "Jane Smith",
                "email": "jane@company.com",
                "department": "Marketing",
                "salary": -50000,  # Invalid
                "hire_date": "2023-02-01"
            }
        },
        {
            "name": "Empty Name",
            "data": {
                "id": 3,
                "name": "",  # Invalid
                "email": "someone@company.com",
                "department": "Sales",
                "salary": 60000,
                "hire_date": "2023-03-01"
            }
        },
        {
            "name": "Invalid ID",
            "data": {
                "id": -1,  # Invalid
                "name": "Bob Wilson",
                "email": "bob@company.com",
                "department": "HR",
                "salary": 65000,
                "hire_date": "2023-04-01"
            }
        }
    ]
    
    st.subheader("Try Invalid Data Examples")
    
    for i, example in enumerate(invalid_examples):
        with st.expander(f"Example {i+1}: {example['name']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Input Data:**")
                st.json(example['data'])
            
            with col2:
                is_valid, employee, errors = validate_employee_data(example['data'])
                
                if is_valid:
                    st.success("✅ Valid data!")
                    st.json(employee.dict())
                else:
                    st.error("❌ Validation errors:")
                    for error in errors:
                        st.error(f"• {error}")
    
    # Custom validation test
    st.subheader("Test Your Own Data")
    
    json_input = st.text_area(
        "Enter JSON data to validate:",
        value='{\n  "id": 1,\n  "name": "Test User",\n  "email": "test@example.com",\n  "department": "Engineering",\n  "salary": 75000,\n  "hire_date": "2023-01-01"\n}',
        height=200
    )
    
    if st.button("Validate JSON", type="primary"):
        try:
            data = json.loads(json_input)
            is_valid, employee, errors = validate_employee_data(data)
            
            if is_valid:
                st.success("✅ Valid data!")
                st.json(employee.dict(), expanded=True)
            else:
                st.error("❌ Validation errors:")
                for error in errors:
                    st.error(f"• {error}")
        
        except json.JSONDecodeError as e:
            st.error(f"❌ Invalid JSON: {str(e)}")

def analytics_dashboard_page():
    st.header("📊 Analytics Dashboard")
    
    if not st.session_state.get('employees'):
        st.warning("⚠️ No employee data available. Please add employees in the 'Employee Data Entry' section first.")
        return
    
    employees = st.session_state.employees
    stats = calculate_stats(employees)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Employees",
            stats.total_employees,
            delta=None
        )
    
    with col2:
        st.metric(
            "Average Salary",
            f"${stats.avg_salary:,.0f}",
            delta=None
        )
    
    with col3:
        st.metric(
            "Active Employees",
            stats.active_employees,
            delta=f"{stats.active_employees - (stats.total_employees - stats.active_employees):+d}"
        )
    
    with col4:
        st.metric(
            "Departments",
            len(stats.departments),
            delta=None
        )
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Salary by department
        if stats.salary_by_department:
            fig_salary = px.bar(
                x=list(stats.salary_by_department.keys()),
                y=list(stats.salary_by_department.values()),
                title="Average Salary by Department",
                labels={'x': 'Department', 'y': 'Average Salary ($)'},
                color=list(stats.salary_by_department.values()),
                color_continuous_scale='viridis'
            )
            fig_salary.update_layout(showlegend=False)
            st.plotly_chart(fig_salary, use_container_width=True)
    
    with col2:
        # Employee count by department
        dept_counts = {}
        for emp in employees:
            dept_counts[emp.department] = dept_counts.get(emp.department, 0) + 1
        
        fig_count = px.pie(
            values=list(dept_counts.values()),
            names=list(dept_counts.keys()),
            title="Employee Distribution by Department"
        )
        st.plotly_chart(fig_count, use_container_width=True)
    
    # Detailed data
    st.subheader("Employee Details")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        dept_filter = st.selectbox(
            "Filter by Department",
            ["All"] + stats.departments
        )
    
    with col2:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Active", "Inactive"]
        )
    
    with col3:
        salary_range = st.slider(
            "Salary Range ($)",
            min_value=0,
            max_value=int(max(emp.salary for emp in employees)),
            value=(0, int(max(emp.salary for emp in employees)))
        )
    
    # Apply filters
    filtered_employees = employees
    
    if dept_filter != "All":
        filtered_employees = [emp for emp in filtered_employees if emp.department == dept_filter]
    
    if status_filter != "All":
        is_active_filter = status_filter == "Active"
        filtered_employees = [emp for emp in filtered_employees if emp.is_active == is_active_filter]
    
    filtered_employees = [
        emp for emp in filtered_employees 
        if salary_range[0] <= emp.salary <= salary_range[1]
    ]
    
    # Display filtered data
    if filtered_employees:
        filtered_data = []
        for emp in filtered_employees:
            filtered_data.append({
                "ID": emp.id,
                "Name": emp.name,
                "Email": emp.email,
                "Department": emp.department,
                "Salary": emp.salary,
                "Hire Date": emp.hire_date,
                "Status": "Active" if emp.is_active else "Inactive"
            })
        
        df_filtered = pd.DataFrame(filtered_data)
        st.dataframe(df_filtered, use_container_width=True)
        
        # Download option
        csv = df_filtered.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"employees_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No employees match the current filters.")

def about_pydantic_page():
    st.header("🔗 About Pydantic")
    
    st.markdown("""
    ### What is Pydantic?
    
    Pydantic is a Python library that provides data validation and parsing using Python type annotations. 
    It's particularly useful for:
    
    - **Data Validation**: Automatic validation of input data
    - **Type Safety**: Runtime type checking with clear error messages
    - **JSON Serialization**: Easy conversion between Python objects and JSON
    - **IDE Support**: Better autocomplete and error detection
    - **Documentation**: Self-documenting code with clear schemas
    
    ### Key Features Demonstrated in this App:
    
    1. **Field Validation**: Using `Field()` with constraints like `min_length`, `max_length`, `gt`, `le`
    2. **Custom Validators**: Using `@validator` decorators for complex business logic
    3. **Error Handling**: Graceful handling of validation errors with user-friendly messages
    4. **Data Models**: Structured data representation with type hints
    5. **JSON Integration**: Easy serialization and deserialization
    
    ### Code Examples:
    """)
    
    st.code("""
# Simple Pydantic model
class Employee(BaseModel):
    id: int = Field(gt=0, description="Employee ID must be positive")
    name: str = Field(min_length=2, max_length=100)
    email: str
    salary: float = Field(gt=0, le=1000000)
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Please enter a valid email address')
        return v.lower()

# Usage
try:
    employee = Employee(
        id=1,
        name="John Doe",
        email="john@company.com",
        salary=75000
    )
    print(employee.json())  # Convert to JSON
except ValidationError as e:
    print(f"Validation error: {e}")
    """, language="python")
    
    st.markdown("""
    ### Benefits for Real Applications:
    
    - **API Development**: Perfect for FastAPI and REST API validation
    - **Data Pipelines**: Ensure data quality in ETL processes
    - **Configuration Management**: Validate application configuration
    - **Database Models**: Type-safe database interactions
    - **Web Forms**: Validate user input in web applications
    
    ### Next Steps:
    
    1. Explore the other sections of this app to see Pydantic in action
    2. Check out the notebook examples for more advanced patterns
    3. Try integrating Pydantic in your own Python projects
    4. Learn about Pydantic V2 features and performance improvements
    
    ### Resources:
    
    - [Pydantic Documentation](https://docs.pydantic.dev/)
    - [GitHub Repository](https://github.com/pydantic/pydantic)
    - [FastAPI Integration](https://fastapi.tiangolo.com/)
    """)

if __name__ == "__main__":
    main()