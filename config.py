#!/usr/bin/env python3
"""
config.py - Core Configuration for JobHuntGPT
Updated to match your project structure: jobhunt-gpt/
"""

import os
from pathlib import Path

class Config:
    """Global configuration for JobHuntGPT"""
    
    def __init__(self):
        # Project root directory (jobhunt-gpt/)
        self.project_root = Path(__file__).parent.absolute()
        
        # Output directories (matching your structure)
        self.output_dir = self.project_root / "output"
        self.assets_dir = self.project_root / "assets"
        self.logs_dir = self.project_root / "logs"
        self.cover_letters_dir = self.output_dir / "cover_letters"
        
        # File paths (matching your existing files)
        self.output_csv = self.output_dir / "jobs.csv"
        self.cv_text_path = self.assets_dir / "cv.txt"  # Your existing file
        self.log_file = self.logs_dir / "job_bot.log"
        
        # API configuration (for your api/main.py)
        self.api_host = "localhost"
        self.api_port = 8000
        self.api_base_url = f"http://{self.api_host}:{self.api_port}"
        
        # Scraper configuration
        self.scraper_config = {
            'max_pages': 5,
            'delay_between_requests': 2,
            'timeout': 30,
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }
        
        # Matcher configuration
        self.matcher_config = {
            'min_score_threshold': 0.1,
            'web3_keyword_weight': 2.0,
            'tech_keyword_weight': 1.0,
            'use_tfidf': True
        }
        
        # Email configuration
        self.email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'use_tls': True,
            'batch_size': 10,
            'delay_between_emails': 30
        }
        
        # API limits (for your existing rate limiting)
        self.api_limits = {
            'cohere_calls_per_minute': 10,
            'max_daily_applications': 50,
            'rate_limit_buffer': 5
        }
    
    def create_directories(self):
        """Create all necessary project directories"""
        directories = [
            self.output_dir,
            self.assets_dir, 
            self.logs_dir,
            self.cover_letters_dir,
            self.project_root / "scraper",
            self.project_root / "matcher",
            self.project_root / "api"  # Your API directory
        ]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except FileExistsError:
                # Handle case where directory exists but Python thinks it doesn't
                if not directory.is_dir():
                    print(f"⚠️  {directory} exists but is not a directory")
                # Continue regardless - directory exists
                pass
            except Exception as e:
                print(f"⚠️  Could not create {directory}: {e}")
            
        # Create __init__.py files for Python modules
        init_files = [
            self.project_root / "scraper" / "__init__.py",
            self.project_root / "matcher" / "__init__.py",
            self.project_root / "api" / "__init__.py"  # Your API init
        ]
        
        for init_file in init_files:
            try:
                if not init_file.exists():
                    init_file.touch()
            except Exception as e:
                print(f"⚠️  Could not create {init_file}: {e}")
        
        print(f"✅ Project directories ready in {self.project_root}")
    
    def get_database_url(self):
        """Get database URL (for future SQLite integration)"""
        return f"sqlite:///{self.output_dir}/jobs.db"
    
    def validate_environment(self):
        """Validate required environment variables"""
        required_vars = ['COHERE_API_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
            print("💡 Create a .env file or set these in your environment")
        
        return len(missing_vars) == 0
    
    def get_cv_content(self):
        """Load CV content from your assets/cv.txt"""
        try:
            if self.cv_text_path.exists():
                with open(self.cv_text_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                print(f"⚠️  CV file not found at {self.cv_text_path}")
                return self.get_default_cv()
        except Exception as e:
            print(f"❌ Error loading CV: {e}")
            return self.get_default_cv()
    
    def get_default_cv(self):
        """Default CV content if file is missing"""
        return """Lucas Rizzo - Web3 Engineer & DeFi Bot Developer

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
• Achieved 18% job application response rate (vs 2-3% industry average)
• Co-founded and scaled food startup to £100k+ revenue in 6 months
• CompTIA Security+ certified

WORK PREFERENCES
• Remote work preferred (async collaboration)
• Open to contract, part-time, or full-time opportunities
• Passionate about decentralized technologies and financial innovation"""

# Global config instance
config = Config()

# Auto-create directories on import (but handle errors gracefully)
if __name__ != "__main__":
    try:
        config.create_directories()
    except Exception as e:
        # Don't crash on directory issues during import
        pass
