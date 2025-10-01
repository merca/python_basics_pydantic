# 🛠️ Developer Setup Guide

**Complete setup instructions for Python Basics with Pydantic from a fresh operating system installation.**

## 📋 Table of Contents

- [🖥️ System Prerequisites](#️-system-prerequisites)
- [🐍 Python Installation](#-python-installation)
- [📦 Package Manager Setup](#-package-manager-setup)
- [🔧 Development Tools](#-development-tools)
- [📁 Repository Setup](#-repository-setup)
- [🚀 Quick Start Verification](#-quick-start-verification)
- [🐛 Troubleshooting](#-troubleshooting)
- [⚙️ Advanced Configuration](#️-advanced-configuration)

## 🖥️ System Prerequisites

### Windows 10/11
```powershell
# Check Windows version
winver

# Enable Windows Subsystem for Linux (optional but recommended)
wsl --install

# Install Windows Terminal (recommended)
winget install Microsoft.WindowsTerminal
```

### macOS
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install Homebrew (package manager)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Linux (Ubuntu/Debian)
```bash
# Update package list
sudo apt update && sudo apt upgrade -y

# Install essential build tools
sudo apt install -y build-essential curl git wget software-properties-common
```

### Linux (CentOS/RHEL/Fedora)
```bash
# CentOS/RHEL
sudo yum groupinstall -y "Development Tools"
sudo yum install -y curl git wget

# Fedora
sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y curl git wget
```

## 🐍 Python Installation

### Option 1: Official Python Installer (Recommended)

#### Windows
```powershell
# Download and install Python 3.11+ from python.org
# OR use winget
winget install Python.Python.3.11

# Verify installation
python --version
pip --version
```

#### macOS
```bash
# Using Homebrew
brew install python@3.11

# Add to PATH (add to ~/.zshrc or ~/.bash_profile)
export PATH="/opt/homebrew/bin:$PATH"

# Verify installation
python3 --version
pip3 --version
```

#### Linux
```bash
# Ubuntu/Debian (Python 3.11+)
sudo apt install -y python3.11 python3.11-venv python3.11-pip

# CentOS/RHEL/Fedora
sudo dnf install -y python3.11 python3.11-pip python3.11-venv

# Verify installation
python3 --version
pip3 --version
```

### Option 2: pyenv (Advanced Users)

#### Install pyenv
```bash
# macOS
brew install pyenv

# Linux
curl https://pyenv.run | bash

# Windows (use pyenv-win)
git clone https://github.com/pyenv-win/pyenv-win.git %USERPROFILE%\.pyenv
```

#### Configure pyenv
```bash
# Add to shell profile (~/.zshrc, ~/.bashrc, etc.)
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"

# Reload shell
source ~/.zshrc  # or ~/.bashrc

# Install Python
pyenv install 3.11.6
pyenv global 3.11.6

# Verify
python --version
```

### Option 3: Anaconda/Miniconda

#### Install Miniconda
```bash
# Download installer for your platform from https://docs.conda.io/en/latest/miniconda.html

# Linux/macOS
bash Miniconda3-latest-Linux-x86_64.sh  # or MacOSX-x86_64.sh

# Create environment
conda create -n pydantic-learning python=3.11
conda activate pydantic-learning
```

## 📦 Package Manager Setup

### pip Configuration
```bash
# Upgrade pip to latest version
python -m pip install --upgrade pip

# Configure pip for faster installations (optional)
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << EOF
[global]
timeout = 60
index-url = https://pypi.org/simple/
trusted-host = pypi.org
               pypi.python.org
               files.pythonhosted.org
EOF
```

### Virtual Environment Tools
```bash
# Install virtualenv (alternative to venv)
pip install virtualenv

# Install pipenv (advanced dependency management)
pip install pipenv

# Install poetry (modern dependency management)
pip install poetry
```

## 🔧 Development Tools

### Essential Tools

#### Git
```bash
# Windows
winget install Git.Git

# macOS
brew install git

# Linux
sudo apt install git  # Ubuntu/Debian
sudo dnf install git  # Fedora
```

#### Configure Git
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global init.defaultBranch main
```

### Code Editors

#### Visual Studio Code (Recommended)
```bash
# Windows
winget install Microsoft.VisualStudioCode

# macOS
brew install --cask visual-studio-code

# Linux
# Download from https://code.visualstudio.com/
```

**Essential VS Code Extensions:**
```bash
# Install via VS Code command palette (Ctrl/Cmd + P)
ext install ms-python.python
ext install ms-python.black-formatter
ext install ms-python.isort
ext install ms-python.mypy-type-checker
ext install ms-vscode.vscode-json
ext install redhat.vscode-yaml
```

#### Alternative Editors
```bash
# PyCharm Community
# Download from https://www.jetbrains.com/pycharm/download/

# Cursor (AI-powered)
# Download from https://cursor.sh/

# Sublime Text
# Download from https://www.sublimetext.com/
```

### Terminal Enhancement (Optional)

#### Oh My Zsh (macOS/Linux)
```bash
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

#### PowerShell 7 (Windows)
```powershell
winget install Microsoft.PowerShell

# Install Oh My Posh
winget install JanDeDobbeleer.OhMyPosh
```

## 📁 Repository Setup

### Clone Repository
```bash
# Create development directory
mkdir -p ~/dev/python-learning
cd ~/dev/python-learning

# Clone repository
git clone https://github.com/merca/python_basics_pydantic.git
cd python_basics_pydantic

# Verify structure
ls -la
```

### Expected Repository Structure
```
python_basics_pydantic/
├── 🔰 basic/                     # Single-file fundamentals
│   ├── app.py                   
│   ├── requirements.txt         
│   └── README.md               
├── 📊 intermediate/              # Database integration
│   ├── models/                  
│   ├── database/               
│   ├── utils/                  
│   ├── app.py                  
│   ├── requirements.txt        
│   └── README.md              
├── 🚀 advanced/                  # Enterprise patterns
│   ├── app/                    
│   ├── src/                   
│   ├── data/                 
│   ├── main.py              
│   ├── requirements.txt     
│   └── README.md           
├── 🏃 run_version.py           # Helper script
├── 📖 README.md               # Main documentation
├── 📄 LICENSE                 
├── ⚙️ pyproject.toml         
└── 🚫 .gitignore             
```

### Helper Script Usage
```bash
# View all available versions
python run_version.py --info

# Check dependencies for a version
python run_version.py --check basic
python run_version.py --check intermediate  
python run_version.py --check advanced

# Launch a specific version (auto-setup)
python run_version.py basic
python run_version.py intermediate
python run_version.py advanced

# Get help
python run_version.py --help
```

## 🚀 Quick Start Verification

### Test Basic Version
```bash
# Navigate to basic version
cd basic

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Launch application
streamlit run app.py
```

**Expected Output:**
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

### Test Helper Script
```bash
# Go back to root
cd ..

# Test helper script
python run_version.py --info

# Expected: Version information display
python run_version.py --check basic

# Expected: ✅ Basic dependencies available
```

### Verify Python Environment
```bash
# Check Python version
python --version
# Expected: Python 3.8+ (3.11+ recommended)

# Check pip version  
pip --version
# Expected: pip 21.0+ (latest recommended)

# Check virtual environment
which python
# Expected: Path to venv python when activated
```

## 🐛 Troubleshooting

### Common Issues

#### Python Not Found
```bash
# Windows: Python not in PATH
# Solution: Reinstall Python with "Add to PATH" checked
# OR manually add to PATH: C:\Users\YourName\AppData\Local\Programs\Python\Python311\

# macOS: python3 vs python
# Solution: Create alias in ~/.zshrc
alias python=python3
alias pip=pip3

# Linux: python3.x-venv not installed
sudo apt install python3.11-venv  # Ubuntu/Debian
sudo dnf install python3.11-venv  # Fedora
```

#### Virtual Environment Issues
```bash
# Windows: Execution policy error
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# macOS/Linux: Permission denied
chmod +x venv/bin/activate

# Alternative activation methods
python -m venv venv --upgrade-deps
python venv/pyvenv.cfg  # Check configuration
```

#### Package Installation Problems
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Clear pip cache
pip cache purge

# Use --no-cache-dir flag
pip install --no-cache-dir -r requirements.txt

# Alternative index (if PyPI is slow)
pip install -i https://pypi.douban.com/simple/ -r requirements.txt
```

#### Streamlit Launch Issues
```bash
# Check port availability
netstat -tulpn | grep :8501

# Use different port
streamlit run app.py --server.port 8502

# Clear Streamlit cache
streamlit cache clear

# Verbose output for debugging
streamlit run app.py --logger.level debug
```

### Platform-Specific Issues

#### Windows
```powershell
# PowerShell execution policy
Get-ExecutionPolicy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Long path support
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force

# Windows Defender exclusion (for performance)
Add-MpPreference -ExclusionPath "C:\Users\YourName\dev"
```

#### macOS
```bash
# Xcode license agreement
sudo xcodebuild -license accept

# macOS Gatekeeper for Python
spctl --master-disable  # Temporarily disable
spctl --master-enable   # Re-enable after setup

# Homebrew PATH issues
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

#### Linux
```bash
# Missing development headers
sudo apt install python3-dev python3.11-dev  # Ubuntu/Debian
sudo dnf install python3-devel               # Fedora

# SSL certificate issues
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# Locale issues
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
```

## ⚙️ Advanced Configuration

### Performance Optimization

#### pip Configuration
```bash
# Create ~/.pip/pip.conf (Linux/macOS) or %APPDATA%\pip\pip.ini (Windows)
[global]
cache-dir = ~/.cache/pip
timeout = 60
retries = 5
trusted-host = pypi.org
               files.pythonhosted.org

[install]
use-pep517 = true
```

#### Virtual Environment Options
```bash
# Use system site packages (not recommended for learning)
python -m venv venv --system-site-packages

# Copy Python binary (instead of symlink)
python -m venv venv --copies

# Upgrade pip and setuptools during creation
python -m venv venv --upgrade-deps
```

### Development Workflow

#### Pre-commit Hooks (Advanced)
```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml (in advanced version)
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

#### Testing Setup
```bash
# Only for advanced version
cd advanced
pip install pytest pytest-cov pytest-asyncio
pytest tests/ -v --cov=src
```

### IDE Configuration

#### VS Code Settings
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "88"],
    "python.linting.enabled": true,
    "python.linting.myPyEnabled": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

#### PyCharm Configuration
1. **Project Settings** → **Python Interpreter** → **Add** → **Existing Environment**
2. Select `venv/bin/python` (or `venv\Scripts\python.exe` on Windows)
3. **Tools** → **Actions on Save** → Enable "Optimize imports" and "Reformat code"

### Environment Variables
```bash
# Create .env file (for advanced version)
cat > .env << EOF
PYTHONPATH=src
ENVIRONMENT=development
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///data/app.db
EOF

# Load environment variables
# Python: pip install python-dotenv
# Then in code: from dotenv import load_dotenv; load_dotenv()
```

## 🎯 Next Steps

After successful setup:

1. **🔰 Start with Basic**: `cd basic && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && streamlit run app.py`

2. **📚 Read Documentation**: Each version has detailed README.md files

3. **🧪 Experiment**: Break things to understand how they work

4. **📈 Progress Gradually**: Don't skip to advanced without understanding fundamentals

5. **🤝 Get Help**: Use GitHub issues for questions and feedback

---

## 📞 Support

### Getting Help
- **Documentation**: Read version-specific README.md files
- **GitHub Issues**: Report problems or ask questions
- **Code Comments**: Every file has extensive educational comments

### Common Learning Path
```
Day 1-2:   🛠️  Environment setup + Basic version
Day 3-7:   🔰  Master Pydantic fundamentals  
Day 8-14:  📊  Database integration patterns
Day 15-30: 🚀  Enterprise architecture study
```

**Happy coding! 🎉**

---

*This guide covers setup for Windows, macOS, and Linux. If you encounter issues specific to your system, please open a GitHub issue with your platform details.*