"""
Edit Employee page for updating existing employees.
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from app.services.employee_service import EmployeeService
from app.components.forms import render_employee_form, validate_employee_data
from src.models.employee import EmploymentStatus


def render_edit_employee():
    """Render the edit employee page."""
    st.markdown('<p class="main-header">✏️ Edit Employee</p>', unsafe_allow_html=True)
    
    try:
        employee_service = EmployeeService()
        
        # Employee selection
        st.markdown('<p class="sub-header">Select Employee to Edit</p>', unsafe_allow_html=True)
        
        # Get all employees for selection
        result = employee_service.get_employees_list(limit=1000)  # Get all for selection
        employees = result['items']
        
        if not employees:
            st.info("💡 No employees found. Add some employees first.")
            if st.button("➕ Add Employee", type="primary", key="add_employee_no_employees"):
                st.session_state.page = "➕ Add Employee"
                st.rerun()
            return
        
        # Create selection options
        employee_options = {
            f"{emp.employee_id} - {emp.first_name} {emp.last_name} ({emp.department.value if hasattr(emp.department, 'value') else str(emp.department)})": emp.id 
            for emp in employees
        }
        
        selected_employee_name = st.selectbox(
            "Choose Employee:",
            options=list(employee_options.keys()),
            index=0
        )
        
        if selected_employee_name:
            employee_id = employee_options[selected_employee_name]
            
            # Get the selected employee
            employee = employee_service.get_employee_by_id(employee_id)
            
            if employee:
                st.markdown('<p class="sub-header">Edit Employee Information</p>', unsafe_allow_html=True)
                
                # Show current employee info
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**Current Status:** {employee.status.value if hasattr(employee.status, 'value') else str(employee.status)}")
                with col2:
                    st.info(f"**Current Department:** {employee.department.value if hasattr(employee.department, 'value') else str(employee.department)}")
                
                # Render the form with current data
                form_data = render_employee_form(employee)
                
                if form_data:
                    try:
                        # Validate the form data
                        employee_data = validate_employee_data(form_data, is_edit=True)
                        
                        if employee_data:
                            # Update the employee
                            updated_employee = employee_service.update_employee(employee_id, employee_data)
                            
                            if updated_employee:
                                st.success(f"✅ Employee {updated_employee.first_name} {updated_employee.last_name} updated successfully!")
                                st.markdown(f"""
                                <div class="success-box">
                                    <strong>Updated Employee Details:</strong><br>
                                    <strong>Name:</strong> {updated_employee.first_name} {updated_employee.last_name}<br>
                                    <strong>Employee ID:</strong> {updated_employee.employee_id}<br>
                                    <strong>Department:</strong> {updated_employee.department.value if hasattr(updated_employee.department, 'value') else str(updated_employee.department)}<br>
                                    <strong>Position:</strong> {updated_employee.position}<br>
                                    <strong>Status:</strong> {updated_employee.status.value if hasattr(updated_employee.status, 'value') else str(updated_employee.status)}<br>
                                    <strong>Salary:</strong> ${updated_employee.salary:,.2f}
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Option to edit another employee
                                if st.button("✏️ Edit Another Employee", type="secondary", key="edit_another_employee"):
                                    st.rerun()
                                
                                # Option to view all employees
                                if st.button("📋 View All Employees", type="secondary", key="view_all_employees_success"):
                                    st.session_state.page = "📋 View Employees"
                                    st.rerun()
                            else:
                                st.error("Failed to update employee. Please check the data and try again.")
                                
                    except Exception as e:
                        error_msg = str(e)
                        
                        # Handle specific error types with user-friendly messages
                        if "FOREIGN KEY constraint failed" in error_msg:
                            st.error("❌ **Manager not found!** The selected manager ID doesn't exist. Please choose a valid manager or leave the field empty.")
                        elif "UNIQUE constraint failed" in error_msg:
                            st.error("❌ **Duplicate data!** An employee with this email or employee ID already exists.")
                        elif "NOT NULL constraint failed" in error_msg:
                            st.error("❌ **Missing required data!** Please fill in all required fields.")
                        else:
                            st.error(f"❌ **Update failed:** {error_msg}")
                        
                        st.markdown(f"""
                        <div class="error-box">
                            <strong>Error Details:</strong><br>
                            {error_msg}
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.error("Employee not found. Please select a different employee.")
        
        # Quick actions
        st.markdown('<p class="sub-header">⚡ Quick Actions</p>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("➕ Add New Employee", type="primary", key="add_new_employee_error"):
                st.session_state.page = "➕ Add Employee"
                st.rerun()
        
        with col2:
            if st.button("📋 View All Employees", type="secondary", key="view_all_employees_error"):
                st.session_state.page = "📋 View Employees"
                st.rerun()
        
        with col3:
            if st.button("📊 Dashboard", type="secondary", key="dashboard_error"):
                st.session_state.page = "📊 Dashboard"
                st.rerun()
        
    except Exception as e:
        st.error(f"Error in edit employee: {str(e)}")
        st.markdown(f"""
        <div class="error-box">
            <strong>Error Details:</strong><br>
            {str(e)}
        </div>
        """, unsafe_allow_html=True)
