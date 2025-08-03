#!/usr/bin/env python3
"""
Launcher for AI Research Analysis System Interfaces
Choose between Streamlit and Web interface.
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import streamlit
        import fastapi
        import uvicorn
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install required packages:")
        print("pip install streamlit fastapi uvicorn")
        return False

def check_api_keys():
    """Check if API keys are configured."""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("Please create a .env file with your API keys:")
        print("OPENAI_API_KEY=your_openai_api_key_here")
        print("NEWS_API_KEY=your_news_api_key_here (optional)")
        return False
    
    with open(env_file, 'r') as f:
        content = f.read()
        if 'your_openai_api_key_here' in content:
            print("⚠️  Please configure your API keys in the .env file")
            return False
    
    return True

def launch_streamlit():
    """Launch the Streamlit interface."""
    print("🚀 Launching Streamlit interface...")
    print("📱 Opening browser automatically...")
    
    # Start Streamlit
    try:
        subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.headless", "true"
        ])
        
        # Wait a moment for the server to start
        time.sleep(3)
        
        # Open browser
        webbrowser.open("http://localhost:8501")
        
        print("✅ Streamlit interface launched successfully!")
        print("🌐 URL: http://localhost:8501")
        print("🛑 Press Ctrl+C to stop the server")
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping Streamlit server...")
            
    except Exception as e:
        print(f"❌ Failed to launch Streamlit: {e}")

def launch_web_interface():
    """Launch the Web interface."""
    print("🚀 Launching Web interface...")
    print("📱 Opening browser automatically...")
    
    # Start FastAPI server
    try:
        subprocess.Popen([
            sys.executable, "web_interface_enhanced.py"
        ])
        
        # Wait a moment for the server to start
        time.sleep(3)
        
        # Open browser
        webbrowser.open("http://localhost:8000")
        
        print("✅ Web interface launched successfully!")
        print("🌐 URL: http://localhost:8000")
        print("🛑 Press Ctrl+C to stop the server")
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping Web server...")
            
    except Exception as e:
        print(f"❌ Failed to launch Web interface: {e}")

def main():
    """Main launcher function."""
    print("🔬 AI Research Analysis System - Interface Launcher")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check API keys
    if not check_api_keys():
        return
    
    print("\n📋 Available Interfaces:")
    print("1. 🎨 Streamlit Interface (Recommended)")
    print("   - Modern, interactive interface")
    print("   - Built-in progress tracking")
    print("   - Real-time updates")
    print("   - Professional appearance")
    
    print("\n2. 🌐 Web Interface")
    print("   - Traditional web application")
    print("   - Custom HTML/CSS design")
    print("   - Lightweight and fast")
    print("   - Works in any browser")
    
    print("\n3. 🧪 Test System")
    print("   - Run a quick test")
    print("   - Verify system functionality")
    
    print("\n4. ❌ Exit")
    
    while True:
        try:
            choice = input("\n🎯 Choose an option (1-4): ").strip()
            
            if choice == "1":
                launch_streamlit()
                break
            elif choice == "2":
                launch_web_interface()
                break
            elif choice == "3":
                print("🧪 Running system test...")
                subprocess.run([sys.executable, "test_system.py"])
                break
            elif choice == "4":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 