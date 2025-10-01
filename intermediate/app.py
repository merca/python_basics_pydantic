"""
🏢 Intermediate Employee Management with Pydantic + SQLAlchemy

This is the INTERMEDIATE version demonstrating:
- Pydantic models with database integration
- SQLAlchemy ORM for data persistence
- Model inheritance and composition
- CRUD operations with validation
- Basic data visualization
- Proper file organization

Learning Objectives:
✅ Understand Pydantic + SQLAlchemy integration
✅ Learn database session management
✅ Practice model inheritance patterns
✅ Implement CRUD operations
✅ Work with database relationships
✅ Create basic analytics and charts

Run with: streamlit run intermediate/app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime
from decimal import Decimal
from pydantic import ValidationError

# Import our models and database functions
from models.employee import (
    Employee, EmployeeCreate, EmployeeUpdate, Department, 
    EmploymentStatus, CompanyStats
)
from database.connection import (
    get_database_manager, init_database_with_sample_data,
    get_all_employees, get_employee_by_id, create_employee, delete_employee
)
from database.models import get_database_stats


def init_app():
    """Initialize the application and database."""
    # Page configuration
    st.set_page_config(
        page_title="Intermediate Employee Management - Pydantic + SQLAlchemy",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize database
    try:
        db = get_database_manager()
        
        # Check if database has data, if not, offer to create sample data
        with st.sidebar:
            if st.button("🔄 Initialize Sample Data"):
                init_database_with_sample_data()
                st.success("Sample data created!")
                st.rerun()
    
    except Exception as e:
        st.error(f"Database initialization error: {e}")


def render_dashboard():
    """Render the main dashboard with analytics."""
    st.subheader("📊 Company Dashboard")
    
    try:
        # Get database statistics
        db = get_database_manager()
        with db.session_scope() as session:
            stats = get_database_stats(session)
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Employees", stats['total_employees'])
        with col2:
            st.metric("Active Employees", stats['active_employees'])
        with col3:
            if stats['salary_stats']['average'] > 0:
                st.metric("Average Salary", f"${stats['salary_stats']['average']:,.2f}")
            else:
                st.metric("Average Salary", "N/A")
        with col4:
            if stats['salary_stats']['total_payroll'] > 0:
                st.metric("Total Payroll", f"${stats['salary_stats']['total_payroll']:,.2f}")
            else:
                st.metric("Total Payroll", "N/A")
        
        # Department distribution chart
        if stats['department_distribution']:
            st.subheader("📈 Department Distribution")
            
            dept_df = pd.DataFrame(
                list(stats['department_distribution'].items()),
                columns=['Department', 'Employee Count']
            )
            
            fig = px.pie(
                dept_df, 
                values='Employee Count', 
                names='Department',
                title="Employees by Department"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent activity or additional charts could go here
        
    except Exception as e:
        st.error(f"Error loading dashboard: {e}")
        st.info("💡 Try initializing sample data using the button in the sidebar.")


def render_add_employee():
    """Render the add employee form."""
    st.subheader("➕ Add New Employee")
    
    with st.form("add_employee_form", clear_on_submit=True):
        # Personal Information
        st.markdown("**Personal Information**")
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name*", max_chars=50)
            email = st.text_input("Email*")
            birth_date = st.date_input(
                "Birth Date (Optional)",
                value=None,
                min_value=date(1920, 1, 1),
                max_value=date.today().replace(year=date.today().year - 16)
            )
        
        with col2:
            last_name = st.text_input("Last Name*", max_chars=50)
            phone = st.text_input("Phone (Optional)")
        
        # Employment Information
        st.markdown("**Employment Information**")
        col3, col4 = st.columns(2)
        
        with col3:
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
            status = st.selectbox(
                "Status*",
                options=list(EmploymentStatus),
                format_func=lambda x: x.value.title()
            )
        
        with col4:
            position = st.text_input("Position*", max_chars=100)
            salary = st.number_input(
                "Salary*",
                min_value=0.0,
                max_value=1000000.0,
                step=1000.0,
                format="%.2f"
            )
        
        # Additional Information
        st.markdown("**Additional Information**")
        skills_input = st.text_input(
            "Skills (comma-separated)",
            help="e.g., Python, SQL, Project Management"
        )
        skills = [s.strip() for s in skills_input.split(",") if s.strip()] if skills_input else []
        
        notes = st.text_area("Notes (Optional)", max_chars=500)
        
        # Submit button
        if st.form_submit_button("Add Employee", type="primary"):
            try:
                # Create employee data
                employee_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "department": department,
                    "position": position,
                    "hire_date": hire_date,
                    "salary": Decimal(str(salary)),
                    "status": status,
                    "skills": skills
                }
                
                # Add optional fields
                if phone:
                    employee_data["phone"] = phone
                if birth_date:
                    employee_data["birth_date"] = birth_date
                if notes:
                    employee_data["notes"] = notes
                
                # Validate with Pydantic first
                employee_create = EmployeeCreate(**employee_data)
                
                # Create in database
                result = create_employee(employee_create.model_dump())
                
                st.success(f"✅ Employee '{result['full_name']}' (ID: {result['employee_id']}) added successfully!")
                st.rerun()
                
            except ValidationError as e:
                st.error("❌ Validation Error:")
                for error in e.errors():
                    field = error['loc'][0] if error['loc'] else 'Unknown'
                    message = error['msg']
                    st.error(f"**{field}**: {message}")
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


def render_employee_list():
    """Render the employee list with basic CRUD operations."""
    st.subheader("👥 Employee List")
    
    try:
        employees = get_all_employees()
        
        if not employees:
            st.info("📝 No employees found. Add some employees or initialize sample data.")
            return
        
        # Display employee list
        for i, emp in enumerate(employees):
            with st.expander(f"👤 {emp['full_name']} ({emp['employee_id']})", expanded=False):
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write(f"**Email:** {emp['email']}")
                    st.write(f"**Department:** {emp['department'].title()}")
                    st.write(f"**Position:** {emp['position']}")
                
                with col2:
                    st.write(f"**Salary:** ${emp['salary']:,.2f}")
                    st.write(f"**Status:** {emp['status'].title()}")
                    st.write(f"**Years of Service:** {emp['years_of_service']}")
                
                with col3:
                    if st.button(f"🗑️ Delete", key=f"delete_{emp['id']}", type="secondary"):
                        if delete_employee(emp['id']):
                            st.success(f"Deleted {emp['full_name']}")
                            st.rerun()
                        else:
                            st.error("Failed to delete employee")
                    
                    if st.button(f"📊 Details", key=f"details_{emp['id']}"):
                        # Show detailed employee information
                        detailed_emp = get_employee_by_id(emp['id'])
                        if detailed_emp:
                            st.json(detailed_emp)
    
    except Exception as e:
        st.error(f"Error loading employees: {e}")


def render_database_info():
    """Render database information and management tools."""
    st.subheader("🗄️ Database Management")
    
    try:
        db = get_database_manager()
        db_info = db.get_info()
        
        # Database status
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Database Information:**")
            st.write(f"URL: `{db_info['database_url']}`")
            st.write(f"Employee Count: {db_info.get('employee_count', 0)}")
            st.write(f"Connection Status: {'✅ Connected' if db_info['connection_test'] else '❌ Failed'}")
        
        with col2:
            st.write("**Management Actions:**")
            
            if st.button("🔄 Recreate Tables"):
                db.recreate_tables()
                st.success("Database tables recreated!")
                st.rerun()
            
            if st.button("📊 Initialize Sample Data"):
                init_database_with_sample_data()
                st.success("Sample data initialized!")
                st.rerun()
        
        # Show raw database info
        with st.expander("🔧 Technical Details"):
            st.json(db_info)
    
    except Exception as e:
        st.error(f"Database management error: {e}")


def render_learning_notes():
    """Render learning notes for the intermediate version."""
    st.subheader("📚 Intermediate Learning Notes")
    
    with st.expander("🎯 What You're Learning", expanded=True):
        st.markdown("""
        **This intermediate version demonstrates:**
        
        ✅ **Pydantic + SQLAlchemy Integration** - Models that work with databases  
        ✅ **Model Inheritance** - BaseEmployee → EmployeeCreate/Update/Response  
        ✅ **Database Sessions** - Proper transaction management  
        ✅ **CRUD Operations** - Create, Read, Update, Delete with validation  
        ✅ **Foreign Key Relationships** - Manager relationships  
        ✅ **Cross-field Validation** - Business rules across multiple fields  
        ✅ **Data Analytics** - Basic statistics and visualizations  
        ✅ **File Organization** - Proper module structure  
        """)
    
    with st.expander("🔍 Key Concepts"):
        st.markdown("""
        **1. Pydantic + SQLAlchemy Pattern**
        ```python
        # Pydantic model for validation
        class EmployeeCreate(BaseModel):
            name: str = Field(min_length=2)
            email: EmailStr
        
        # SQLAlchemy model for database
        class EmployeeTable(Base):
            name = Column(String(50), nullable=False)
            email = Column(String(255), unique=True)
        ```
        
        **2. Database Session Management**
        ```python
        with db.session_scope() as session:
            employee = EmployeeTable(**validated_data)
            session.add(employee)
            # Auto-commit and cleanup
        ```
        
        **3. Model Inheritance**
        ```python
        class BaseEmployee(BaseModel):
            # Common fields and validation
        
        class EmployeeCreate(BaseEmployee):
            # Fields needed for creation
        
        class Employee(BaseEmployee):
            # Full model with database fields
        ```
        """)
    
    with st.expander("🚀 Next Steps - Advanced Version"):
        st.markdown("""
        **Ready for more complexity? The advanced version adds:**
        
        🏗️ **Service Layer Architecture** - Business logic separation  
        📦 **Repository Pattern** - Data access abstraction  
        🔧 **Dependency Injection** - Flexible component management  
        📊 **Advanced Analytics** - Complex queries and reporting  
        🛡️ **Error Handling** - Comprehensive error management  
        🔄 **Background Tasks** - Async operations and caching  
        
        *The advanced version shows enterprise-level patterns!*
        """)


def main():
    """Main application function."""
    # Initialize the app
    init_app()
    
    # Header
    st.title("🏢 Intermediate Employee Management")
    st.subheader("Learn Pydantic + SQLAlchemy Integration")
    
    # Learning progress indicator
    st.info("📊 **INTERMEDIATE VERSION** - Focus: Database integration, model inheritance, and CRUD operations")
    
    # Sidebar navigation
    st.sidebar.title("🧭 Navigation")
    page = st.sidebar.radio(
        "Choose a section:",
        ["Dashboard", "Add Employee", "Employee List", "Database Info", "Learning Notes"],
        index=0
    )
    
    # Version navigation
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 Learning Path")
    st.sidebar.markdown("Previous: 🔰 Basic")
    st.sidebar.markdown("**Current: 📊 Intermediate** (You are here)")
    st.sidebar.markdown("Next: 🚀 Advanced")
    
    # Database connection status
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🗄️ Database Status")
    try:
        db = get_database_manager()
        if db.test_connection():
            st.sidebar.success("✅ Database Connected")
            
            # Quick stats
            with db.session_scope() as session:
                from database.models import EmployeeTable
                count = session.query(EmployeeTable).count()
                st.sidebar.metric("Total Employees", count)
        else:
            st.sidebar.error("❌ Database Error")
    except Exception as e:
        st.sidebar.error(f"❌ DB Error: {str(e)[:50]}...")
    
    # App statistics
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 App Stats")
    st.sidebar.metric("Lines of Code", "~900")
    st.sidebar.metric("Files", "5 modules")
    st.sidebar.metric("Learning Focus", "DB Integration")
    
    # Render selected page
    if page == "Dashboard":
        render_dashboard()
    elif page == "Add Employee":
        render_add_employee()
    elif page == "Employee List":
        render_employee_list()
    elif page == "Database Info":
        render_database_info()
    elif page == "Learning Notes":
        render_learning_notes()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
        <p>🐍 Pydantic v2 + SQLAlchemy</p>
        <p>🗄️ SQLite Database</p>
        <p>Built with ❤️ for Learning</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()