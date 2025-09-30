# Development Setup Guide

This guide will help you set up a complete development environment for the Employee Management System from scratch, on both Windows and Mac.

## 🎯 What We'll Install

- **Visual Studio Code** - Code editor and IDE
- **Git** - Version control system
- **UV** - Fast Python package manager
- **Databricks CLI** - Databricks integration tools
- **Python** - Programming language runtime

## 🪟 Windows Setup (Using Winget)

### Step 1: Install Windows Package Manager (Winget)

Winget comes pre-installed on Windows 10 (version 1709+) and Windows 11. If you don't have it:

1. Open **Microsoft Store**
2. Search for "App Installer"
3. Install the latest version

### Step 2: Install Development Tools

Open **PowerShell as Administrator** and run these commands:

```powershell
# Install Visual Studio Code
winget install Microsoft.VisualStudioCode

# Install Git
winget install Git.Git

# Install Python (latest stable version)
winget install Python.Python.3.11

# Install UV (Python package manager)
winget install Astral.UV

# Install Databricks CLI
winget install Databricks.DatabricksCLI
```

### Step 3: Verify Installations

Open a new **PowerShell** window and verify each tool:

```powershell
# Check Python
python --version

# Check Git
git --version

# Check UV
uv --version

# Check Databricks CLI
databricks --version

# Check VS Code
code --version
```

## 🍎 Mac Setup (Using Homebrew)

### Step 1: Install Homebrew

Open **Terminal** and run:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow the prompts and add Homebrew to your PATH when prompted.

### Step 2: Install Development Tools

```bash
# Install Visual Studio Code
brew install --cask visual-studio-code

# Install Git (usually pre-installed, but let's make sure)
brew install git

# Install Python
brew install python@3.11

# Install UV
brew install uv

# Install Databricks CLI
brew install databricks/tap/databricks
```

### Step 3: Verify Installations

```bash
# Check Python
python3 --version

# Check Git
git --version

# Check UV
uv --version

# Check Databricks CLI
databricks --version

# Check VS Code
code --version
```

## 🚀 Project Setup

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/merca/python_basics_pydantic.git

# Navigate to the project directory
cd python_basics_pydantic
```

### Step 2: Set Up Python Environment with UV

```bash
# Create a virtual environment and install dependencies
uv venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate

# On Mac/Linux:
source .venv/bin/activate

# Install project dependencies
uv pip install -r requirements.txt
```

### Step 3: Configure Git (First Time Setup)

```bash
# Set your name and email
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Optional: Set default branch name
git config --global init.defaultBranch main
```

## 🔧 VS Code Configuration

### Step 1: Install Recommended Extensions

Open VS Code and install these extensions:

```bash
# Open the project in VS Code
code .
```

Then install these extensions:

- **Python** (by Microsoft)
- **Pylance** (by Microsoft)
- **Python Debugger** (by Microsoft)
- **GitLens** (by GitKraken)
- **Prettier** (by Prettier)
- **Black Formatter** (by Microsoft)
- **isort** (by Microsoft)

### Step 2: Configure Python Interpreter

1. Open VS Code
2. Press `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac)
3. Type "Python: Select Interpreter"
4. Choose the interpreter from your virtual environment:
   - Windows: `.\venv\Scripts\python.exe`
   - Mac: `./venv/bin/python`

### Step 3: Configure Settings

Create `.vscode/settings.json` in your project root:

```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.sortImports.args": ["--profile", "black"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/.pytest_cache": true
  }
}
```

## 🗄️ Database Setup

### Step 1: Initialize Database

```bash
# The database will be created automatically when you run the app
# But you can also initialize it manually:

python -c "
from src.database.connection import initialize_database
db_manager = initialize_database(create_tables=True, sample_data=False)
print('Database initialized successfully!')
"
```

### Step 2: Add Sample Data (Optional)

```bash
python -c "
from src.database.sample_data import insert_sample_data
from src.database.connection import get_database_manager

db_manager = get_database_manager()
result = insert_sample_data(db_manager, employee_count=10, user_count=3)
print(f'Added {result[\"employees_created\"]} employees and {result[\"users_created\"]} users!')
"
```

## 🚀 Running the Application

### Step 1: Start the Streamlit App

```bash
# Make sure your virtual environment is activated
# On Windows:
.venv\Scripts\activate

# On Mac/Linux:
source .venv/bin/activate

# Run the application
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### Step 2: Run Jupyter Notebooks

```bash
# Start Jupyter Lab
jupyter lab

# Or start Jupyter Notebook
jupyter notebook
```

## 🧪 Testing Your Setup

### Step 1: Run Tests

```bash
# Install test dependencies
uv pip install pytest pytest-cov

# Run tests
pytest

# Run tests with coverage
pytest --cov=src tests/
```

### Step 2: Check Code Quality

```bash
# Install development tools
uv pip install black isort flake8 mypy

# Format code
black .

# Sort imports
isort .

# Lint code
flake8 src/

# Type checking
mypy src/
```

## 🔧 Databricks Setup (Optional)

### Step 1: Configure Databricks CLI

```bash
# Configure Databricks CLI
databricks configure

# You'll need:
# - Databricks host (e.g., https://your-workspace.cloud.databricks.com)
# - Personal access token
```

### Step 2: Test Databricks Connection

```bash
# Test connection
databricks workspace list

# List clusters
databricks clusters list
```

## 🐛 Troubleshooting

### Common Issues

**Python not found:**

```bash
# Windows: Add Python to PATH
# Mac: Check if Python is in your PATH
echo $PATH
```

**UV not found:**

```bash
# Windows: Restart PowerShell after installation
# Mac: Add to PATH in ~/.zshrc or ~/.bash_profile
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**VS Code not opening from terminal:**

```bash
# Windows: Add VS Code to PATH
# Mac: Install "Shell Command: Install 'code' command in PATH" from VS Code
```

**Database connection errors:**

```bash
# Check if SQLite is working
python -c "import sqlite3; print('SQLite version:', sqlite3.version)"
```

**Streamlit not starting:**

```bash
# Check if port 8501 is available
netstat -an | grep 8501

# Try a different port
streamlit run app.py --server.port 8502
```

### Getting Help

1. **Check the logs**: Look for error messages in the terminal
2. **Restart your terminal**: Close and reopen PowerShell/Terminal
3. **Restart VS Code**: Close and reopen VS Code
4. **Check virtual environment**: Make sure it's activated
5. **Update tools**: Run `winget upgrade` (Windows) or `brew upgrade` (Mac)

## 📚 Next Steps

Once your development environment is set up:

1. **Explore the codebase**: Start with `app.py` and the `src/` directory
2. **Run the application**: Use `streamlit run app.py`
3. **Try the notebooks**: Open `notebooks/01_python_basics.ipynb`
4. **Make changes**: Edit code and see live updates
5. **Run tests**: Use `pytest` to verify everything works

## 🎉 You're Ready!

Your development environment is now set up with:

- ✅ Visual Studio Code with Python extensions
- ✅ Git for version control
- ✅ UV for fast Python package management
- ✅ Databricks CLI for cloud integration
- ✅ Python virtual environment
- ✅ All project dependencies installed

Happy coding! 🚀
