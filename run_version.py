#!/usr/bin/env python3
"""
Quick launcher script for different Pydantic learning versions.

This script helps you easily run and switch between the Basic, Intermediate, 
and Advanced versions of the Employee Management System.

Usage:
    python run_version.py basic
    python run_version.py intermediate  
    python run_version.py advanced
    python run_version.py --help
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path


def run_streamlit_app(version: str):
    """Run the Streamlit app for the specified version."""
    
    version_configs = {
        'basic': {
            'dir': 'basic',
            'file': 'app.py',
            'description': '🔰 BASIC - Pydantic Fundamentals'
        },
        'intermediate': {
            'dir': 'intermediate', 
            'file': 'app.py',
            'description': '📊 INTERMEDIATE - Database Integration'
        },
        'advanced': {
            'dir': 'advanced',
            'file': 'main.py', 
            'description': '🚀 ADVANCED - Enterprise Patterns'
        }
    }
    
    if version not in version_configs:
        print(f"❌ Invalid version: {version}")
        print(f"Available versions: {', '.join(version_configs.keys())}")
        return False
    
    config = version_configs[version]
    app_dir = Path(config['dir'])
    app_file = app_dir / config['file']
    
    # Check if directory and file exist
    if not app_dir.exists():
        print(f"❌ Directory '{app_dir}' not found!")
        print("Make sure you're running this from the repository root directory.")
        return False
    
    if not app_file.exists():
        print(f"❌ App file '{app_file}' not found!")
        return False
    
    print(f"🚀 Starting {config['description']}")
    print(f"📁 Directory: {app_dir}")
    print(f"📄 File: {app_file}")
    print("-" * 50)
    
    # Change to app directory and run streamlit
    try:
        os.chdir(app_dir)
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', config['file']], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 Streamlit app stopped by user")
        return True
    
    return True


def show_version_info():
    """Show information about all available versions."""
    
    print("🐍 Python Basics with Pydantic - Learning Versions")
    print("=" * 55)
    
    versions_info = [
        {
            'name': '🔰 BASIC',
            'command': 'basic',
            'description': 'Pydantic Fundamentals',
            'features': [
                '✅ Data validation basics',
                '✅ Type hints & constraints', 
                '✅ Custom validators',
                '✅ JSON serialization',
                '✅ Error handling',
                '✅ Simple Streamlit UI'
            ],
            'stats': '📝 ~620 lines | 📦 3 dependencies | ⏱️ 30-60min'
        },
        {
            'name': '📊 INTERMEDIATE', 
            'command': 'intermediate',
            'description': 'Database Integration',
            'features': [
                '✅ SQLAlchemy integration',
                '✅ Model inheritance',
                '✅ Database sessions',
                '✅ CRUD operations',
                '✅ Data relationships',
                '✅ Basic analytics'
            ],
            'stats': '📝 ~1,200 lines | 📦 6 dependencies | ⏱️ 1-2hrs'
        },
        {
            'name': '🚀 ADVANCED',
            'command': 'advanced', 
            'description': 'Enterprise Patterns',
            'features': [
                '✅ Service layer architecture',
                '✅ Repository pattern',
                '✅ Dependency injection',
                '✅ Enterprise error handling',
                '✅ Production optimization',
                '✅ Testing strategies'
            ],
            'stats': '📝 ~3,000 lines | 📦 20+ dependencies | ⏱️ 4-8hrs'
        }
    ]
    
    for version in versions_info:
        print(f"\n{version['name']} - {version['description']}")
        print("-" * 30)
        for feature in version['features']:
            print(f"  {feature}")
        print(f"\n  {version['stats']}")
        print(f"  🚀 Run: python run_version.py {version['command']}")
        print()


def check_dependencies(version: str):
    """Check if dependencies are installed for the specified version."""
    
    requirements_file = Path(version) / 'requirements.txt'
    
    if not requirements_file.exists():
        print(f"⚠️  No requirements.txt found for {version}")
        return True
    
    print(f"🔍 Checking dependencies for {version}...")
    
    try:
        # Try to import key packages based on version
        if version == 'basic':
            import streamlit
            import pydantic
            print("✅ Basic dependencies available")
            
        elif version == 'intermediate':
            import streamlit
            import pydantic
            import sqlalchemy
            import pandas
            import plotly
            print("✅ Intermediate dependencies available")
            
        elif version == 'advanced':
            import streamlit
            import pydantic
            import sqlalchemy
            import pandas
            import plotly
            print("✅ Advanced dependencies available")
            
        return True
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print(f"💡 Install with: pip install -r {requirements_file}")
        return False


def main():
    """Main function to handle command line arguments."""
    
    parser = argparse.ArgumentParser(
        description="Run different versions of the Pydantic learning application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_version.py basic        # Run basic version
  python run_version.py intermediate # Run intermediate version  
  python run_version.py advanced     # Run advanced version
  python run_version.py --info       # Show version information
        """
    )
    
    parser.add_argument(
        'version',
        nargs='?',
        choices=['basic', 'intermediate', 'advanced'],
        help='Version to run (basic, intermediate, advanced)'
    )
    
    parser.add_argument(
        '--info', '-i',
        action='store_true',
        help='Show information about all versions'
    )
    
    parser.add_argument(
        '--check', '-c',
        metavar='VERSION',
        help='Check dependencies for specified version'
    )
    
    args = parser.parse_args()
    
    # Show version info
    if args.info:
        show_version_info()
        return
    
    # Check dependencies
    if args.check:
        success = check_dependencies(args.check)
        sys.exit(0 if success else 1)
    
    # Run version
    if args.version:
        # Check dependencies first
        if not check_dependencies(args.version):
            print(f"\n💡 To install dependencies for {args.version}:")
            print(f"   cd {args.version}")
            print(f"   pip install -r requirements.txt")
            sys.exit(1)
        
        success = run_streamlit_app(args.version)
        sys.exit(0 if success else 1)
    
    # No arguments provided
    print("🐍 Python Basics with Pydantic - Learning Versions\n")
    print("Usage:")
    print("  python run_version.py basic        # 🔰 Start with fundamentals")
    print("  python run_version.py intermediate # 📊 Database integration")
    print("  python run_version.py advanced     # 🚀 Enterprise patterns") 
    print("  python run_version.py --info       # ℹ️  Show detailed info")
    print("\n💡 New to Pydantic? Start with: python run_version.py basic")


if __name__ == "__main__":
    main()