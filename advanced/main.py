"""
Main Streamlit application for Employee Management System.

This is the refactored version of the original app.py, broken down into modular components.
"""

import streamlit as st
import sys
import os

# Add current directory and src directory to path
current_dir = os.path.dirname(__file__)
sys.path.insert(0, current_dir)
sys.path.append(os.path.join(current_dir, "src"))

# Import components
from app.components.styling import apply_custom_css
from app.services.database_service import get_database_health, get_database_url
from app.pages.dashboard import render_dashboard
from app.pages.add_employee import render_add_employee
from app.pages.view_employees import render_view_employees
from app.pages.edit_employee import render_edit_employee
from app.pages.database_management import render_database_management


def main():
    """Main application function."""
    # Page configuration
    st.set_page_config(
        page_title="Employee Management System",
        page_icon="👥",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': None
        }
    )
    
    # Apply custom CSS
    apply_custom_css()
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = "📊 Dashboard"
    if 'employee_page' not in st.session_state:
        st.session_state.employee_page = 0
    
    # Check if database has data, if not show a message
    try:
        from app.services.employee_service import EmployeeService
        employee_service = EmployeeService()
        metrics = employee_service.get_dashboard_metrics()
        
        if metrics['total_employees'] == 0:
            st.info("💡 No employees found in the database. Use the Database Management page to add sample data.")
            
            # Quick add sample data button
            if st.button("🚀 Add Sample Data Now", type="primary"):
                try:
                    from app.services.database_service import get_database_manager_cached
                    from src.database.sample_data import insert_sample_data
                    db_manager = get_database_manager_cached()
                    result = insert_sample_data(db_manager, employee_count=10, user_count=0)
                    st.success(f"Added {result['employees_created']} employees!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to add sample data: {str(e)}")
    except Exception as e:
        st.warning(f"Database connection issue: {str(e)}")
    
    # Sidebar navigation with database status
    st.sidebar.markdown('<p class="main-header">🏢 Employee Management</p>', unsafe_allow_html=True)
    
    # Database health check
    health = get_database_health()
    if health["status"] == "healthy":
        st.sidebar.markdown('<p class="db-status-healthy">🟢 Database Connected</p>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('<p class="db-status-error">🔴 Database Error</p>', unsafe_allow_html=True)
        st.sidebar.error(health.get("error", "Unknown database error"))
    
    # Navigation
    st.sidebar.markdown("### Navigation")
    page = st.sidebar.selectbox(
        "Select Page:",
        ["📊 Dashboard", "➕ Add Employee", "📋 View Employees", "✏️ Edit Employee", "🔧 Database Management"],
        index=["📊 Dashboard", "➕ Add Employee", "📋 View Employees", "✏️ Edit Employee", "🔧 Database Management"].index(st.session_state.page)
    )
    
    # Update session state if page changed
    if page != st.session_state.page:
        st.session_state.page = page
        st.rerun()
    
    # Main content based on selected page
    if page == "📊 Dashboard":
        render_dashboard()
    elif page == "➕ Add Employee":
        render_add_employee()
    elif page == "📋 View Employees":
        render_view_employees()
    elif page == "✏️ Edit Employee":
        render_edit_employee()
    elif page == "🔧 Database Management":
        render_database_management()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"""
        <div style='text-align: center; color: #666; font-size: 0.8em;'>
            <p>🐍 Powered by Pydantic v2</p>
            <p>🗄️ SQLite Database</p>
            <p>Built with ❤️ using Streamlit</p>
            <p>Database: {get_database_url()}</p>
        </div>
        """, 
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
