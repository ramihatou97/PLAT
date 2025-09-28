#!/usr/bin/env python3
"""
PLAT Setup Script
Easy installation and configuration helper
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header():
    """Print setup header."""
    print("🧠 PLAT - Neurosurgical Encyclopedia Setup")
    print("=" * 50)
    print()

def check_python_version():
    """Check Python version requirement."""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} - OK")
    return True

def check_prerequisites():
    """Check system prerequisites."""
    print("🔍 Checking prerequisites...")
    
    if not check_python_version():
        return False
    
    # Check pip
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print("✅ pip - OK")
    except subprocess.CalledProcessError:
        print("❌ pip not found")
        return False
    
    return True

def install_dependencies():
    """Install Python dependencies."""
    print("\n📦 Installing dependencies...")
    
    try:
        # Install requirements
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file from template."""
    print("\n⚙️  Setting up configuration...")
    
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            shutil.copy(".env.example", ".env")
            print("✅ Created .env file from template")
            print("📝 Please edit .env with your API keys")
        else:
            print("❌ .env.example not found")
            return False
    else:
        print("✅ .env file already exists")
    
    return True

def create_directories():
    """Create necessary directories."""
    print("\n📁 Creating directories...")
    
    directories = ["data", "logs", "data/chromadb"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created {directory}/")
    
    return True

def run_demo():
    """Run the demonstration."""
    print("\n🚀 Running demo...")
    
    try:
        result = subprocess.run([sys.executable, "demo.py"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Demo failed: {e}")
        return False

def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API keys:")
    print("   - OpenAI API key for GPT-4")
    print("   - Google API key for Gemini")
    print("   - Anthropic API key for Claude")
    print("   - PubMed email for research access")
    print()
    print("2. Initialize the database:")
    print("   python scripts/initialize_data.py")
    print()
    print("3. Start the server:")
    print("   python main.py")
    print()
    print("4. Access the system:")
    print("   Web UI: http://localhost:8000/frontend/templates/index.html")
    print("   API Docs: http://localhost:8000/docs")
    print("   Health Check: http://localhost:8000/health")
    print()
    print("📚 For more information, see README.md")
    print("=" * 50)

def main():
    """Main setup function."""
    print_header()
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed")
        sys.exit(1)
    
    # Install dependencies (optional - user might want to use virtual env)
    install_deps = input("\n📦 Install Python dependencies? (y/N): ").lower().strip()
    if install_deps in ['y', 'yes']:
        if not install_dependencies():
            print("\n❌ Dependency installation failed")
            sys.exit(1)
    else:
        print("⏭️  Skipping dependency installation")
        print("   Run manually: pip install -r requirements.txt")
    
    # Create configuration
    if not create_env_file():
        print("\n❌ Configuration setup failed")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("\n❌ Directory creation failed")
        sys.exit(1)
    
    # Run demo
    run_demo_choice = input("\n🚀 Run demonstration? (Y/n): ").lower().strip()
    if run_demo_choice not in ['n', 'no']:
        run_demo()
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()