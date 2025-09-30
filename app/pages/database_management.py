"""
Database Management page for database operations and statistics.
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from app.services.database_service import get_database_health, get_database_url
from app.services.employee_service import EmployeeService
from src.database.sample_data import insert_sample_data, reset_with_sample_data
from src.models.employee import EmploymentStatus


def render_database_management():
    """Render the database management page."""
    st.markdown('<p class="main-header">🔧 Database Management</p>', unsafe_allow_html=True)
    
    # Database health status
    st.markdown('<p class="sub-header">🔍 Database Health</p>', unsafe_allow_html=True)
    
    health = get_database_health()
    if health["status"] == "healthy":
        st.success("🟢 Database is healthy and connected")
    else:
        st.error(f"🔴 Database error: {health.get('error', 'Unknown error')}")
    
    # Database information
    st.markdown('<p class="sub-header">📊 Database Information</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Database URL:** {get_database_url()}")
    with col2:
        st.info(f"**Status:** {health['status'].title()}")
    
    # Database operations
    st.markdown('<p class="sub-header">⚙️ Database Operations</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear All Data", type="secondary"):
            if st.session_state.get('confirm_clear_all'):
                try:
                    from app.services.database_service import get_database_manager_cached
                    db_manager = get_database_manager_cached()
                    
                    with db_manager.session_scope() as session:
                        from src.database.models import EmployeeTable
                        session.query(EmployeeTable).delete()
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
    
    # Add sample data
    st.markdown('<p class="sub-header">📈 Add Sample Data</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        employee_count = st.number_input("Number of Employees", min_value=1, max_value=100, value=10)
    
    with col2:
        user_count = st.number_input("Number of Users", min_value=1, max_value=50, value=3)
    
    if st.button("🚀 Add Sample Data", type="primary"):
        try:
            from app.services.database_service import get_database_manager_cached
            db_manager = get_database_manager_cached()
            result = insert_sample_data(db_manager, employee_count=int(employee_count), user_count=int(user_count))
            st.success(f"Added {result['employees_created']} employees and {result['users_created']} users!")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to add sample data: {str(e)}")
    
    # Database statistics
    st.markdown('<p class="sub-header">📈 Database Statistics</p>', unsafe_allow_html=True)
    
    try:
        employee_service = EmployeeService()
        metrics = employee_service.get_dashboard_metrics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Employees", metrics['total_employees'])
        
        with col2:
            st.metric("Departments", len(metrics['department_stats']))
        
        with col3:
            if metrics['salary_stats']['count'] > 0:
                st.metric("Avg Salary", f"${metrics['salary_stats']['average']:,.0f}")
            else:
                st.metric("Avg Salary", "$0")
        
        with col4:
            st.metric("Active Employees", metrics['active_employees'])
        
        # Department breakdown
        if metrics['department_stats']:
            st.markdown('<p class="sub-header">🏢 Department Breakdown</p>', unsafe_allow_html=True)
            
            dept_data = []
            for dept, count in metrics['department_stats'].items():
                dept_data.append({
                    'Department': dept,
                    'Employee Count': count
                })
            
            if dept_data:
                import pandas as pd
                df = pd.DataFrame(dept_data)
                st.dataframe(df, width='stretch', hide_index=True)
        
    except Exception as e:
        st.error(f"Statistics error: {str(e)}")
    
    # Quick actions
    st.markdown('<p class="sub-header">⚡ Quick Actions</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 View Dashboard", type="primary"):
            st.session_state.page = "📊 Dashboard"
            st.rerun()
    
    with col2:
        if st.button("📋 View Employees", type="secondary"):
            st.session_state.page = "📋 View Employees"
            st.rerun()
    
    with col3:
        if st.button("➕ Add Employee", type="secondary"):
            st.session_state.page = "➕ Add Employee"
            st.rerun()
