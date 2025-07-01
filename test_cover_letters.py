#!/usr/bin/env python3
"""
test_cover_letters.py - Test cover letter generation
"""

def test_cover_letter_generation():
    """Test the cover letter generation with real data"""
    
    try:
        # Import your modules
        from config import config
        import main
        
        print("🧪 Testing cover letter generation...")
        
        # Initialize bot
        bot = main.Web3JobBot()
        
        # Load CV
        cv_text = bot.load_cv_text()
        print(f"✅ CV loaded: {len(cv_text)} characters")
        
        # Test with a simple job
        test_job = {
            'title': 'Web3 Engineer',
            'company': 'Test Company',
            'description': 'Looking for Web3 developer with Solidity skills',
            'tags': ['Web3', 'Solidity'],
            'combined_score': 0.8
        }
        
        # Test cover letter generation
        generator = bot.generator
        job_text = f"Job Title: {test_job['title']}\nCompany: {test_job['company']}\nDescription: {test_job['description']}"
        
        cover_letter = generator.generate_fallback_cover_letter(cv_text, job_text)
        
        if cover_letter and len(cover_letter) > 100:
            print(f"✅ Cover letter generated: {len(cover_letter)} characters")
            print("\n📝 Sample cover letter:")
            print(cover_letter[:200] + "...")
            return True
        else:
            print("❌ Cover letter generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_cover_letter_generation()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}")
