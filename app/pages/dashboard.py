"""
Dashboard page for employee analytics and metrics.
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from app.services.employee_service import EmployeeService
from app.components.charts import (
    render_department_pie_chart, 
    render_salary_box_chart,
    render_years_of_service_histogram,
    render_status_bar_chart
)
from app.services.database_service import get_database_health
from src.database.sample_data import insert_sample_data
from src.models.employee import EmploymentStatus


def render_dashboard():
    """Render the dashboard page."""
    st.markdown('<p class="main-header">📊 Employee Dashboard</p>', unsafe_allow_html=True)
    
    try:
        employee_service = EmployeeService()
        metrics = employee_service.get_dashboard_metrics()
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Employees", metrics['total_employees'])
        
        with col2:
            st.metric("Average Salary", f"${metrics['salary_stats']['average']:,.2f}")
        
        with col3:
            st.metric("Departments", len(metrics['department_stats']))
        
        with col4:
            st.metric("Active Employees", metrics['active_employees'])
        
        # Additional metrics
        col5, col6, col7, col8 = st.columns(4)
        with col5:
            st.metric("Min Salary", f"${metrics['salary_stats']['minimum']:,.2f}")
        with col6:
            st.metric("Max Salary", f"${metrics['salary_stats']['maximum']:,.2f}")
        with col7:
            st.metric("Avg Years of Service", f"{metrics['avg_years_of_service']:.1f}")
        with col8:
            st.metric("Employees with Managers", metrics['employees_with_managers'])
        
        # Charts
        st.markdown('<p class="sub-header">📈 Analytics</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Department distribution pie chart
            dept_data = employee_service.get_department_chart_data()
            render_department_pie_chart(dept_data)
        
        with col2:
            # Salary distribution by department
            df_salary = employee_service.get_salary_chart_data()
            render_salary_box_chart(df_salary)
        
        # Years of service histogram
        col3, col4 = st.columns(2)
        
        with col3:
            years_data = employee_service.get_years_of_service_data()
            render_years_of_service_histogram(years_data)
        
        with col4:
            # Status distribution
            status_data = employee_service.get_status_distribution_data()
            render_status_bar_chart(status_data)
        
    except Exception as e:
        st.error(f"Dashboard error: {str(e)}")
        
        # Show option to add sample data if no employees found
        if "No employees found" in str(e) or "ProgrammingError" in str(e):
            st.info("💡 No employees found. Add some employees to see analytics.")
            
            if st.button("🚀 Add Sample Data", type="primary"):
                try:
                    from app.services.database_service import get_database_manager_cached
                    db_manager = get_database_manager_cached()
                    result = insert_sample_data(db_manager, employee_count=10, user_count=0)
                    st.success(f"Added {result['employees_created']} employees!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to add sample data: {str(e)}")
