#!/usr/bin/env python3
"""
setup_project.py - Setup Script for Your JobHunt-GPT Structure
Creates missing files and ensures everything connects properly
"""

import os
from pathlib import Path

def create_missing_files():
    """Create missing files that your main.py needs"""
    
    project_root = Path.cwd()
    print(f"🚀 Setting up JobHunt-GPT in: {project_root}")
    
    # Ensure required directories exist (matching your structure)
    directories = [
        "output",
        "output/cover_letters", 
        "assets",
        "logs",
        "scraper",
        "matcher",
        "api"
    ]
    
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Directory: {directory}")
    
    # Create __init__.py files for Python modules
    init_files = [
        "scraper/__init__.py",
        "matcher/__init__.py", 
        "api/__init__.py"
    ]
    
    for init_file in init_files:
        init_path = project_root / init_file
        if not init_path.exists():
            init_path.touch()
            print(f"✅ Created: {init_file}")
    
    # Check if CV file exists
    cv_path = project_root / "assets" / "cv.txt"
    if not cv_path.exists():
        print(f"⚠️  CV file not found at {cv_path}")
        print("💡 Please ensure your CV content is in assets/cv.txt")
        
        # Create basic CV template
        cv_content = """Lucas Rizzo - Web3 Engineer & DeFi Bot Developer

PROFESSIONAL SUMMARY
Experienced Web3 Engineer and DeFi Bot Developer with extensive hands-on blockchain development experience. Proven track record in building production-grade liquidation bots, smart contract systems, and automated ERC-20 token ecosystems. Successfully achieved 18% job application response rate.

CORE TECHNICAL SKILLS
• Blockchain Development: Solidity, Smart Contracts, DeFi Protocol Development
• Web3 Technologies: Ethers.js, Web3.js, MetaMask Integration
• Programming Languages: Python, JavaScript, Node.js, TypeScript
• DeFi Specialization: Flash Loans, Liquidation Bots, MEV Protection
• Backend Development: FastAPI, Express.js, RESTful APIs

KEY ACHIEVEMENTS
• Built production-grade liquidation bots with stealth relay systems
• Developed automated ERC-20 token ecosystems
• Achieved 18% job application response rate (vs 2-3% industry average)
• Co-founded and scaled startup to £100k+ revenue
• CompTIA Security+ certified

WORK PREFERENCES
• Remote work preferred (async collaboration)
• Passionate about decentralized technologies and financial innovation"""

        with open(cv_path, "w", encoding="utf-8") as f:
            f.write(cv_content)
        print("✅ Created CV template - please customize with your details")
    
    # Create .env template if missing
    env_path = project_root / ".env"
    if not env_path.exists():
        env_content = """# JobHunt-GPT Environment Variables
COHERE_API_KEY=your_cohere_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Email Configuration (Optional)
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# Debug Mode
DEBUG_LOGGING=false
"""
        with open(env_path, "w") as f:
            f.write(env_content)
        print("✅ Created .env template")

def create_requirements():
    """Create requirements.txt for dependencies"""
    
    requirements = """# Core Dependencies
pandas>=1.5.0
python-dotenv>=0.19.0
requests>=2.28.0
beautifulsoup4>=4.11.0
lxml>=4.9.0

# AI/ML Dependencies  
cohere>=4.0.0
scikit-learn>=1.1.0

# Web Framework Dependencies
fastapi>=0.95.0
uvicorn>=0.20.0
pydantic>=2.0.0

# Optional Dependencies
selenium>=4.8.0
"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements.strip())
    
    print("✅ Created requirements.txt")

def test_imports():
    """Test that all required modules can be imported"""
    print("\n🧪 Testing imports...")
    
    # Test config import
    try:
        from config import config
        print("✅ Config imported successfully")
        config.create_directories()
        print("✅ Config directories created")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    # Test scraper import
    try:
        import scraper.scrape_and_match as scraper
        print("✅ Scraper module imported")
        
        # Test scraper functionality
        if hasattr(scraper, 'main'):
            print("✅ Scraper main function found")
        else:
            print("❌ Scraper main function missing")
            
    except Exception as e:
        print(f"❌ Scraper import failed: {e}")
        return False
    
    # Test matcher import
    try:
        from matcher.match_job import match_score
        print("✅ Matcher module imported")
        
        # Test with sample data
        test_score = match_score("python developer", "python programming job")
        print(f"✅ Matcher working (test score: {test_score:.3f})")
        
    except Exception as e:
        print(f"❌ Matcher import failed: {e}")
        return False
    
    return True

def test_main_bot():
    """Test your existing main.py bot"""
    print("\n🤖 Testing main bot...")
    
    try:
        import main
        print("✅ Main module imported")
        
        if hasattr(main, 'Web3JobBot'):
            bot = main.Web3JobBot()
            print("✅ Web3JobBot initialized")
            
            # Test CV loading
            cv_text = bot.load_cv_text()
            if cv_text and len(cv_text) > 100:
                print(f"✅ CV loaded ({len(cv_text)} characters)")
            else:
                print("⚠️  CV content seems short - check assets/cv.txt")
            
            return True
        else:
            print("❌ Web3JobBot class not found")
            return False
            
    except Exception as e:
        print(f"❌ Main bot test failed: {e}")
        return False

def test_api():
    """Test API module"""
    print("\n🌐 Testing API...")
    
    try:
        from api.main import app
        print("✅ FastAPI app imported")
        
        # Test basic functionality
        if hasattr(app, 'routes'):
            route_count = len(app.routes)
            print(f"✅ API has {route_count} routes configured")
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Main setup function"""
    
    print("🚀 JobHunt-GPT Project Setup")
    print("=" * 50)
    
    # Create missing files
    create_missing_files()
    create_requirements()
    
    print("\n" + "=" * 50)
    print("🧪 TESTING SETUP")
    print("=" * 50)
    
    # Run tests
    tests_passed = 0
    total_tests = 4
    
    if test_imports():
        tests_passed += 1
    
    if test_main_bot():
        tests_passed += 1
    
    if test_api():
        tests_passed += 1
    
    # Test project structure
    required_files = ["config.py", "main.py", "api/main.py", "assets/cv.txt"]
    structure_ok = all(Path(f).exists() for f in required_files)
    
    if structure_ok:
        tests_passed += 1
        print("✅ Project structure complete")
    else:
        print("❌ Missing required files")
    
    print("\n" + "=" * 50)
    print("📊 SETUP RESULTS") 
    print("=" * 50)
    print(f"✅ Tests Passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("\n🎉 SETUP COMPLETE!")
        print("🚀 Your JobHunt-GPT is ready!")
        
        print("\n📋 NEXT STEPS:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Configure .env with your COHERE_API_KEY")
        print("3. Customize assets/cv.txt with your CV")
        print("4. Test scraping: python -c \"import scraper.scrape_and_match as s; s.main()\"")
        print("5. Run full bot: python main.py --template-only")
        print("6. Start API: python api/main.py")
        
        print("\n🎯 READY TO ACHIEVE 18% RESPONSE RATES!")
        
    else:
        print(f"\n⚠️  {total_tests - tests_passed} issues need fixing")
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Ensure all artifact files are saved correctly")
        print("2. Check that your main.py is in the root directory")
        print("3. Verify Python path and imports")
        print("4. Run: python setup_project.py again")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
