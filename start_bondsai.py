#!/usr/bin/env python3
"""
Startup script for BondsAI frontend and backend.
This script will start the Flask API server and open the frontend in a browser.
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_requirements():
    """Check if required packages are installed."""
    try:
        import flask
        import flask_cors
        import openai
        import dotenv
        print("✓ All required packages are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing required package: {e}")
        print("Please install requirements with: pip install -r BondsAI/requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists with OpenAI API key."""
    env_path = Path("BondsAI/.env")
    if not env_path.exists():
        print("✗ .env file not found in BondsAI directory")
        print("Please create BondsAI/.env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
        return False
    
    # Check if API key is set
    from dotenv import load_dotenv
    load_dotenv(env_path)
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key or api_key.strip() == '':
        print("✗ OPENAI_API_KEY not set in .env file")
        print("Please add your OpenAI API key to BondsAI/.env:")
        print("OPENAI_API_KEY=your_api_key_here")
        return False
    
    print("✓ OpenAI API key found")
    return True

def start_backend():
    """Start the Flask backend server."""
    print("Starting BondsAI backend server...")
    
    # Change to BondsAI directory and start the server
    backend_process = subprocess.Popen([
        sys.executable, "api_server.py"
    ], cwd="BondsAI")
    
    return backend_process

def open_frontend():
    """Open the frontend in the default browser."""
    frontend_path = Path("frontend/index.html").absolute()
    frontend_url = f"file://{frontend_path}"
    
    print(f"Opening frontend: {frontend_url}")
    webbrowser.open(frontend_url)

def main():
    """Main startup function."""
    print("🚀 Starting BondsAI Application")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        return 1
    
    # Check environment
    if not check_env_file():
        return 1
    
    try:
        # Start backend
        backend_process = start_backend()
        
        # Wait a moment for server to start
        print("Waiting for backend to start...")
        time.sleep(3)
        
        # Open frontend
        open_frontend()
        
        print("\n" + "=" * 50)
        print("🎉 BondsAI is now running!")
        print("Backend API: http://localhost:5000")
        print("Frontend: Opened in your default browser")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 50)
        
        # Wait for user to stop
        try:
            backend_process.wait()
        except KeyboardInterrupt:
            print("\n\nStopping BondsAI...")
            backend_process.terminate()
            backend_process.wait()
            print("✓ BondsAI stopped successfully")
            
    except Exception as e:
        print(f"✗ Error starting BondsAI: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
