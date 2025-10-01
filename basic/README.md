# 🔰 Basic Version - Pydantic Fundamentals

Welcome to the **Basic Version** of the Employee Management System! This is your first step in learning Pydantic and modern Python data validation.

## 🎯 Learning Objectives

By the end of this tutorial, you'll understand:

✅ **Pydantic BaseModel** - The foundation of data validation  
✅ **Type Hints & Constraints** - Field validation with min_length, max_length, ge  
✅ **Enums** - Type-safe choices for departments and status  
✅ **Custom Validators** - Business logic validation with @field_validator  
✅ **Computed Properties** - Derived fields like age and years_of_service  
✅ **JSON Serialization** - Converting models to/from JSON  
✅ **Error Handling** - ValidationError handling and user feedback  

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Basic understanding of Python classes and type hints

### Installation

#### Option 1: Using uv (Recommended - Much Faster!) ⚡

```bash
# Navigate to the basic directory
cd basic

# Create virtual environment and install dependencies (one step!)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Run the application
streamlit run app.py
```

#### Option 2: Traditional Method 🐌

```bash
# Navigate to the basic directory
cd basic

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux  
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

#### Option 3: Helper Script (Easiest!) 🚀

```bash
# From repository root - handles everything automatically!
python run_version.py basic
```

The application will open in your browser at `http://localhost:8501`

## 📚 What's Inside

### Single File Architecture
This version uses a **single file** (`app.py`) to keep things simple and focused on learning Pydantic concepts.

```python
# Key Learning Components:
📝 Pydantic Models (Employee, Department, EmploymentStatus)
🔍 Custom Validators (@field_validator decorators)
💾 In-Memory Storage (Streamlit session state)
🖥️ Interactive UI (Streamlit forms and displays)
📊 JSON Operations (Import/Export functionality)
```

### Core Features

#### 1. **Data Validation in Action**
- Real-time form validation
- Custom business rules (age >= 16, salary limits)
- Type safety with Enums
- Email format validation

#### 2. **Interactive Learning**
- Add/remove employees
- See validation errors in real-time
- Export data to JSON
- Import and validate JSON data

#### 3. **Educational Components**
- Built-in learning notes
- Code examples in the UI
- Progress indicators
- Next steps guidance

## 🧭 Navigation

The app includes 4 main sections:

1. **Add Employee** - Practice with Pydantic validation
2. **View Employees** - See your data and computed properties  
3. **JSON Operations** - Learn serialization/deserialization
4. **Learning Notes** - Understand key concepts

## 💡 Key Pydantic Concepts Demonstrated

### 1. BaseModel with Validation
```python
class Employee(BaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    email: EmailStr  # Automatic email validation
    salary: Decimal = Field(ge=0, le=1000000)
```

### 2. Custom Validators
```python
@field_validator('birth_date')
@classmethod
def validate_birth_date(cls, v: Optional[date]) -> Optional[date]:
    if v and (date.today().year - v.year) < 16:
        raise ValueError('Employee must be at least 16 years old')
    return v
```

### 3. Computed Properties
```python
@property
def full_name(self) -> str:
    return f"{self.first_name} {self.last_name}"

@property
def age(self) -> Optional[int]:
    # Calculate age from birth_date...
```

### 4. JSON Serialization
```python
# Model to JSON
json_data = employee.model_dump(mode='json')

# JSON to Model
employee = Employee(**json_data)
```

## 🎓 Learning Exercises

Try these hands-on exercises:

### Exercise 1: Basic Validation
1. Add an employee with invalid data (empty name, invalid email)
2. Observe the validation errors
3. Fix the data and successfully add the employee

### Exercise 2: Custom Validators
1. Try adding an employee who is 15 years old
2. See the custom age validation in action
3. Modify the age validation logic

### Exercise 3: JSON Operations
1. Add several employees
2. Export them to JSON
3. Clear the list and import them back
4. Try importing invalid JSON data

### Exercise 4: Enums and Type Safety
1. Notice how department and status use Enums
2. Try to understand why this is better than plain strings
3. Look at the generated JSON to see enum values

## 🚧 Common Issues & Solutions

### **Validation Errors**
If you see validation errors, they're intentional! This is how you learn:
- Read the error message carefully
- Identify which field failed validation
- Check the field constraints in the code
- Fix your input and try again

### **Email Validation**
Make sure to use valid email format: `name@domain.com`

### **Date Validation**
- Birth dates: Must result in age >= 16
- Hire dates: Cannot be in the future

## 📈 Next Steps

Ready to level up? The **Intermediate Version** adds:

🗄️ **Database Integration** - SQLite with SQLAlchemy  
📁 **File Organization** - Proper module structure  
🔄 **CRUD Operations** - Create, Read, Update, Delete  
📊 **Data Relationships** - Foreign keys and joins  
🛡️ **Advanced Validation** - Cross-field validation  

Run the intermediate version: `streamlit run ../intermediate/app.py`

## 🤝 Tips for Success

1. **Take Your Time** - This is about understanding, not speed
2. **Experiment** - Try breaking things to understand validation
3. **Read Error Messages** - They're designed to be helpful
4. **Use the Learning Notes** - Built-in documentation in the app
5. **Ask Questions** - Use the concepts in your own projects

## 📊 Stats

- **Lines of Code**: ~620
- **Dependencies**: 3 core packages
- **Learning Time**: 30-60 minutes
- **Complexity**: Beginner-friendly
- **Focus**: Pydantic fundamentals

---

**Happy Learning! 🚀**

*This is the first step in your Pydantic journey. Master these basics before moving to the intermediate version.*