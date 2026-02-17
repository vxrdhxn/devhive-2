#!/usr/bin/env python3
"""
KTP - Knowledge Transfer Platform
Startup Script for Local Development
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def main():
    print("🧠 KTP - Knowledge Transfer Platform")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("server").exists():
        print("❌ Error: Please run this script from the project root directory")
        print("   Make sure you have a 'server' folder with the Flask app")
        sys.exit(1)
    
    print("🚀 Starting KTP...")
    print()
    
    # Start Flask backend
    print("📡 Starting Flask backend...")
    flask_process = subprocess.Popen([
        sys.executable, "app.py"
    ], cwd="server")
    
    # Wait a moment for Flask to start
    time.sleep(3)
    
    # Start Streamlit frontend
    print("🎨 Starting Streamlit frontend...")
    streamlit_process = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
        "--server.port", "8501",
        "--server.address", "localhost"
    ], cwd="frontend")
    
    print()
    print("✅ KTP is starting up!")
    print()
    print("🌐 Access your application:")
    print("   📡 Backend API: http://localhost:5000")
    print("   🎨 Frontend UI: http://localhost:8501")
    print()
    print("📋 Available endpoints:")
    print("   • GET  /health - Server health check")
    print("   • POST /ingest - Upload text content")
    print("   • POST /ingest/file - Upload file")
    print("   • POST /search - Search knowledge base")
    print("   • POST /ask - Ask questions")
    print("   • POST /integrate/github - GitHub integration")
    print("   • POST /integrate/notion - Notion integration")
    print("   • POST /integrate/slack - Slack integration")
    print("   • POST /integrate/all - One-click integration")
    print("   • GET  /stats - Get statistics")
    print("   • POST /tokens/store - Store API tokens")
    print("   • GET  /tokens/list - List stored tokens")
    print()
    print("🛑 Press Ctrl+C to stop both servers")
    
    try:
        # Keep the script running
        flask_process.wait()
        streamlit_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down KTP...")
        flask_process.terminate()
        streamlit_process.terminate()
        print("✅ KTP stopped")

if __name__ == "__main__":
    main() 