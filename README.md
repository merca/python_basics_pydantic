# Python Basics with Pydantic

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Pydantic](https://img.shields.io/badge/pydantic-2.0+-green.svg)](https://docs.pydantic.dev/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A comprehensive tutorial repository covering Python fundamentals with Pydantic, specifically designed for Databricks and Streamlit development workflows.

## 🎯 Overview

This repository provides a hands-on learning experience for Python developers looking to master:

- **Python Fundamentals**: Core concepts, data structures, and object-oriented programming
- **Pydantic Data Modeling**: Type-safe data validation and serialization
- **Databricks Integration**: ETL pipelines, data quality monitoring, and ML feature stores
- **Streamlit Applications**: Interactive web apps with real-time data validation

## 📚 What's Included

### 📓 Jupyter Notebooks
- **[01_python_basics.ipynb](notebooks/01_python_basics.ipynb)**: Python fundamentals covering data types, control structures, functions, and OOP
- **[02_pydantic_modeling.ipynb](notebooks/02_pydantic_modeling.ipynb)**: Comprehensive Pydantic guide with validation, serialization, and advanced patterns
- **[03_databricks_integration.ipynb](notebooks/03_databricks_integration.ipynb)**: Integration patterns for Databricks workflows and Delta Lake
- **[04_test_verification.ipynb](notebooks/04_test_verification.ipynb)**: Testing and verification of all code examples

### 🖥️ Interactive Applications
- **[Streamlit Demo App](examples/streamlit_app.py)**: Interactive web application demonstrating Pydantic validation with data visualization

### 📁 Project Structure
```
python_basics_pydantic/
├── notebooks/           # Jupyter notebooks with tutorials
├── examples/           # Example applications and code
├── src/               # Source code modules
├── tests/             # Test files
├── docs/              # Documentation
├── requirements.txt   # Python dependencies
├── pyproject.toml     # Project configuration
└── README.md         # This file
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
   # Basic installation
   pip install -r requirements.txt
   
   # Or install with optional dependencies
   pip install -e .[dev,jupyter,viz]
   ```

### Running the Examples

#### Jupyter Notebooks
```bash
# Start Jupyter Lab
jupyter lab

# Or use Jupyter Notebook
jupyter notebook
```

Navigate to the `notebooks/` directory and start with `01_python_basics.ipynb`.

#### Streamlit Application
```bash
# Run the interactive demo
streamlit run examples/streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`.

## 📖 Learning Path

### 1. Python Fundamentals (01_python_basics.ipynb)
- Data types and variables
- Control structures (if/else, loops)
- Functions and lambda expressions
- Object-oriented programming
- Error handling
- File operations and JSON
- Type hints

### 2. Pydantic Modeling (02_pydantic_modeling.ipynb)
- Introduction to Pydantic models
- Field validation and constraints
- Custom validators
- Nested models and complex structures
- Serialization and deserialization
- Error handling patterns
- Performance considerations

### 3. Databricks Integration (03_databricks_integration.ipynb)
- Data pipeline models
- ETL validation patterns
- Feature engineering with validation
- Data quality monitoring
- ML feature store integration
- Delta Lake schema management

### 4. Interactive Applications
- Streamlit app with real-time validation
- Data visualization with Plotly
- User input validation
- Error handling in web interfaces

## 🎯 Use Cases

### For Data Engineers
- **ETL Pipelines**: Validate data at every stage of processing
- **Data Quality**: Monitor and ensure data integrity
- **Schema Evolution**: Manage changes in data structures safely

### For Data Scientists
- **Feature Engineering**: Create validated feature transformations
- **Model Input Validation**: Ensure ML model inputs are correct
- **Experiment Tracking**: Structured experiment configurations

### For Web Developers
- **API Development**: Type-safe request/response models
- **Form Validation**: Client and server-side validation
- **Configuration Management**: Validated application settings

### For Databricks Users
- **Notebook Development**: Better code organization and validation
- **Job Configuration**: Type-safe job parameters
- **Delta Lake Integration**: Schema validation and evolution

## 🛠️ Key Features Demonstrated

### Pydantic Features
- ✅ **Type Safety**: Runtime type checking with clear error messages
- ✅ **Data Validation**: Built-in and custom validators
- ✅ **JSON Serialization**: Easy conversion between Python objects and JSON
- ✅ **Field Constraints**: Min/max values, string patterns, custom logic
- ✅ **Model Composition**: Nested models and inheritance patterns
- ✅ **Error Handling**: Graceful validation error management

### Integration Patterns
- 🔧 **Databricks Workflows**: ETL pipelines with validation
- 🔧 **Streamlit Applications**: Interactive data apps
- 🔧 **Delta Lake**: Schema evolution and constraints
- 🔧 **ML Pipelines**: Feature stores and model validation
- 🔧 **Data Quality**: Automated monitoring and reporting

## 📊 Example: Employee Data Model

```python
from pydantic import BaseModel, Field, validator
from datetime import date
from typing import Optional

class Employee(BaseModel):
    id: int = Field(gt=0, description="Employee ID must be positive")
    name: str = Field(min_length=2, max_length=100)
    email: str
    department: str
    salary: float = Field(gt=0, le=1000000)
    hire_date: date
    is_active: bool = True
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Please enter a valid email address')
        return v.lower()
    
    @validator('name')
    def validate_name(cls, v):
        return v.title()

# Usage
employee = Employee(
    id=1,
    name="john doe",
    email="john@company.com",
    department="Engineering",
    salary=75000,
    hire_date="2023-01-15"
)

print(employee.json(indent=2))
```

## 🧪 Testing

Run the test suite to verify all examples:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test categories
pytest -m "not slow"  # Skip slow tests
```

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

## 📚 Additional Resources

### Official Documentation
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Databricks Documentation](https://docs.databricks.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)

### Related Projects
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework using Pydantic
- [SQLModel](https://sqlmodel.tiangolo.com/) - SQL databases with Python type hints
- [Typer](https://typer.tiangolo.com/) - CLI applications with type hints

### Learning Resources
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Data Classes](https://docs.python.org/3/library/dataclasses.html)
- [JSON Schema](https://json-schema.org/)

## ❓ Troubleshooting

### Common Issues

**ImportError: No module named 'pydantic'**
```bash
pip install pydantic>=2.0.0
```

**Streamlit app not loading**
```bash
# Ensure Streamlit is installed
pip install streamlit>=1.25.0

# Check if port is available
streamlit run examples/streamlit_app.py --server.port 8502
```

**Jupyter notebook kernel issues**
```bash
# Install ipykernel in your virtual environment
pip install ipykernel
python -m ipykernel install --user --name=python_basics_pydantic
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Pydantic](https://github.com/pydantic/pydantic) team for the excellent validation library
- [Streamlit](https://github.com/streamlit/streamlit) team for the web app framework
- [Databricks](https://databricks.com/) for the data platform inspiration
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