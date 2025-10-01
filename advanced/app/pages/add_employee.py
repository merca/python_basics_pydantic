"""
Add Employee page for creating new employees.
"""

import streamlit as st
from app.services.employee_service import EmployeeService
from app.components.forms import render_employee_form, validate_employee_data


def render_add_employee():
    """Render the add employee page."""
    st.markdown('<p class="main-header">➕ Add New Employee</p>', unsafe_allow_html=True)
    
    # Render the form
    form_data = render_employee_form()
    
    if form_data:
        try:
            # Validate the form data
            employee_data = validate_employee_data(form_data, is_edit=False)
            
            if employee_data:
                # Create the employee
                employee_service = EmployeeService()
                new_employee = employee_service.create_employee(employee_data)
                
                # Clear form data from session state on successful submission
                if 'add_employee_form_data' in st.session_state:
                    del st.session_state['add_employee_form_data']
                
                st.success(f"✅ Employee {new_employee.first_name} {new_employee.last_name} added successfully!")
                st.markdown(f"""
                <div class="success-box">
                    <strong>Employee Details:</strong><br>
                    <strong>Name:</strong> {new_employee.first_name} {new_employee.last_name}<br>
                    <strong>Employee ID:</strong> {new_employee.employee_id}<br>
                                    <strong>Department:</strong> {new_employee.department.value if hasattr(new_employee.department, 'value') else str(new_employee.department)}<br>
                    <strong>Position:</strong> {new_employee.position}<br>
                    <strong>Salary:</strong> ${new_employee.salary:,.2f}
                </div>
                """, unsafe_allow_html=True)
                
                # Option to add another employee
                if st.button("➕ Add Another Employee", type="secondary"):
                    st.rerun()
                
                # Option to view employees
                if st.button("📋 View All Employees", type="secondary"):
                    st.session_state.page = "📋 View Employees"
                    st.rerun()
                    
        except Exception as e:
            st.error(f"Failed to add employee: {str(e)}")
            st.markdown(f"""
            <div class="error-box">
                <strong>Error Details:</strong><br>
                {str(e)}
            </div>
            """, unsafe_allow_html=True)
