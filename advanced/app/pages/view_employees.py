"""
View Employees page for displaying and managing employee list.
"""

import streamlit as st
import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from app.services.employee_service import EmployeeService
from src.models.employee import EmploymentStatus


def render_view_employees():
    """Render the view employees page."""
    st.markdown('<p class="main-header">📋 View Employees</p>', unsafe_allow_html=True)
    
    try:
        employee_service = EmployeeService()
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.selectbox(
                "Filter by Status",
                options=["All"] + [status.value for status in EmploymentStatus],
                index=0
            )
        
        with col2:
            search_term = st.text_input("Search by Name or Employee ID", placeholder="Enter name or ID...")
        
        with col3:
            page_size = st.selectbox("Employees per page", options=[10, 25, 50, 100], index=1)
        
        # Convert status filter
        status = None
        if status_filter != "All":
            status = EmploymentStatus(status_filter)
        
        # Get employees with pagination
        page = st.session_state.get('employee_page', 0)
        offset = page * page_size
        
        result = employee_service.get_employees_list(
            limit=page_size, 
            offset=offset, 
            status=status
        )
        
        employees = result['items']
        total_count = result['total_count']
        
        # Apply search filter if provided
        if search_term:
            search_lower = search_term.lower()
            employees = [
                emp for emp in employees 
                if (search_lower in emp.first_name.lower() or 
                    search_lower in emp.last_name.lower() or 
                    search_lower in emp.employee_id.lower())
            ]
        
        # Display results
        if employees:
            st.markdown(f"**Showing {len(employees)} of {total_count} employees**")
            
            # Create DataFrame for display
            df_data = []
            for emp in employees:
                df_data.append({
                    'ID': emp.id,
                    'Employee ID': emp.employee_id,
                    'Name': f"{emp.first_name} {emp.last_name}",
                    'Email': emp.email,
                    'Department': emp.department.value if hasattr(emp.department, 'value') else str(emp.department),
                    'Position': emp.position,
                    'Status': emp.status.value if hasattr(emp.status, 'value') else str(emp.status),
                    'Salary': f"${emp.salary:,.2f}",
                    'Years of Service': emp.years_of_service,
                    'Manager ID': str(emp.manager_id) if emp.manager_id else "N/A"
                })
            
            df = pd.DataFrame(df_data)
            
            # Display the table
            st.dataframe(
                df,
                width='stretch',
                hide_index=True,
                column_config={
                    "ID": st.column_config.NumberColumn("ID", width="small"),
                    "Employee ID": st.column_config.TextColumn("Employee ID", width="medium"),
                    "Name": st.column_config.TextColumn("Name", width="large"),
                    "Email": st.column_config.TextColumn("Email", width="large"),
                    "Department": st.column_config.TextColumn("Department", width="medium"),
                    "Position": st.column_config.TextColumn("Position", width="medium"),
                    "Status": st.column_config.TextColumn("Status", width="small"),
                    "Salary": st.column_config.TextColumn("Salary", width="medium"),
                    "Years of Service": st.column_config.NumberColumn("Years", width="small"),
                    "Manager ID": st.column_config.TextColumn("Manager", width="small")
                }
            )
            
            # Pagination controls
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                if page > 0:
                    if st.button("⬅️ Previous"):
                        st.session_state.employee_page = page - 1
                        st.rerun()
            
            with col2:
                st.write(f"Page {page + 1}")
            
            with col3:
                if (page + 1) * page_size < total_count:
                    if st.button("Next ➡️"):
                        st.session_state.employee_page = page + 1
                        st.rerun()
            
            with col4:
                if st.button("🔄 Refresh"):
                    st.rerun()
            
            with col5:
                if st.button("✏️ Edit Selected"):
                    st.session_state.page = "✏️ Edit Employee"
                    st.rerun()
            
            # Quick actions
            st.markdown('<p class="sub-header">⚡ Quick Actions</p>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("➕ Add New Employee", type="primary"):
                    st.session_state.page = "➕ Add Employee"
                    st.rerun()
            
            with col2:
                if st.button("📊 View Dashboard", type="secondary"):
                    st.session_state.page = "📊 Dashboard"
                    st.rerun()
            
            with col3:
                if st.button("🔧 Database Management", type="secondary"):
                    st.session_state.page = "🔧 Database Management"
                    st.rerun()
        
        else:
            st.info("💡 No employees found matching your criteria.")
            
            if search_term:
                st.write(f"No employees found matching '{search_term}'")
                if st.button("🔍 Clear Search"):
                    st.session_state.employee_page = 0
                    st.rerun()
            else:
                st.write("Add some employees to get started!")
                if st.button("➕ Add First Employee", type="primary"):
                    st.session_state.page = "➕ Add Employee"
                    st.rerun()
        
    except Exception as e:
        st.error(f"Error loading employees: {str(e)}")
        st.markdown(f"""
        <div class="error-box">
            <strong>Error Details:</strong><br>
            {str(e)}
        </div>
        """, unsafe_allow_html=True)
