"""
Database Connection Management

This module provides database connection and session management
using SQLAlchemy with SQLite for local development.
"""

import os
import logging
from pathlib import Path
from typing import Generator, Optional
from contextlib import contextmanager

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool

# Set up logging
logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Database connection manager for SQLite.
    
    Handles connection creation, session management, and database configuration.
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database manager.
        
        Args:
            database_url: Database URL. If None, will use default SQLite database.
        """
        if database_url is None:
            # Create database directory if it doesn't exist
            db_dir = Path("data")
            db_dir.mkdir(exist_ok=True)
            database_url = f"sqlite:///data/app.db"
        
        self.database_url = database_url
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=self.engine
        )
        
        # Configure SQLite for better concurrency
        if "sqlite" in database_url:
            self._configure_sqlite()
    
    def _create_engine(self) -> Engine:
        """Create and configure database engine."""
        if "sqlite" in self.database_url:
            # SQLite specific configuration
            engine = create_engine(
                self.database_url,
                connect_args={
                    "check_same_thread": False,  # Allow multiple threads
                    "timeout": 30,  # Connection timeout in seconds
                },
                poolclass=StaticPool,  # Use static pool for SQLite
                echo=os.getenv("DATABASE_DEBUG", "false").lower() == "true"
            )
        else:
            # Generic database configuration
            engine = create_engine(
                self.database_url,
                echo=os.getenv("DATABASE_DEBUG", "false").lower() == "true"
            )
        
        return engine
    
    def _configure_sqlite(self) -> None:
        """Configure SQLite specific settings."""
        
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Set SQLite pragmas for better performance and reliability."""
            cursor = dbapi_connection.cursor()
            
            # Enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys=ON")
            
            # Set journal mode to WAL for better concurrency
            cursor.execute("PRAGMA journal_mode=WAL")
            
            # Set synchronous mode for balance of safety and performance
            cursor.execute("PRAGMA synchronous=NORMAL")
            
            # Set cache size (negative value = KB)
            cursor.execute("PRAGMA cache_size=-64000")  # 64MB
            
            # Enable memory-mapped I/O
            cursor.execute("PRAGMA mmap_size=268435456")  # 256MB
            
            cursor.close()
    
    def get_session(self) -> Session:
        """
        Get a new database session.
        
        Returns:
            SQLAlchemy session instance
        """
        return self.SessionLocal()
    
    @contextmanager
    def session_scope(self):
        """
        Context manager for database sessions with automatic cleanup.
        
        Yields:
            SQLAlchemy session with automatic commit/rollback
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def create_tables(self) -> None:
        """Create all database tables."""
        from .models import Base
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created successfully")
    
    def drop_tables(self) -> None:
        """Drop all database tables."""
        from .models import Base
        Base.metadata.drop_all(bind=self.engine)
        logger.info("Database tables dropped successfully")
    
    def recreate_tables(self) -> None:
        """Drop and recreate all database tables."""
        self.drop_tables()
        self.create_tables()
    
    def test_connection(self) -> bool:
        """
        Test database connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            with self.session_scope() as session:
                session.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def get_database_info(self) -> dict:
        """
        Get information about the database.
        
        Returns:
            Dictionary with database information
        """
        info = {
            "database_url": self.database_url,
            "engine": str(self.engine),
            "pool_size": getattr(self.engine.pool, 'size', 'N/A'),
            "connection_test": self.test_connection()
        }
        
        if "sqlite" in self.database_url:
            # Add SQLite specific info
            try:
                with self.session_scope() as session:
                    result = session.execute(text("PRAGMA database_list")).fetchall()
                    info["sqlite_databases"] = [dict(row._mapping) for row in result]
                    
                    result = session.execute(text("PRAGMA compile_options")).fetchall()
                    info["sqlite_compile_options"] = [row[0] for row in result]
            except Exception as e:
                logger.warning(f"Could not get SQLite info: {e}")
        
        return info


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """
    Get the global database manager instance.
    
    Returns:
        DatabaseManager instance
    """
    global _db_manager
    
    if _db_manager is None:
        database_url = os.getenv("DATABASE_URL")
        _db_manager = DatabaseManager(database_url)
        logger.info(f"Initialized database manager with URL: {_db_manager.database_url}")
    
    return _db_manager


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session in FastAPI/Streamlit.
    
    Yields:
        SQLAlchemy session
    """
    db_manager = get_database_manager()
    with db_manager.session_scope() as session:
        yield session


def initialize_database(create_tables: bool = True, sample_data: bool = False) -> DatabaseManager:
    """
    Initialize the database with optional table creation and sample data.
    
    Args:
        create_tables: Whether to create database tables
        sample_data: Whether to insert sample data
    
    Returns:
        DatabaseManager instance
    """
    db_manager = get_database_manager()
    
    if create_tables:
        db_manager.create_tables()
    
    if sample_data:
        from .sample_data import insert_sample_data
        insert_sample_data(db_manager)
    
    return db_manager


def reset_database() -> DatabaseManager:
    """
    Reset the database by dropping and recreating all tables.
    
    Returns:
        DatabaseManager instance
    """
    db_manager = get_database_manager()
    db_manager.recreate_tables()
    logger.info("Database reset completed")
    return db_manager


# Connection health check
def check_database_health() -> dict:
    """
    Check database health and return status information.
    
    Returns:
        Dictionary with health status
    """
    try:
        db_manager = get_database_manager()
        info = db_manager.get_database_info()
        
        health_status = {
            "status": "healthy" if info["connection_test"] else "unhealthy",
            "database_url": info["database_url"],
            "timestamp": os.times(),
            "details": info
        }
    except Exception as e:
        health_status = {
            "status": "error",
            "error": str(e),
            "timestamp": os.times()
        }
    
    return health_status