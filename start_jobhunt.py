#!/usr/bin/env python3
"""
start_jobhunt.py - Easy startup script for JobHunt-GPT
Starts both backend API and frontend together
"""

import os
import sys
import subprocess
import time
import threading
import webbrowser
from pathlib import Path

def check_requirements():
    """Check if all requirements are met"""
    
    print("🔍 Checking requirements...")
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ main.py not found. Please run from the jobsearchBotV1 directory")
        return False
    
    if not Path("api/main.py").exists():
        print("❌ api/main.py not found. Please save the API backend file")
        return False
    
    if not Path("output/jobs.csv").exists():
        print("⚠️  No jobs.csv found. Run job discovery first:")
        print("   python main.py --template-only")
        return False
    
    # Check if dependencies are installed
    try:
        import fastapi
        import uvicorn
        import pandas
        print("✅ Python dependencies installed")
    except ImportError as e:
        print(f"❌ Missing Python dependencies: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False
    
    print("✅ All requirements met")
    return True

def start_backend():
    """Start the FastAPI backend"""
    
    print("🚀 Starting JobHunt-GPT API backend...")
    
    try:
        # Change to api directory and start uvicorn
        os.chdir("api")
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Backend stopped by user")
    except Exception as e:
        print(f"❌ Backend failed: {e}")

def check_backend_health():
    """Check if backend is running"""
    
    import requests
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_frontend_dev_server():
    """Instructions for starting frontend"""
    
    print("\n🌐 FRONTEND SETUP INSTRUCTIONS:")
    print("=" * 50)
    print("1. Open a new terminal")
    print("2. Navigate to your frontend directory:")
    print("   cd frontend")
    print("3. Install dependencies (if not done):")
    print("   npm install")
    print("4. Start the development server:")
    print("   npm run dev")
    print("   # or")
    print("   npm start")
    print("5. Open http://localhost:3000 in your browser")
    print("\n💡 Your React app will connect to the API at http://localhost:8000")

def quick_start():
    """Quick start process"""
    
    print("🎯 JobHunt-GPT Quick Start")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements not met. Please fix the issues above.")
        return False
    
    print("\n📋 STARTUP OPTIONS:")
    print("1. Start backend only (API server)")
    print("2. Run job discovery first")
    print("3. Show frontend setup instructions")
    print("4. Full setup guide")
    
    try:
        choice = input("\nChoose option (1-4): ").strip()
        
        if choice == "1":
            print("\n🚀 Starting backend API server...")
            print("📍 API will be available at: http://localhost:8000")
            print("📚 API docs at: http://localhost:8000/docs")
            print("🛑 Press Ctrl+C to stop")
            start_backend()
            
        elif choice == "2":
            print("\n🔍 Running job discovery...")
            result = subprocess.run([sys.executable, "main.py", "--template-only"])
            if result.returncode == 0:
                print("\n✅ Job discovery complete!")
                print("💡 Now start the backend: python start_jobhunt.py")
            else:
                print("\n❌ Job discovery failed")
            
        elif choice == "3":
            start_frontend_dev_server()
            
        elif choice == "4":
            show_full_guide()
            
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n👋 Startup cancelled")
    except Exception as e:
        print(f"❌ Error: {e}")

def show_full_guide():
    """Show complete setup guide"""
    
    print("\n📚 COMPLETE JOBHUNT-GPT SETUP GUIDE")
    print("=" * 50)
    
    print("\n🔧 BACKEND SETUP:")
    print("1. Ensure all Python dependencies installed:")
    print("   pip install -r requirements.txt")
    print()
    print("2. Run job discovery to get real data:")
    print("   python main.py --template-only")
    print()
    print("3. Start the API backend:")
    print("   python start_jobhunt.py")
    print("   (Choose option 1)")
    
    print("\n🌐 FRONTEND SETUP:")
    print("1. Navigate to your frontend directory")
    print("2. Install React dependencies:")
    print("   npm install")
    print()
    print("3. Replace your App.jsx with the updated version")
    print("   (Copy from the artifact provided)")
    print()
    print("4. Start the React development server:")
    print("   npm run dev  # or npm start")
    print()
    print("5. Open http://localhost:3000")
    
    print("\n🎯 VERIFICATION:")
    print("✅ Backend health: http://localhost:8000/api/health")
    print("✅ API docs: http://localhost:8000/docs")
    print("✅ Frontend: http://localhost:3000")
    print("✅ Real job data flowing from backend to frontend")
    
    print("\n🚀 SUCCESS INDICATORS:")
    print("• Green 'Live' indicator in dashboard header")
    print("• Real job data (not mock data)")
    print("• Functional 'Scan Now' button")
    print("• Apply buttons that work")
    print("• Pipeline status updates")

def main():
    """Main function"""
    
    # Go back to project root if we're in api directory
    if Path.cwd().name == "api":
        os.chdir("..")
    
    quick_start()

if __name__ == "__main__":
    main()
