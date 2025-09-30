#!/usr/bin/env python3
"""
Streamlit Employee Management App with Database Integration

A comprehensive example demonstrating Pydantic integration with Streamlit
and SQLite database for building production-ready web applications.

Features:
- Pydantic model validation with database persistence
- Interactive data visualization with real-time updates
- Multi-page application structure with SQL backend
- Complete CRUD operations with error handling
- Database connection management and health monitoring
- Sample data generation and management tools

Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
import plotly.express as px
import plotly.graph_objects as go
from pydantic import ValidationError

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Import our modules
from src.models.employee import (
    Employee, EmployeeCreate, EmployeeUpdate, 
    Department, EmploymentStatus
)
from src.models.user import UserRole, UserStatus
from src.models.validation import ValidationResponse
from src.database.connection import (
    initialize_database, get_database_manager, 
    check_database_health, reset_database
)
from src.database.repository import EmployeeRepository, UserRepository
from src.database.sample_data import (
    insert_sample_data, create_demo_data, reset_with_sample_data
)

# Page configuration
st.set_page_config(
    page_title="Employee Management System",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1f77b4;
    margin-bottom: 1rem;
}
.sub-header {
    font-size: 1.5rem;
    font-weight: 600;
    color: #ff7f0e;
    margin-bottom: 0.5rem;
}
.success-box {
    padding: 1rem;
    border-radius: 0.5rem;
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    margin: 1rem 0;
}
.error-box {
    padding: 1rem;
    border-radius: 0.5rem;
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    margin: 1rem 0;
}
.metric-card {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 0.5rem;
    border: 1px solid #dee2e6;
    margin: 0.5rem 0;
}
.db-status-healthy {
    color: #28a745;
    font-weight: bold;
}
.db-status-error {
    color: #dc3545;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# Initialize database connection
@st.cache_resource
def init_database():
    """Initialize database and return manager."""
    try:
        db_manager = initialize_database(create_tables=True, sample_data=False)
        return db_manager, None
    except Exception as e:
        return None, str(e)

# Database helper functions
def get_employee_repository():
    """Get employee repository with database session."""
    db_manager = get_database_manager()
    session = db_manager.get_session()
    return EmployeeRepository(session), session

def close_session(session):
    """Close database session."""
    session.close()

# Initialize database
db_manager, db_error = init_database()

if db_error:
    st.error(f"Database initialization failed: {db_error}")
    st.stop()

# Sidebar navigation with database status
st.sidebar.markdown('<p class="main-header">🏢 Employee Management</p>', unsafe_allow_html=True)

# Database health check
health = check_database_health()
if health["status"] == "healthy":
    st.sidebar.markdown('<p class="db-status-healthy">🟢 Database Connected</p>', unsafe_allow_html=True)
else:
    st.sidebar.markdown('<p class="db-status-error">🔴 Database Error</p>', unsafe_allow_html=True)
    st.sidebar.error(health.get("error", "Unknown database error"))

page = st.sidebar.selectbox(
    "Navigate to:",
    ["📊 Dashboard", "➕ Add Employee", "📋 View Employees", "✏️ Edit Employee", "🔧 Database Management"]
)

# Main content based on selected page
if page == "📊 Dashboard":
    st.markdown('<p class="main-header">📊 Employee Dashboard</p>', unsafe_allow_html=True)
    
    try:
        emp_repo, session = get_employee_repository()
        
        # Get employees with pagination
        employees_result = emp_repo.list(limit=1000)  # Get all for dashboard
        employees = employees_result.items
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_employees = len(employees)
        with col1:
            st.metric("Total Employees", total_employees)
        
        if employees:
            # Get statistics from repository
            salary_stats = emp_repo.get_salary_stats()
            dept_stats = emp_repo.get_department_stats()
            
            with col2:
                st.metric("Average Salary", f"${salary_stats['average']:,.2f}")
            
            with col3:
                st.metric("Departments", len(dept_stats))
            
            active_count = sum(1 for emp in employees if emp.status == EmploymentStatus.ACTIVE)
            with col4:
                st.metric("Active Employees", active_count)
            
            # Additional metrics
            col5, col6, col7, col8 = st.columns(4)
            with col5:
                st.metric("Min Salary", f"${salary_stats['minimum']:,.2f}")
            with col6:
                st.metric("Max Salary", f"${salary_stats['maximum']:,.2f}")
            with col7:
                avg_years = sum(emp.years_of_service for emp in employees) / len(employees)
                st.metric("Avg Years of Service", f"{avg_years:.1f}")
            with col8:
                managers_count = sum(1 for emp in employees if emp.manager_id is not None)
                st.metric("Employees with Managers", managers_count)
            
            # Charts
            st.markdown('<p class="sub-header">📈 Analytics</p>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Department distribution pie chart
                fig_pie = px.pie(
                    values=list(dept_stats.values()),
                    names=list(dept_stats.keys()),
                    title="Employee Distribution by Department",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Salary distribution by department
                dept_salary_data = []
                for emp in employees:
                    dept_salary_data.append({
                        'Department': emp.department.value if hasattr(emp.department, 'value') else str(emp.department),
                        'Salary': float(emp.salary)
                    })
                
                if dept_salary_data:
                    df_salary = pd.DataFrame(dept_salary_data)
                    fig_box = px.box(
                        df_salary, 
                        x='Department', 
                        y='Salary',
                        title="Salary Distribution by Department",
                        color='Department'
                    )
                    fig_box.update_layout(showlegend=False)
                    st.plotly_chart(fig_box, use_container_width=True)
            
            # Years of service histogram
            col3, col4 = st.columns(2)
            
            with col3:
                years_data = [emp.years_of_service for emp in employees]
                fig_hist = px.histogram(
                    x=years_data,
                    title="Years of Service Distribution",
                    labels={'x': 'Years of Service', 'y': 'Number of Employees'},
                    nbins=20
                )
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col4:
                # Status distribution
                status_data = {}
                for emp in employees:
                    status = emp.status.value if hasattr(emp.status, 'value') else str(emp.status)
                    status_data[status] = status_data.get(status, 0) + 1
                
                fig_status = px.bar(
                    x=list(status_data.keys()),
                    y=list(status_data.values()),
                    title="Employee Status Distribution",
                    labels={'x': 'Status', 'y': 'Count'},
                    color=list(status_data.keys())
                )
                st.plotly_chart(fig_status, use_container_width=True)
            
        else:
            st.info("💡 No employees found. Add some employees to see analytics.")
            
            if st.button("🚀 Add Sample Data", type="primary"):
                try:
                    result = insert_sample_data(db_manager, employee_count=10, user_count=3)
                    st.success(f"Added {result['employees_created']} employees and {result['users_created']} users!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to add sample data: {str(e)}")
        
        close_session(session)
        
    except Exception as e:
        st.error(f"Dashboard error: {str(e)}")

elif page == "➕ Add Employee":
    st.markdown('<p class="main-header">➕ Add New Employee</p>', unsafe_allow_html=True)
    
    with st.form("add_employee_form", clear_on_submit=True):
        st.markdown('<p class="sub-header">Personal Information</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name*", max_chars=50)
            email = st.text_input("Email*")
            birth_date = st.date_input("Birth Date", value=None, max_value=date.today())
        
        with col2:
            last_name = st.text_input("Last Name*", max_chars=50)
            phone = st.text_input("Phone")
        
        st.markdown('<p class="sub-header">Employment Information</p>', unsafe_allow_html=True)
        
        col3, col4 = st.columns(2)
        with col3:
            employee_id = st.text_input("Employee ID*", max_chars=10, help="e.g., EMP001")
            department = st.selectbox("Department*", options=list(Department), format_func=lambda x: x.value)
            hire_date = st.date_input("Hire Date*", value=date.today(), max_value=date.today())
        
        with col4:
            position = st.text_input("Position*", max_chars=100)
            salary = st.number_input("Annual Salary*", min_value=0.0, step=1000.0, format="%.2f")
            status = st.selectbox("Status", options=list(EmploymentStatus), index=0, format_func=lambda x: x.value)
        
        # Manager selection
        try:
            emp_repo, session = get_employee_repository()
            potential_managers = emp_repo.list(limit=100).items
            manager_options = {"None": None}
            for emp in potential_managers:
                manager_options[f"{emp.full_name} ({emp.employee_id})"] = emp.id
            
            manager_choice = st.selectbox("Manager (optional)", options=list(manager_options.keys()))
            manager_id = manager_options[manager_choice]
            close_session(session)
        except Exception:
            manager_id = None
        
        st.markdown('<p class="sub-header">Additional Information</p>', unsafe_allow_html=True)
        
        skills_input = st.text_area("Skills (one per line)", help="Enter each skill on a new line")
        skills = [skill.strip() for skill in skills_input.split('\n') if skill.strip()] if skills_input else []
        
        submitted = st.form_submit_button("Add Employee", type="primary")
        
        if submitted:
            # Validate required fields
            if not all([first_name, last_name, email, employee_id, position, salary]):
                st.error("Please fill in all required fields (marked with *)")
            else:
                try:
                    employee_data = EmployeeCreate(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        phone=phone if phone else None,
                        birth_date=birth_date,
                        employee_id=employee_id.upper(),
                        department=department,
                        position=position,
                        hire_date=hire_date,
                        salary=Decimal(str(salary)),
                        status=status,
                        manager_id=manager_id,
                        skills=skills
                    )
                    
                    # Save to database
                    emp_repo, session = get_employee_repository()
                    
                    try:
                        new_employee = emp_repo.create(employee_data)
                        st.success(f"Employee {new_employee.full_name} added successfully!")
                        st.balloons()
                        
                        # Show created employee details
                        with st.expander("👤 Employee Details", expanded=True):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**ID:** {new_employee.id}")
                                st.write(f"**Name:** {new_employee.full_name}")
                                st.write(f"**Email:** {new_employee.email}")
                                st.write(f"**Department:** {new_employee.department.value if hasattr(new_employee.department, 'value') else str(new_employee.department)}")
                            with col2:
                                st.write(f"**Employee ID:** {new_employee.employee_id}")
                                st.write(f"**Position:** {new_employee.position}")
                                st.write(f"**Salary:** ${new_employee.salary:,.2f}")
                                st.write(f"**Status:** {new_employee.status.value if hasattr(new_employee.status, 'value') else str(new_employee.status)}")
                    
                    except ValueError as e:
                        st.error(f"Database error: {str(e)}")
                    finally:
                        close_session(session)
                        
                except ValidationError as e:
                    st.error("Validation failed:")
                    for error in e.errors():
                        field = '.'.join(str(loc) for loc in error['loc'])
                        st.error(f"• {field}: {error['msg']}")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}")

elif page == "📋 View Employees":
    st.markdown('<p class="main-header">📋 Employee Directory</p>', unsafe_allow_html=True)
    
    try:
        emp_repo, session = get_employee_repository()
        
        # Filter options
        st.markdown('<p class="sub-header">🔍 Filter Options</p>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            filter_dept = st.selectbox(
                "Department", 
                options=[None] + list(Department),
                format_func=lambda x: "All Departments" if x is None else x.value
            )
        
        with col2:
            filter_status = st.selectbox(
                "Status",
                options=[None] + list(EmploymentStatus),
                format_func=lambda x: "All Statuses" if x is None else x.value
            )
        
        with col3:
            search_term = st.text_input("Search", placeholder="Name, email, or ID")
        
        with col4:
            page_size = st.selectbox("Items per page", options=[10, 25, 50, 100], index=1)
        
        # Pagination
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 1
        
        # Get filtered employees
        skip = (st.session_state.current_page - 1) * page_size
        employees_result = emp_repo.list(
            skip=skip,
            limit=page_size,
            department=filter_dept,
            status=filter_status,
            search=search_term
        )
        
        employees = employees_result.items
        total_count = employees_result.total_count
        
        st.markdown(f'<p class="sub-header">👥 Employees ({total_count} total)</p>', unsafe_allow_html=True)
        
        if employees:
            # Create DataFrame for display
            data = []
            for emp in employees:
                data.append({
                    'ID': emp.id,
                    'Employee ID': emp.employee_id,
                    'Name': emp.full_name,
                    'Email': emp.email,
                    'Department': emp.department.value if hasattr(emp.department, 'value') else str(emp.department),
                    'Position': emp.position,
                    'Salary': f"${emp.salary:,.2f}",
                    'Hire Date': emp.hire_date.strftime('%Y-%m-%d'),
                    'Status': emp.status.value if hasattr(emp.status, 'value') else str(emp.status),
                    'Years of Service': emp.years_of_service
                })
            
            df = pd.DataFrame(data)
            
            # Display table
            st.dataframe(
                df, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "ID": st.column_config.NumberColumn("ID", width="small"),
                    "Employee ID": st.column_config.TextColumn("Emp ID", width="small"),
                    "Name": st.column_config.TextColumn("Name", width="medium"),
                    "Email": st.column_config.TextColumn("Email", width="medium"),
                    "Salary": st.column_config.TextColumn("Salary", width="small"),
                    "Years of Service": st.column_config.NumberColumn("Years", width="small")
                }
            )
            
            # Pagination controls
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                if st.button("← Previous", disabled=not employees_result.has_previous):
                    st.session_state.current_page -= 1
                    st.rerun()
            
            with col2:
                st.write(f"Page {employees_result.page} of {employees_result.total_pages}")
            
            with col3:
                if st.button("Next →", disabled=not employees_result.has_next):
                    st.session_state.current_page += 1
                    st.rerun()
            
            # Employee details
            st.markdown('<p class="sub-header">📄 Employee Details</p>', unsafe_allow_html=True)
            
            if employees:
                selected_emp_id = st.selectbox(
                    "Select employee for details:",
                    options=[emp.employee_id for emp in employees],
                    format_func=lambda x: f"{x} - {next(emp.full_name for emp in employees if emp.employee_id == x)}"
                )
                
                if selected_emp_id:
                    selected_emp = next(emp for emp in employees if emp.employee_id == selected_emp_id)
                    
                    with st.container():
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown("**Personal Information**")
                            st.write(f"**Name:** {selected_emp.full_name}")
                            st.write(f"**Email:** {selected_emp.email}")
                            st.write(f"**Phone:** {selected_emp.phone or 'N/A'}")
                            if selected_emp.age:
                                st.write(f"**Age:** {selected_emp.age}")
                        
                        with col2:
                            st.markdown("**Employment Information**")
                            st.write(f"**Employee ID:** {selected_emp.employee_id}")
                            st.write(f"**Department:** {selected_emp.department.value if hasattr(selected_emp.department, 'value') else str(selected_emp.department)}")
                            st.write(f"**Position:** {selected_emp.position}")
                            st.write(f"**Status:** {selected_emp.status.value if hasattr(selected_emp.status, 'value') else str(selected_emp.status)}")
                        
                        with col3:
                            st.markdown("**Work Details**")
                            st.write(f"**Hire Date:** {selected_emp.hire_date}")
                            st.write(f"**Years of Service:** {selected_emp.years_of_service}")
                            st.write(f"**Salary:** ${selected_emp.salary:,.2f}")
                            if selected_emp.manager_id:
                                # Get manager info
                                manager = emp_repo.get(selected_emp.manager_id)
                                if manager:
                                    st.write(f"**Manager:** {manager.full_name}")
                        
                        if selected_emp.skills:
                            st.markdown("**Skills:**")
                            skills_text = " • ".join(selected_emp.skills)
                            st.write(skills_text)
                        else:
                            st.write("**Skills:** None listed")
        else:
            st.info("No employees match the current filters.")
        
        close_session(session)
        
    except Exception as e:
        st.error(f"Error loading employees: {str(e)}")

elif page == "✏️ Edit Employee":
    st.markdown('<p class="main-header">✏️ Edit Employee</p>', unsafe_allow_html=True)
    
    try:
        emp_repo, session = get_employee_repository()
        
        # Get all employees for selection
        employees_result = emp_repo.list(limit=1000)
        employees = employees_result.items
        
        if not employees:
            st.info("No employees found. Add some employees first.")
        else:
            # Select employee to edit
            selected_emp_id = st.selectbox(
                "Select employee to edit:",
                options=[emp.employee_id for emp in employees],
                format_func=lambda x: f"{x} - {next(emp.full_name for emp in employees if emp.employee_id == x)}"
            )
            
            if selected_emp_id:
                selected_emp = next(emp for emp in employees if emp.employee_id == selected_emp_id)
                
                with st.form("edit_employee_form"):
                    st.markdown('<p class="sub-header">Personal Information</p>', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        first_name = st.text_input("First Name", value=selected_emp.first_name, max_chars=50)
                        email = st.text_input("Email", value=selected_emp.email)
                        birth_date = st.date_input("Birth Date", value=selected_emp.birth_date, max_value=date.today())
                    
                    with col2:
                        last_name = st.text_input("Last Name", value=selected_emp.last_name, max_chars=50)
                        phone = st.text_input("Phone", value=selected_emp.phone or "")
                    
                    st.markdown('<p class="sub-header">Employment Information</p>', unsafe_allow_html=True)
                    
                    col3, col4 = st.columns(2)
                    with col3:
                        department = st.selectbox(
                            "Department", 
                            options=list(Department), 
                            index=list(Department).index(selected_emp.department),
                            format_func=lambda x: x.value
                        )
                        salary = st.number_input(
                            "Annual Salary", 
                            value=float(selected_emp.salary), 
                            min_value=0.0, 
                            step=1000.0, 
                            format="%.2f"
                        )
                    
                    with col4:
                        position = st.text_input("Position", value=selected_emp.position, max_chars=100)
                        status = st.selectbox(
                            "Status", 
                            options=list(EmploymentStatus), 
                            index=list(EmploymentStatus).index(selected_emp.status),
                            format_func=lambda x: x.value
                        )
                    
                    # Manager selection
                    potential_managers = [emp for emp in employees if emp.id != selected_emp.id]
                    manager_options = {"None": None}
                    for emp in potential_managers:
                        manager_options[f"{emp.full_name} ({emp.employee_id})"] = emp.id
                    
                    current_manager_key = "None"
                    if selected_emp.manager_id:
                        for key, value in manager_options.items():
                            if value == selected_emp.manager_id:
                                current_manager_key = key
                                break
                    
                    manager_choice = st.selectbox(
                        "Manager", 
                        options=list(manager_options.keys()),
                        index=list(manager_options.keys()).index(current_manager_key)
                    )
                    manager_id = manager_options[manager_choice]
                    
                    st.markdown('<p class="sub-header">Additional Information</p>', unsafe_allow_html=True)
                    
                    skills_text = '\n'.join(selected_emp.skills)
                    skills_input = st.text_area("Skills (one per line)", value=skills_text)
                    skills = [skill.strip() for skill in skills_input.split('\n') if skill.strip()] if skills_input else []
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        submitted = st.form_submit_button("Update Employee", type="primary")
                    with col2:
                        delete_clicked = st.form_submit_button("🗑️ Delete", type="secondary")
                    
                    if submitted:
                        try:
                            # Only include changed fields
                            update_data = EmployeeUpdate(
                                first_name=first_name if first_name != selected_emp.first_name else None,
                                last_name=last_name if last_name != selected_emp.last_name else None,
                                email=email if email != selected_emp.email else None,
                                phone=phone if phone != (selected_emp.phone or "") else None,
                                birth_date=birth_date if birth_date != selected_emp.birth_date else None,
                                department=department if department != selected_emp.department else None,
                                position=position if position != selected_emp.position else None,
                                salary=Decimal(str(salary)) if Decimal(str(salary)) != selected_emp.salary else None,
                                status=status if status != selected_emp.status else None,
                                manager_id=manager_id if manager_id != selected_emp.manager_id else None,
                                skills=skills if skills != selected_emp.skills else None
                            )
                            
                            updated_employee = emp_repo.update(selected_emp.id, update_data)
                            
                            if updated_employee:
                                st.success(f"Employee {updated_employee.full_name} updated successfully!")
                                st.rerun()
                            else:
                                st.error("Employee not found")
                                
                        except ValueError as e:
                            st.error(f"Database error: {str(e)}")
                        except ValidationError as e:
                            st.error("Validation failed:")
                            for error in e.errors():
                                field = '.'.join(str(loc) for loc in error['loc'])
                                st.error(f"• {field}: {error['msg']}")
                        except Exception as e:
                            st.error(f"An unexpected error occurred: {str(e)}")
                    
                    if delete_clicked:
                        if st.session_state.get('confirm_delete') == selected_emp.id:
                            if emp_repo.delete(selected_emp.id):
                                st.success(f"Employee {selected_emp.full_name} deleted successfully")
                                st.session_state.confirm_delete = None
                                st.rerun()
                            else:
                                st.error("Failed to delete employee")
                        else:
                            st.session_state.confirm_delete = selected_emp.id
                            st.warning(f"Click delete again to confirm deletion of {selected_emp.full_name}")
        
        close_session(session)
        
    except Exception as e:
        st.error(f"Error in edit page: {str(e)}")

elif page == "🔧 Database Management":
    st.markdown('<p class="main-header">🔧 Database Management</p>', unsafe_allow_html=True)
    
    # Database status and info
    st.markdown('<p class="sub-header">📊 Database Status</p>', unsafe_allow_html=True)
    
    health = check_database_health()
    
    col1, col2 = st.columns(2)
    with col1:
        if health["status"] == "healthy":
            st.success("✅ Database is healthy")
        else:
            st.error(f"❌ Database error: {health.get('error', 'Unknown error')}")
    
    with col2:
        if st.button("🔄 Refresh Status"):
            st.rerun()
    
    # Database information
    if health["status"] == "healthy":
        db_info = health["details"]
        
        with st.expander("🔍 Database Details", expanded=False):
            st.json(db_info)
    
    # Sample data management
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<p class="sub-header">📥 Sample Data</p>', unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            demo_count = st.number_input("Demo employees", min_value=1, max_value=5, value=3)
            if st.button("Add Demo Data", type="secondary"):
                try:
                    result = create_demo_data()
                    st.success(f"Added {result['demo_employees_created']} demo employees and {result['demo_users_created']} users!")
                    st.info(result['note'])
                except Exception as e:
                    st.error(f"Failed to add demo data: {str(e)}")
        
        with col_b:
            sample_count = st.number_input("Sample employees", min_value=5, max_value=100, value=20)
            if st.button("Add Sample Data", type="secondary"):
                try:
                    result = insert_sample_data(db_manager, employee_count=sample_count, user_count=max(3, sample_count//10))
                    st.success(f"Added {result['employees_created']} employees and {result['users_created']} users!")
                    st.info(f"Departments: {result['departments_represented']}, Employees with managers: {result['employees_with_managers']}")
                except Exception as e:
                    st.error(f"Failed to add sample data: {str(e)}")
    
    with col2:
        st.markdown('<p class="sub-header">📊 Export & Backup</p>', unsafe_allow_html=True)
        
        try:
            emp_repo, session = get_employee_repository()
            employees_result = emp_repo.list(limit=10000)  # Get all employees
            employees = employees_result.items
            
            if employees:
                # Prepare export data
                export_data = []
                for emp in employees:
                    export_data.append({
                        'ID': emp.id,
                        'Employee_ID': emp.employee_id,
                        'First_Name': emp.first_name,
                        'Last_Name': emp.last_name,
                        'Email': emp.email,
                        'Phone': emp.phone,
                        'Birth_Date': emp.birth_date.isoformat() if emp.birth_date else None,
                        'Department': emp.department.value if hasattr(emp.department, 'value') else str(emp.department),
                        'Position': emp.position,
                        'Hire_Date': emp.hire_date.isoformat(),
                        'Salary': float(emp.salary),
                        'Status': emp.status.value if hasattr(emp.status, 'value') else str(emp.status),
                        'Manager_ID': emp.manager_id,
                        'Skills': ', '.join(emp.skills),
                        'Created_At': emp.created_at.isoformat() if emp.created_at else None,
                        'Updated_At': emp.updated_at.isoformat() if emp.updated_at else None
                    })
                
                df = pd.DataFrame(export_data)
                csv = df.to_csv(index=False)
                
                st.download_button(
                    label=f"📄 Export {len(employees)} Employees (CSV)",
                    data=csv,
                    file_name=f"employees_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                # JSON export
                import json
                json_data = json.dumps(export_data, indent=2, default=str)
                st.download_button(
                    label=f"📋 Export {len(employees)} Employees (JSON)",
                    data=json_data,
                    file_name=f"employees_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            else:
                st.info("No employees to export")
            
            close_session(session)
            
        except Exception as e:
            st.error(f"Export error: {str(e)}")
    
    # Danger zone
    st.markdown('<p class="sub-header">⚠️ Danger Zone</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear All Data", type="secondary"):
            if st.session_state.get('confirm_clear_all'):
                try:
                    db_manager = get_database_manager()
                    with db_manager.session_scope() as session:
                        from src.database.models import EmployeeTable, UserTable
                        session.query(EmployeeTable).delete()
                        session.query(UserTable).delete()
                        session.commit()
                    
                    st.session_state.confirm_clear_all = False
                    st.success("All data cleared successfully")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to clear data: {str(e)}")
            else:
                st.session_state.confirm_clear_all = True
                st.warning("Click again to confirm clearing all data")
    
    with col2:
        if st.button("🔄 Reset Database", type="secondary"):
            if st.session_state.get('confirm_reset_db'):
                try:
                    result = reset_with_sample_data(employee_count=5, user_count=2)
                    st.session_state.confirm_reset_db = False
                    st.success(f"Database reset with {result['employees_created']} employees and {result['users_created']} users")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to reset database: {str(e)}")
            else:
                st.session_state.confirm_reset_db = True
                st.warning("Click again to confirm database reset with sample data")
    
    # Database statistics
    st.markdown('<p class="sub-header">📈 Database Statistics</p>', unsafe_allow_html=True)
    
    try:
        emp_repo, session = get_employee_repository()
        
        # Get counts
        total_employees = emp_repo.list(limit=1).total_count
        dept_stats = emp_repo.get_department_stats()
        salary_stats = emp_repo.get_salary_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Employees", total_employees)
        
        with col2:
            st.metric("Departments", len(dept_stats))
        
        with col3:
            if salary_stats['count'] > 0:
                st.metric("Avg Salary", f"${salary_stats['average']:,.0f}")
            else:
                st.metric("Avg Salary", "$0")
        
        with col4:
            active_result = emp_repo.list(status=EmploymentStatus.ACTIVE, limit=1)
            st.metric("Active Employees", active_result.total_count)
        
        close_session(session)
        
    except Exception as e:
        st.error(f"Statistics error: {str(e)}")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown(
    f"""
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
        <p>🐍 Powered by Pydantic v2</p>
        <p>🗄️ SQLite Database</p>
        <p>Built with ❤️ using Streamlit</p>
        <p>Database: {db_manager.database_url if db_manager else 'Not connected'}</p>
    </div>
    """, 
    unsafe_allow_html=True
)