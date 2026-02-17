#!/usr/bin/env python3
"""
KTP - Knowledge Transfer Platform
Main Application for Render Deployment
Combines Flask Backend and Streamlit Frontend
"""

import os
import threading
import time
import subprocess
import sys
from pathlib import Path

def start_flask_backend():
    """Start Flask backend in a separate thread"""
    print("📡 Starting Flask backend...")
    subprocess.run([
        sys.executable, "-m", "gunicorn", "app:app",
        "--bind", "0.0.0.0:5000",
        "--workers", "1",
        "--timeout", "120"
    ], cwd="server")

def start_streamlit_frontend():
    """Start Streamlit frontend"""
    print("🎨 Starting Streamlit frontend...")
    port = os.environ.get('PORT', 8501)
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
        "--server.port", str(port),
        "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ], cwd="frontend")

def main():
    print("🧠 KTP - Knowledge Transfer Platform")
    print("🚀 Starting on Render...")
    
    # Check if we're in the right directory
    if not Path("server").exists() or not Path("frontend").exists():
        print("❌ Error: Please run this from the project root directory")
        sys.exit(1)
    
    # Start Flask backend in a separate thread
    flask_thread = threading.Thread(target=start_flask_backend, daemon=True)
    flask_thread.start()
    
    # Wait a moment for Flask to start
    time.sleep(5)
    
    # Start Streamlit frontend (this will be the main process)
    start_streamlit_frontend()

if __name__ == "__main__":
    main() 