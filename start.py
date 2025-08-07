#!/usr/bin/env python3
"""
🚀 iFixit Repair Guide API - Quick Start Script
Helps you get the API running quickly and easily.
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}")

def print_step(step_num, title, description=""):
    """Print a formatted step."""
    print(f"\n{step_num}. {title}")
    if description:
        print(f"   {description}")

def check_python_version():
    """Check if Python version is compatible."""
    print_step(1, "Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("   ❌ Python 3.8+ is required!")
        print(f"   📊 Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} is compatible!")
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    print_step(2, "Checking dependencies...")
    
    try:
        import fastapi
        import uvicorn
        import requests
        import pydantic
        print("   ✅ All dependencies are installed!")
        return True
    except ImportError as e:
        print(f"   ❌ Missing dependency: {e}")
        print("   💡 Installing dependencies...")
        return install_dependencies()

def install_dependencies():
    """Install required dependencies."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("   ✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("   ❌ Failed to install dependencies!")
        print("   💡 Try running: pip install -r requirements.txt")
        return False

def setup_environment():
    """Set up environment variables."""
    print_step(3, "Setting up environment...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("   📝 Creating .env file from template...")
            with open(env_example, 'r') as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            print("   ✅ .env file created!")
        else:
            print("   ⚠️  No .env.example found, creating basic .env...")
            with open(env_file, 'w') as f:
                f.write("# iFixit Repair Guide API Environment\n")
                f.write("PORT=8000\n")
                f.write("HOST=127.0.0.1\n")
                f.write("ALLOWED_ORIGINS=*\n")
            print("   ✅ Basic .env file created!")
    else:
        print("   ✅ .env file already exists!")
    
    return True

def start_server():
    """Start the API server."""
    print_step(4, "Starting the API server...")
    
    try:
        print("   🚀 Starting server...")
        print("   📍 Server will be available at: http://localhost:8000")
        print("   📚 API Documentation: http://localhost:8000/docs")
        print("   💚 Health Check: http://localhost:8000/health")
        print("\n   ⏹️  Press Ctrl+C to stop the server")
        print("   " + "="*50)
        
        # Start the server
        subprocess.run([sys.executable, "app.py"])
        
    except KeyboardInterrupt:
        print("\n\n   👋 Server stopped by user")
    except Exception as e:
        print(f"   ❌ Failed to start server: {e}")
        return False
    
    return True

def test_server():
    """Test if the server is running correctly."""
    print_step(5, "Testing server...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Server is running correctly!")
            return True
        else:
            print(f"   ❌ Server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to server")
        return False
    except Exception as e:
        print(f"   ❌ Error testing server: {e}")
        return False

def main():
    """Main startup function."""
    print_header("iFixit Repair Guide API - Quick Start")
    print("This script will help you get the API running quickly!")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Start server
    print_header("Starting API Server")
    start_server()

if __name__ == "__main__":
    main() 