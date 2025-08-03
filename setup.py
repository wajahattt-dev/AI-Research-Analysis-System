"""
Setup script for the AI Research Analysis Project.
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    
    try:
        # Install from requirements.txt
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file from template."""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_example.exists():
        print("❌ env.example file not found")
        return False
    
    try:
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file with your API keys")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def create_directories():
    """Create necessary directories."""
    directories = ["reports", "data", "logs"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Created necessary directories")

def validate_setup():
    """Validate the setup."""
    print("🔍 Validating setup...")
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("❌ .env file not found. Please run setup again.")
        return False
    
    # Check if directories exist
    for directory in ["reports", "data"]:
        if not Path(directory).exists():
            print(f"❌ {directory} directory not found")
            return False
    
    # Try to import main modules
    try:
        from main import ResearchAnalyst
        print("✅ Main modules can be imported")
    except ImportError as e:
        print(f"❌ Failed to import main modules: {e}")
        return False
    
    print("✅ Setup validation passed!")
    return True

def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "=" * 60)
    print("🎉 Setup completed successfully!")
    print("=" * 60)
    print("\n📋 Next steps:")
    print("1. Edit the .env file with your API keys:")
    print("   - OPENAI_API_KEY (required)")
    print("   - NEWS_API_KEY (optional)")
    print("   - ARXIV_EMAIL (optional)")
    print("\n2. Test the system:")
    print("   python example_usage.py")
    print("\n3. Run the web interface:")
    print("   python web_interface.py")
    print("\n4. Or use the system programmatically:")
    print("   from main import ResearchAnalyst")
    print("   analyst = ResearchAnalyst()")
    print("   results = await analyst.conduct_research('your query')")
    print("\n📚 For more information, see the README.md file")

def main():
    """Main setup function."""
    print("🚀 AI Research Analysis System - Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed during dependency installation")
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        print("❌ Setup failed during .env file creation")
        sys.exit(1)
    
    # Validate setup
    if not validate_setup():
        print("❌ Setup validation failed")
        sys.exit(1)
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main() 