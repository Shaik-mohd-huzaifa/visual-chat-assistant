"""
Setup script for Visual Understanding Chat Assistant
"""

import os
import sys
import subprocess
import shutil

def setup_environment():
    """Set up the development environment"""
    
    print("🚀 Setting up Visual Understanding Chat Assistant...")
    print("-" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists("venv"):
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"])
        print("✅ Virtual environment created")
    else:
        print("✅ Virtual environment already exists")
    
    # Determine pip path
    pip_path = "venv\\Scripts\\pip" if os.name == 'nt' else "venv/bin/pip"
    
    # Install dependencies
    print("📚 Installing dependencies...")
    subprocess.run([pip_path, "install", "-r", "requirements.txt"])
    print("✅ Dependencies installed")
    
    # Create .env file if it doesn't exist
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            shutil.copy(".env.example", ".env")
            print("⚠️  Created .env file from .env.example")
            print("⚠️  Please edit .env and add your OpenAI API key")
        else:
            print("❌ .env.example not found")
    else:
        print("✅ .env file exists")
    
    # Create necessary directories
    directories = ["temp", "static", "src"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created {directory}/ directory")
    
    print("-" * 50)
    print("✨ Setup complete!")
    print("\nNext steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Activate virtual environment:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("3. Run the application:")
    print("   python main.py")
    print("\n4. Open http://localhost:8000 in your browser")

if __name__ == "__main__":
    setup_environment()
