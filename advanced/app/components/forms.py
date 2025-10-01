"""
Form components for employee management.
"""

import streamlit as st
from datetime import date
from typing import Dict, Any, Optional
from pydantic import ValidationError
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from src.models.employee import Employee, EmployeeCreate, EmployeeUpdate, Department, EmploymentStatus

def validate_email_realtime(email: str) -> bool:
    """Validate email format in real-time."""
    return '@' in email and '.' in email.split('@')[-1] if email else True

def validate_age_realtime(birth_date) -> tuple[bool, str]:
    """Validate age in real-time."""
    if not birth_date:
        return True, ""
    
    from datetime import date
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    
    if age < 16:
        return False, f"❌ Must be at least 16 years old (currently {age})"
    elif age > 80:
        return False, f"⚠️ Age seems high ({age} years old)"
    else:
        return True, f"✅ Age: {age} years old"


def render_employee_form(employee: Optional[Employee] = None) -> Dict[str, Any]:
    """Render employee form and return form data."""
    is_edit = employee is not None
    
    # Initialize session state for form data if not exists
    form_key = f"{'edit' if is_edit else 'add'}_employee_form_data"
    if form_key not in st.session_state:
        st.session_state[form_key] = {}
    
    with st.form(f"{'edit' if is_edit else 'add'}_employee_form", clear_on_submit=False):
        st.markdown('<p class="sub-header">Personal Information</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input(
                "First Name*", 
                value=employee.first_name if is_edit else st.session_state[form_key].get('first_name', ''),
                max_chars=50
            )
            
            email = st.text_input(
                "Email*",
                value=employee.email if is_edit else st.session_state[form_key].get('email', ''),
                help="Enter a valid email address (e.g., john@company.com)"
            )
            
            # Real-time email validation
            if email and not validate_email_realtime(email):
                st.warning("⚠️ Please enter a valid email address with @ symbol")
            
            birth_date = st.date_input(
                "Birth Date", 
                value=employee.birth_date if is_edit and employee.birth_date else st.session_state[form_key].get('birth_date'),
                min_value=date.today().replace(year=date.today().year - 100),  # Allow up to 100 years ago
                max_value=date.today().replace(year=date.today().year - 16),   # Must be at least 16 years old
                help="Employee must be at least 16 years old"
            )
            
            # Real-time age validation
            if birth_date:
                is_valid_age, age_message = validate_age_realtime(birth_date)
                if not is_valid_age:
                    st.error(age_message)
                else:
                    st.success(age_message)
                
        
        with col2:
            last_name = st.text_input(
                "Last Name*", 
                value=employee.last_name if is_edit else st.session_state[form_key].get('last_name', ''),
                max_chars=50
            )
            
            phone = st.text_input(
                "Phone",
                value=employee.phone if is_edit and employee.phone else st.session_state[form_key].get('phone', '')
            )
        
        st.markdown('<p class="sub-header">Employment Information</p>', unsafe_allow_html=True)
        
        col3, col4 = st.columns(2)
        with col3:
            if is_edit:
                # Show current employee ID for edit mode
                st.text_input(
                    "Employee ID", 
                    value=employee.employee_id,
                    disabled=True,
                    help="Employee ID cannot be changed"
                )
            else:
                # Show info that ID will be auto-generated
                st.info("🔄 Employee ID will be auto-generated (e.g., EMP001)")
            department = st.selectbox(
                "Department*", 
                options=list(Department), 
                format_func=lambda x: x.value,
                index=list(Department).index(employee.department) if is_edit else (list(Department).index(st.session_state[form_key].get('department', Department.ENGINEERING)) if st.session_state[form_key].get('department') else 0)
            )
            hire_date = st.date_input(
                "Hire Date*", 
                value=employee.hire_date if is_edit else st.session_state[form_key].get('hire_date', date.today()),
                max_value=date.today()
            )
        
        with col4:
            position = st.text_input(
                "Position*", 
                value=employee.position if is_edit else st.session_state[form_key].get('position', ''),
                max_chars=100
            )
            status = st.selectbox(
                "Status*", 
                options=list(EmploymentStatus), 
                format_func=lambda x: x.value,
                index=list(EmploymentStatus).index(employee.status) if is_edit else (list(EmploymentStatus).index(st.session_state[form_key].get('status', EmploymentStatus.ACTIVE)) if st.session_state[form_key].get('status') else 0)
            )
            if is_edit:
                # Show calculated years of service for edit mode
                st.number_input(
                    "Years of Service", 
                    value=employee.years_of_service,
                    disabled=True,
                    help="Years of service is calculated from hire date"
                )
            else:
                # Show info that years of service will be calculated
                st.info("📅 Years of service will be calculated from hire date")
        
        st.markdown('<p class="sub-header">Compensation & Management</p>', unsafe_allow_html=True)
        
        col5, col6 = st.columns(2)
        with col5:
            salary = st.number_input(
                "Salary*", 
                min_value=0.0, 
                step=1000.0,
                value=float(employee.salary) if is_edit else st.session_state[form_key].get('salary', 0.0),
                format="%.2f"
            )
        
        with col6:
            # Get list of potential managers
            try:
                from app.services.employee_service import EmployeeService
                employee_service = EmployeeService()
                managers = employee_service.get_managers_list()
                
                # Create manager options
                manager_options = ["No Manager"] + [f"{m['id']} - {m['name']}" for m in managers]
                
                # Find current manager
                current_manager = None
                if is_edit and employee.manager_id:
                    for m in managers:
                        if m['id'] == employee.manager_id:
                            current_manager = f"{m['id']} - {m['name']}"
                            break
                
                selected_manager = st.selectbox(
                    "Manager (Optional)",
                    options=manager_options,
                    index=manager_options.index(current_manager) if current_manager else 0,
                    help="Select a manager from existing employees"
                )
                
                # Extract manager ID
                if selected_manager == "No Manager":
                    manager_id = None
                else:
                    manager_id = int(selected_manager.split(" - ")[0])
                    
            except Exception as e:
                st.warning(f"Could not load managers: {str(e)}")
                manager_id = st.number_input(
                    "Manager ID (Optional)", 
                    min_value=1, 
                    step=1,
                    value=employee.manager_id if is_edit and employee.manager_id else None,
                    help="Enter the database ID of the manager"
                )
        
        submitted = st.form_submit_button(
            f"{'Update' if is_edit else 'Add'} Employee", 
            type="primary"
        )
        
        if submitted:
            # Create form data first
            form_data = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone': phone if phone else None,
                'birth_date': birth_date,
                'department': department,
                'position': position,
                'hire_date': hire_date,
                'status': status,
                'salary': salary,
                'manager_id': manager_id if manager_id else None
            }
            
            # Only include employee_id for edit mode
            if is_edit:
                form_data['employee_id'] = employee.employee_id
            
            # Save form data to session state IMMEDIATELY for persistence on errors
            if not is_edit:
                st.session_state[form_key] = form_data.copy()
            
            # Validate required fields
            if not all([first_name, last_name, email, position]):
                st.error("Please fill in all required fields (marked with *)")
                return None
            
            # For updates, remove non-updatable fields
            if is_edit:
                form_data.pop('employee_id', None)  # Employee ID cannot be changed
                form_data.pop('hire_date', None)    # Hire date cannot be changed
                form_data.pop('years_of_service', None)  # Years of service is calculated
                
                # Validate manager_id if provided
                if manager_id and manager_id > 0:
                    # Check if manager exists (this will be validated in the service layer)
                    pass
            
            return form_data
    
    return None


