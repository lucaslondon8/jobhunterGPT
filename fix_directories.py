#!/usr/bin/env python3
"""
fix_directories.py - Fix directory structure issues
"""

import os
import shutil
from pathlib import Path

def fix_cover_letters_directory():
    """Fix the cover_letters directory issue"""
    
    project_root = Path.cwd()
    cover_letters_path = project_root / "output" / "cover_letters"
    
    print("🔧 Fixing directory structure...")
    
    try:
        if cover_letters_path.exists():
            if cover_letters_path.is_file():
                print(f"❌ {cover_letters_path} is a file, removing...")
                cover_letters_path.unlink()
                cover_letters_path.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created directory: {cover_letters_path}")
            elif cover_letters_path.is_dir():
                print(f"✅ {cover_letters_path} is already a directory")
            else:
                print(f"⚠️  {cover_letters_path} exists but is neither file nor directory")
                # Try to remove and recreate
                shutil.rmtree(cover_letters_path, ignore_errors=True)
                cover_letters_path.mkdir(parents=True, exist_ok=True)
                print(f"✅ Recreated directory: {cover_letters_path}")
        else:
            cover_letters_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {cover_letters_path}")
            
    except Exception as e:
        print(f"❌ Error fixing cover_letters directory: {e}")
        return False
    
    return True

def check_cv_file():
    """Check and fix CV file"""
    
    project_root = Path.cwd()
    assets_dir = project_root / "assets"
    cv_path = assets_dir / "cv.txt"
    
    print("📄 Checking CV file...")
    
    # Ensure assets directory exists
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    if cv_path.exists():
        try:
            with open(cv_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if len(content) > 50:
                    print(f"✅ CV file exists with {len(content)} characters")
                    return True
                else:
                    print(f"⚠️  CV file exists but is too short ({len(content)} chars)")
        except Exception as e:
            print(f"❌ Error reading CV file: {e}")
    
    # Create default CV
    print("📝 Creating default CV content...")
    
    default_cv = """Lucas Rizzo - Web3 Engineer & DeFi Bot Developer

PROFESSIONAL SUMMARY
Experienced Web3 Engineer and DeFi Bot Developer with 300+ hours of hands-on blockchain development experience. Proven track record in building production-grade liquidation bots, smart contract systems, and automated ERC-20 token ecosystems. Successfully achieved 18% job application response rate through strategic technical positioning and personalized outreach.

CORE TECHNICAL SKILLS
• Blockchain Development: Solidity, Smart Contracts, DeFi Protocol Development
• Web3 Technologies: Ethers.js, Web3.js, MetaMask Integration, IPFS
• Programming Languages: Python, JavaScript, Node.js, TypeScript
• DeFi Specialization: Flash Loans, Liquidation Bots, MEV Protection, Yield Farming
• Backend Development: FastAPI, Express.js, RESTful APIs, Database Design
• Frontend Development: React, HTML5, CSS3, Responsive Design

KEY ACHIEVEMENTS
• Built production-grade liquidation bots with stealth relay systems
• Developed automated ERC-20 token ecosystems with real-time monitoring
• Implemented MEV protection mechanisms for DeFi protocols
• Created flash loan arbitrage systems with risk management
• Achieved 18% job application response rate (vs 2-3% industry average)
• Co-founded and scaled food startup to £100k+ revenue in 6 months
• CompTIA Security+ certified

TECHNICAL PROJECTS
• DeFi Liquidation Bot System: Production-grade monitoring for major protocols
• Automated ERC-20 Token Ecosystem: Smart contract suite with governance
• Flash Loan Arbitrage System: Multi-protocol detection and execution
• MEV Protection Tools: Stealth relay mechanisms for transaction privacy

WORK PREFERENCES
• Remote work preferred (async collaboration)
• Open to contract, part-time, or full-time opportunities
• Passionate about decentralized technologies and financial innovation
• Available for immediate start on exciting Web3 and DeFi projects"""

    try:
        with open(cv_path, 'w', encoding='utf-8') as f:
            f.write(default_cv)
        print(f"✅ Created CV file at {cv_path} ({len(default_cv)} characters)")
        return True
    except Exception as e:
        print(f"❌ Error creating CV file: {e}")
        return False

def main():
    """Fix all directory and file issues"""
    
    print("🔧 JobHunt-GPT Directory Fix")
    print("=" * 40)
    
    # Fix cover letters directory
    dir_fixed = fix_cover_letters_directory()
    
    # Check/create CV file
    cv_fixed = check_cv_file()
    
    print("\n" + "=" * 40)
    print("📊 RESULTS")
    print("=" * 40)
    
    if dir_fixed and cv_fixed:
        print("✅ All issues fixed!")
        print("\n🚀 Try running your bot now:")
        print("   python main.py --template-only")
    else:
        print("❌ Some issues remain")
        print("💡 Check the errors above and try manual fixes")

if __name__ == "__main__":
    main()
