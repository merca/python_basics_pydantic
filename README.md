# Employee Management System with Pydantic & Streamlit

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Pydantic](https://img.shields.io/badge/pydantic-2.0+-green.svg)](https://docs.pydantic.dev/)
[![SQLite](https://img.shields.io/badge/database-sqlite-blue.svg)](https://sqlite.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.25+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A comprehensive Employee Management System built with modern Python technologies, demonstrating production-ready application development with Pydantic data validation, SQLite database integration, and Streamlit web interface.

## 🎯 Overview

This repository showcases a complete Employee Management System featuring:

- **Pydantic v2**: Advanced data validation, serialization, and type safety for employee data
- **SQLite Database**: Local database with SQLAlchemy ORM integration and connection management
- **Streamlit Web App**: Interactive dashboard with real-time data visualization and CRUD operations
- **Repository Pattern**: Clean architecture with separation of concerns
- **Data Validation**: Comprehensive field validation with custom constraints and error handling
- **Sample Data**: Automated data generation for testing and demonstration

## 🚀 Features

### 📊 Dashboard & Analytics

- **Real-time Metrics**: Total employees, average salary, department distribution
- **Interactive Charts**: Department pie charts, salary distribution, years of service histograms
- **Status Tracking**: Active/inactive employee monitoring
- **Performance Analytics**: Salary statistics and department insights

### 👥 Employee Management

- **Complete CRUD Operations**: Create, read, update, and delete employees
- **Advanced Search & Filtering**: Filter by department, status, and search terms
- **Pagination**: Efficient handling of large employee datasets
- **Data Validation**: Real-time form validation with Pydantic models

### 🗄️ Database Features

- **SQLite Integration**: Local database with SQLAlchemy ORM
- **Connection Management**: Automatic database initialization and health monitoring
- **Sample Data Generation**: Automated creation of realistic test data
- **Export Functionality**: CSV and JSON export capabilities

### 🔧 Technical Features

- **Type Safety**: Full type hints with Pydantic validation
- **Error Handling**: Comprehensive error management and user feedback
- **Data Integrity**: Foreign key relationships and constraint validation
- **Performance**: Optimized queries and efficient data loading

## 📁 Project Structure

```
python_basics_pydantic/
├── app.py                    # Main Streamlit application
├── src/                      # Source code modules
│   ├── models/               # Pydantic data models
│   │   ├── base.py          # Base model classes
│   │   ├── employee.py      # Employee models and validation
│   │   ├── user.py          # User authentication models
│   │   └── validation.py    # Validation response models
│   └── database/            # Database layer
│       ├── connection.py    # Database connection management
│       ├── models.py        # SQLAlchemy ORM models
│       ├── repository.py   # Data access layer
│       └── sample_data.py   # Sample data generation
├── examples/                 # Example applications
│   ├── streamlit_app.py    # Simple Streamlit demo
│   └── api/                # FastAPI examples
├── notebooks/               # Jupyter tutorials
│   ├── 01_python_basics.ipynb
│   ├── 02_pydantic_modeling.ipynb
│   ├── 03_databricks_integration.ipynb
│   └── 04_test_verification.ipynb
├── data/                    # Database files
├── tests/                   # Test files
├── docs/                    # Documentation
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Git (for cloning the repository)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/merca/python_basics_pydantic.git
   cd python_basics_pydantic
   ```

2. **Create a virtual environment**

   ```bash
   # Using venv
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

#### Main Employee Management System

```bash
# Run the main Streamlit application
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501` with a full-featured Employee Management System.

#### Jupyter Notebooks

```bash
# Start Jupyter Lab
jupyter lab

# Or use Jupyter Notebook
jupyter notebook
```

Navigate to the `notebooks/` directory for interactive tutorials.

#### Example Applications

```bash
# Run the simple Streamlit demo
streamlit run examples/streamlit_app.py

# Run FastAPI examples (if available)
cd examples/api
python employee_api.py
```

## 📖 Application Pages

### 📊 Dashboard

- **Overview Metrics**: Total employees, average salary, department counts
- **Interactive Charts**: Department distribution, salary analysis, years of service
- **Real-time Updates**: Live data visualization with filtering options
- **Quick Actions**: Add sample data, export functionality

### ➕ Add Employee

- **Form Validation**: Real-time validation with Pydantic models
- **Field Constraints**: Email validation, phone number patterns, salary ranges
- **Manager Selection**: Hierarchical employee relationships
- **Skills Management**: Multi-skill tracking and validation

### 📋 View Employees

- **Advanced Filtering**: Filter by department, status, search terms
- **Pagination**: Efficient handling of large datasets
- **Sortable Columns**: Click to sort by any field
- **Employee Details**: Comprehensive employee information display

### ✏️ Edit Employee

- **Update Forms**: Pre-populated forms with current data
- **Validation**: Same validation rules as creation
- **Delete Functionality**: Safe employee deletion with confirmation
- **Change Tracking**: Visual indicators for modified fields

### 🔧 Database Management

- **Health Monitoring**: Database connection status and diagnostics
- **Sample Data**: Generate realistic test data
- **Export Tools**: CSV and JSON export functionality
- **Reset Options**: Clear data or reset with sample data

## 🛠️ Key Technologies

### Pydantic Features Demonstrated

- ✅ **Type Safety**: Runtime type checking with clear error messages
- ✅ **Data Validation**: Built-in and custom validators for all fields
- ✅ **JSON Serialization**: Easy conversion between Python objects and JSON
- ✅ **Field Constraints**: Min/max values, string patterns, custom logic
- ✅ **Model Composition**: Nested models and inheritance patterns
- ✅ **Error Handling**: Graceful validation error management

### Database Integration

- 🔧 **SQLAlchemy ORM**: Object-relational mapping with type safety
- 🔧 **Repository Pattern**: Clean separation of data access logic
- 🔧 **Connection Management**: Automatic database initialization and health checks
- 🔧 **Migration Support**: Schema evolution and data migration tools

### Web Interface

- 🔧 **Streamlit**: Interactive web application framework
- 🔧 **Real-time Validation**: Client-side and server-side validation
- 🔧 **Data Visualization**: Plotly charts and interactive graphs
- 🔧 **Responsive Design**: Mobile-friendly interface

## 📊 Example: Employee Data Model

```python
from pydantic import BaseModel, Field, field_validator
from datetime import date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from enum import Enum

class Department(str, Enum):
    ENGINEERING = "engineering"
    MARKETING = "marketing"
    SALES = "sales"
    HR = "hr"
    FINANCE = "finance"
    OPERATIONS = "operations"

class EmploymentStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TERMINATED = "terminated"
    ON_LEAVE = "on_leave"

class Employee(BaseModel):
    id: Optional[int] = None
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: str = Field(pattern=r'^[^@]+@[^@]+\.[^@]+$')
    phone: Optional[str] = Field(pattern=r'^\+?[\d\s\-\(\)\.x]+$')
    birth_date: Optional[date] = None
    employee_id: str = Field(pattern=r'^[A-Z0-9]+$')
    department: Department
    position: str = Field(min_length=1, max_length=100)
    hire_date: date
    salary: Decimal = Field(ge=0, decimal_places=2)
    status: EmploymentStatus = EmploymentStatus.ACTIVE
    manager_id: Optional[int] = None
    skills: List[str] = Field(default_factory=list)
    additional_metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        return v.lower()

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def years_of_service(self) -> float:
        today = date.today()
        delta = today - self.hire_date
        return round(delta.days / 365.25, 1)
```

## 🧪 Testing

Run the test suite to verify all functionality:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test categories
pytest -m "not slow"  # Skip slow tests
```

## 🎯 Use Cases

### For HR Professionals

- **Employee Records**: Complete employee information management
- **Department Analytics**: Track employee distribution and trends
- **Performance Monitoring**: Salary analysis and department insights
- **Data Export**: Generate reports for external systems

### For Developers

- **Pydantic Learning**: Comprehensive examples of data validation
- **Database Integration**: SQLAlchemy ORM patterns and best practices
- **Web Development**: Streamlit application architecture
- **Type Safety**: Modern Python development with type hints

### For Data Analysts

- **Data Visualization**: Interactive charts and analytics
- **Export Functionality**: CSV and JSON data export
- **Sample Data**: Realistic test data generation
- **Database Queries**: SQLAlchemy query patterns and optimization

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Run the test suite (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📋 Development Setup

For contributors and advanced users:

```bash
# Install development dependencies
pip install -e .[dev,jupyter,viz,docs]

# Set up pre-commit hooks
pre-commit install

# Run code formatting
black .
isort .

# Run type checking
mypy src/

# Run linting
flake8 src/
```

## ❓ Troubleshooting

### Common Issues

**Streamlit app not loading**

```bash
# Ensure Streamlit is installed
pip install streamlit>=1.25.0

# Check if port is available
streamlit run app.py --server.port 8502
```

**Database connection errors**

```bash
# Check if SQLite is working
python -c "import sqlite3; print('SQLite version:', sqlite3.version)"
```

**Import errors**

```bash
# Ensure all dependencies are installed
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

## 📚 Additional Resources

### Official Documentation

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

### Related Projects

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework using Pydantic
- [SQLModel](https://sqlmodel.tiangolo.com/) - SQL databases with Python type hints
- [Typer](https://typer.tiangolo.com/) - CLI applications with type hints

### Learning Resources

- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Data Classes](https://docs.python.org/3/library/dataclasses.html)
- [JSON Schema](https://json-schema.org/)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Pydantic](https://github.com/pydantic/pydantic) team for the excellent validation library
- [Streamlit](https://github.com/streamlit/streamlit) team for the web app framework
- [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy) team for the ORM library
- Python community for continuous innovation

## 📞 Support

If you have questions or need help:

1. Check the [documentation](notebooks/) and examples
2. Search [existing issues](https://github.com/merca/python_basics_pydantic/issues)
3. Create a [new issue](https://github.com/merca/python_basics_pydantic/issues/new) with details
4. Join the discussion in our [community forums](https://github.com/merca/python_basics_pydantic/discussions)

---

**Happy Learning! 🚀**

Made with ❤️ for the Python community