def validate_employee_data(form_data: Dict[str, Any], is_edit: bool = False) -> Optional[Employee]:
    """Validate employee form data and return Employee object."""
    
    # Pre-validate with user-friendly messages
    validation_errors = []
    
    # Email validation
    email = form_data.get('email', '')
    if email and '@' not in email:
        validation_errors.append("❌ **Invalid email address.** Please enter a valid email with @ symbol (e.g., john@company.com)")
    
    # Age validation
    birth_date = form_data.get('birth_date')
    if birth_date:
        from datetime import date
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        if age < 16:
            validation_errors.append(f"❌ **Age requirement not met.** Employee must be at least 16 years old (currently {age} years old)")
        elif age > 80:
            validation_errors.append(f"❌ **Age too high.** Please enter a reasonable birth date (currently {age} years old)")
    
    # Salary validation
    salary = form_data.get('salary', 0)
    if salary < 0:
        validation_errors.append("❌ **Invalid salary.** Salary cannot be negative")
    elif salary > 1000000:
        validation_errors.append("❌ **Salary too high.** Please enter a reasonable salary amount")
    
    # Phone validation
    phone = form_data.get('phone', '')
    if phone and len(phone) < 10:
        validation_errors.append("❌ **Invalid phone number.** Please enter a complete phone number (at least 10 digits)")
    
    # Name validation
    first_name = form_data.get('first_name', '')
    last_name = form_data.get('last_name', '')
    if first_name and len(first_name) < 2:
        validation_errors.append("❌ **First name too short.** Please enter at least 2 characters")
    if last_name and len(last_name) < 2:
        validation_errors.append("❌ **Last name too short.** Please enter at least 2 characters")
    
    # Show validation errors
    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return None
    
    # Try to create the model object
    try:
        if is_edit:
            # For updates, create EmployeeUpdate object
            update_data = {k: v for k, v in form_data.items() if v is not None}
            return EmployeeUpdate(**update_data)
        else:
            # For creation, create EmployeeCreate object
            return EmployeeCreate(**form_data)
    except ValidationError as e:
        # Handle any remaining Pydantic validation errors
        error_details = []
        for error in e.errors():
            field = error.get('loc', ['unknown'])[0]
            error_type = error.get('type', 'unknown')
            error_msg = error.get('msg', 'Unknown error')
            
            if field == 'email':
                error_details.append("❌ **Email format error.** Please enter a valid email address (e.g., john@company.com)")
            elif field == 'phone':
                error_details.append("❌ **Phone format error.** Please enter a valid phone number")
            elif 'pattern' in error_type:
                error_details.append(f"❌ **{field.title()} format error.** {error_msg}")
            else:
                error_details.append(f"❌ **{field.title()} error:** {error_msg}")
        
        for error in error_details:
            st.error(error)
        return None
