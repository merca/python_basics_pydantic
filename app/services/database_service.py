"""
Database service for managing connections and sessions.
"""

import streamlit as st
import sys
import os
from contextlib import contextmanager
from typing import Generator, Tuple, Optional

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from src.database.connection import (
    initialize_database, get_database_manager, 
    check_database_health
)
from src.database.repository import EmployeeRepository


@st.cache_resource
def get_database_manager_cached():
    """Get cached database manager."""
    try:
        return initialize_database(create_tables=True, sample_data=False)
    except Exception as e:
        st.error(f"Database initialization failed: {e}")
        return None


@contextmanager
def get_employee_repository() -> Generator[Tuple[EmployeeRepository, any], None, None]:
    """Context manager for employee repository with automatic session cleanup."""
    db_manager = get_database_manager_cached()
    if not db_manager:
        raise Exception("Database not available")
    
    session = db_manager.get_session()
    try:
        yield EmployeeRepository(session), session
    finally:
        session.close()




def get_database_health() -> dict:
    """Get database health status."""
    return check_database_health()


def get_database_url() -> str:
    """Get database URL for display."""
    db_manager = get_database_manager_cached()
    return db_manager.database_url if db_manager else 'Not connected'
