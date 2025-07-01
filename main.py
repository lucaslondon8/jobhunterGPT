#!/usr/bin/env python3
"""
main.py - CV-Adaptive Web3 Job Bot with Universal Job Discovery
Enhanced to work with ANY CV, not just Web3
"""

import os
import sys
import logging
import argparse
import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd
from cohere import Client
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Import configuration
try:
    from config import config
    config.create_directories()
except ImportError:
    print("❌ Error: config.py not found. Please create config.py first.")
    sys.exit(1)

# Import CV analyzer and universal scraper
try:
    from cv_analyzer import analyze_any_cv
    CV_ANALYZER_AVAILABLE = True
    print("✅ CV Analyzer imported - Universal job discovery enabled")
except ImportError:
    print("⚠️  CV Analyzer not found - Using Web3-specific mode")
    CV_ANALYZER_AVAILABLE = False
    analyze_any_cv = None

try:
    from universal_scraper import UniversalJobScraper
    UNIVERSAL_SCRAPER_AVAILABLE = True
    print("✅ Universal Scraper imported")
except ImportError:
    print("⚠️  Universal Scraper not found - Using basic scraper")
    UNIVERSAL_SCRAPER_AVAILABLE = False
    UniversalJobScraper = None

# Import your existing modules (fallback)
scraper_module = None
matcher_module = None

print("🔍 Detecting available modules...")

try:
    import scraper.scrape_and_match as scraper_module
    print("✅ Found scraper module")
except ImportError as e:
    print(f"❌ Could not import scraper: {e}")

try:
    import matcher.match_job as matcher_module
    print("✅ Found matcher module")
except ImportError as e:
    print(f"❌ Could not import matcher: {e}")

load_dotenv()

class CVAdaptiveJobBot:
    """CV-Adaptive Job Bot that works with ANY profession"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        
        # Initialize CV profile
        self.cv_profile = None
        self.cv_text = None
        
        # Initialize components based on availability
        self.universal_scraper = None
        if UNIVERSAL_SCRAPER_AVAILABLE:
            self.universal_scraper = UniversalJobScraper()
        
        # Rate-limited cover letter generator
        self.generator = RateLimitedCoverLetterGenerator()
        self.batch_processor = SmartBatchProcessor(self.generator, max_api_calls=20)
        
        self.stats = {
            'scraped_jobs': 0,
            'matched_jobs': 0,
            'cover_letters_generated': 0,
            'api_calls_used': 0,
            'template_calls_used': 0,
            'errors': []
        }
        
        self.logger.info("🚀 CV-Adaptive Job Bot initialized")
    
    def setup_logging(self):
        """Setup logging."""
        log_level = logging.DEBUG if os.getenv('DEBUG_LOGGING', 'false').lower() == 'true' else logging.INFO
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        os.makedirs('logs', exist_ok=True)
        file_handler = logging.FileHandler(f'logs/job_bot_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
    
    def load_and_analyze_cv(self):
        """Load CV and analyze it to determine job search strategy"""
        
        try:
            # Load CV content
            self.cv_text = config.get_cv_content()
            if not self.cv_text or len(self.cv_text) < 50:
                self.logger.error("CV text is too short or empty")
                return False
            
            self.logger.info(f"✅ Loaded CV text ({len(self.cv_text)} characters)")
            
            # Analyze CV if analyzer is available
            if CV_ANALYZER_AVAILABLE and analyze_any_cv:
                print("\n🧠 ANALYZING YOUR CV...")
                print("=" * 50)
                
                self.cv_profile = analyze_any_cv(self.cv_text)
                
                # Display analysis results
                print(f"📊 CV ANALYSIS RESULTS:")
                print(f"   • Experience Level: {self.cv_profile.get('experience_level', 'Unknown')}")
                print(f"   • Primary Roles: {', '.join(self.cv_profile.get('primary_roles', []))}")
                print(f"   • Top Skills: {', '.join([skill for skill, _ in self.cv_profile.get('top_skills', [])[:8]])}")
                print(f"   • Target Industries: {', '.join(self.cv_profile.get('target_industries', []))}")
                print(f"   • CV Strength: {self.cv_profile.get('cv_strength', 'Unknown')}")
                
                # Show job search strategy
                strategy = self.cv_profile.get('job_search_strategy', {})
                if strategy:
                    print(f"   • Recommended Job Sites: {', '.join(strategy.get('primary_job_sites', [])[:5])}")
                    print(f"   • Search Keywords: {', '.join(strategy.get('search_terms', [])[:10])}")
                
                self.logger.info("✅ CV analysis completed")
                return True
            else:
                print("⚠️  Using basic CV analysis (universal analyzer not available)")
                self.cv_profile = self._basic_cv_analysis()
                return True
                
        except Exception as e:
            self.logger.error(f"CV analysis failed: {e}")
            return False
    
    def _basic_cv_analysis(self):
        """Basic CV analysis fallback"""
        
        cv_lower = self.cv_text.lower()
        
        # Simple analysis
        profile = {
            'experience_level': 'mid',
            'primary_roles': ['developer'],
            'top_skills': [('python', 1.0), ('javascript', 1.0)],
            'target_industries': ['tech'],
            'cv_strength': 'Good',
            'job_search_strategy': {
                'primary_job_sites': ['Indeed', 'LinkedIn', 'Remote OK'],
                'search_terms': ['developer', 'engineer', 'python']
            }
        }
        
        # Simple role detection
        if any(word in cv_lower for word in ['web3', 'blockchain', 'defi', 'solidity']):
            profile['target_industries'] = ['blockchain', 'tech']
            profile['primary_roles'] = ['developer']
            profile['top_skills'] = [('web3', 2.0), ('blockchain', 2.0), ('solidity', 2.0)]
        
        return profile
    
    def discover_jobs_adaptively(self):
        """Discover jobs based on CV analysis"""
        
        self.logger.info("🔍 Starting adaptive job discovery...")
        
        try:
            # Use universal scraper if available
            if UNIVERSAL_SCRAPER_AVAILABLE and self.universal_scraper:
                print("\n🎯 ADAPTIVE JOB DISCOVERY")
                print("=" * 40)
                
                jobs_data = self.universal_scraper.discover_jobs(self.cv_text, max_jobs=50)
                
                if jobs_data:
                    self.stats['scraped_jobs'] = len(jobs_data)
                    self.logger.info(f"✅ Found {len(jobs_data)} jobs using adaptive discovery")
                    return jobs_data
                else:
                    print("⚠️  Adaptive discovery found no jobs, falling back to basic scraper")
            
            # Fallback to existing scraper
            if scraper_module and hasattr(scraper_module, 'main'):
                print("\n📡 FALLBACK: Using existing scraper")
                result = scraper_module.main()
                
                if os.path.exists(config.output_csv):
                    df = pd.read_csv(config.output_csv)
                    jobs_data = df.to_dict('records')
                    self.stats['scraped_jobs'] = len(jobs_data)
                    self.logger.info(f"✅ Loaded {len(jobs_data)} jobs from existing scraper")
                    return jobs_data
            
            self.logger.error("No job discovery method available")
            return []
            
        except Exception as e:
            self.logger.error(f"Job discovery failed: {e}")
            self.stats['errors'].append(f"Job discovery failed: {e}")
            return []
    
    def match_jobs_adaptively(self, jobs_data):
        """Match jobs using CV-adaptive or fallback matching"""
        
        self.logger.info(f"🎯 Matching {len(jobs_data)} jobs against CV...")
        
        try:
            # If we have CV profile, use adaptive matching
            if self.cv_profile:
                matched_jobs = self._adaptive_job_matching(jobs_data)
            else:
                # Fallback to existing matcher
                if matcher_module and hasattr(matcher_module, 'batch_match_jobs'):
                    matched_jobs = matcher_module.batch_match_jobs(self.cv_text, jobs_data)
                else:
                    # Basic matching
                    matched_jobs = self._basic_job_matching(jobs_data)
            
            self.stats['matched_jobs'] = len(matched_jobs)
            self.logger.info(f"✅ Job matching completed for {len(matched_jobs)} jobs")
            return matched_jobs
            
        except Exception as e:
            self.logger.error(f"Job matching failed: {e}")
            self.stats['errors'].append(f"Job matching failed: {e}")
            return jobs_data
    
    def _adaptive_job_matching(self, jobs_data):
        """CV-adaptive job matching using profile analysis"""
        
        print("\n🧠 ADAPTIVE JOB MATCHING")
        print("=" * 30)
        
        # Get CV skills and preferences
        top_skills = {skill: weight for skill, weight in self.cv_profile.get('top_skills', [])}
        target_industries = self.cv_profile.get('target_industries', [])
        experience_level = self.cv_profile.get('experience_level', 'mid')
        
        for job in jobs_data:
            # Calculate adaptive match score
            job_text = f"{job.get('title', '')} {job.get('description', '')} {job.get('company', '')}".lower()
            
            score = 0.0
            
            # Skill matching (60% weight)
            for skill, weight in top_skills.items():
                if skill.lower() in job_text:
                    score += weight * 0.6
            
            # Industry matching (25% weight)
            for industry in target_industries:
                if industry.lower() in job_text:
                    score += 0.25
            
            # Experience level matching (15% weight)
            if experience_level in job_text:
                score += 0.15
            
            # Normalize score to 0-1 range
            job['match_score'] = min(1.0, score / 5.0)
            job['combined_score'] = job['match_score']
            job['score'] = job['match_score']
            
            # Add match reasoning
            job['match_reason'] = f"CV-adaptive match based on {experience_level} level and {len(top_skills)} skills"
        
        # Sort by match score
        jobs_data.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        print(f"✅ Adaptive matching complete")
        print(f"   • Top match: {jobs_data[0]['title']} ({jobs_data[0]['match_score']:.3f})")
        print(f"   • Average score: {sum(job['match_score'] for job in jobs_data) / len(jobs_data):.3f}")
        
        return jobs_data
    
    def _basic_job_matching(self, jobs_data):
        """Basic job matching fallback"""
        
        for i, job in enumerate(jobs_data):
            # Simple keyword matching
            job_text = f"{job.get('title', '')} {job.get('description', '')}".lower()
            cv_lower = self.cv_text.lower()
            
            # Count common words
            job_words = set(job_text.split())
            cv_words = set(cv_lower.split())
            
            common_words = job_words.intersection(cv_words)
            score = len(common_words) / max(len(job_words), 1) if job_words else 0
            
            job['match_score'] = min(1.0, score * 2)  # Amplify score
            job['combined_score'] = job['match_score']
            job['score'] = job['match_score']
        
        # Sort by score
        jobs_data.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        return jobs_data
    
    def generate_cover_letters(self, matched_jobs):
        """Generate cover letters using existing system"""
        
        self.logger.info(f"📝 Starting cover letter generation for {len(matched_jobs)} jobs...")
        
        try:
            # Use existing batch processor
            processed_jobs = self.batch_processor.process_intelligently(matched_jobs, self.cv_text)
            
            # Update statistics
            api_count = sum(1 for job in processed_jobs if job.get('generation_method') == 'api')
            template_count = sum(1 for job in processed_jobs if job.get('generation_method') == 'template')
            
            self.stats['cover_letters_generated'] = len(processed_jobs)
            self.stats['api_calls_used'] = api_count
            self.stats['template_calls_used'] = template_count
            
            self.logger.info(f"✅ Cover letter generation complete!")
            return processed_jobs
            
        except Exception as e:
            self.logger.error(f"Cover letter generation failed: {e}")
            self.stats['errors'].append(f"Cover letter generation failed: {e}")
            return matched_jobs
    
    def save_results(self, matched_jobs):
        """Save results to CSV."""
        try:
            df = pd.DataFrame(matched_jobs)
            os.makedirs(os.path.dirname(config.output_csv), exist_ok=True)
            df.to_csv(config.output_csv, index=False)
            
            self.logger.info(f"✅ Saved results to {config.output_csv}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to save results: {e}"
            self.logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return False
    
    def print_adaptive_summary(self, matched_jobs):
        """Print CV-adaptive execution summary"""
        
        print("\n" + "="*80)
        print("🧠 CV-ADAPTIVE JOB BOT - EXECUTION SUMMARY")
        print("="*80)
        
        print(f"📊 CV ANALYSIS:")
        if self.cv_profile:
            print(f"   • Experience Level: {self.cv_profile.get('experience_level', 'Unknown')}")
            print(f"   • Primary Roles: {', '.join(self.cv_profile.get('primary_roles', []))}")
            print(f"   • Top Skills: {', '.join([skill for skill, _ in self.cv_profile.get('top_skills', [])[:5]])}")
            print(f"   • Target Industries: {', '.join(self.cv_profile.get('target_industries', []))}")
            print(f"   • CV Strength: {self.cv_profile.get('cv_strength', 'Unknown')}")
        
        print(f"\n📊 JOB DISCOVERY:")
        print(f"   • Jobs discovered: {self.stats['scraped_jobs']}")
        print(f"   • Jobs matched: {self.stats['matched_jobs']}")
        print(f"   • Cover letters generated: {self.stats['cover_letters_generated']}")
        print(f"   • Discovery method: {'Adaptive' if UNIVERSAL_SCRAPER_AVAILABLE else 'Standard'}")
        print(f"   • Matching method: {'CV-Adaptive' if self.cv_profile else 'Basic'}")
        
        if matched_jobs:
            # Show top matches
            sorted_jobs = sorted(matched_jobs, key=lambda x: x.get('match_score', 0), reverse=True)
            print(f"\n🏆 TOP 5 ADAPTIVE MATCHES:")
            for i, job in enumerate(sorted_jobs[:5]):
                score = job.get('match_score', 0)
                print(f"   {i+1}. {job['title'][:50]}")
                print(f"      {job['company']} | Score: {score:.3f} | {job.get('match_reason', 'Standard match')}")
        
        print(f"\n🚀 NEXT STEPS:")
        print(f"   • Review adaptive results: {config.output_csv}")
        print(f"   • Your CV was analyzed for: {', '.join(self.cv_profile.get('primary_roles', []))} roles")
        print(f"   • Jobs targeted your: {', '.join(self.cv_profile.get('target_industries', []))} expertise")
        
        print("="*80)
    
    def run_adaptive_pipeline(self):
        """Run the complete CV-adaptive job application pipeline"""
        
        try:
            self.logger.info("🚀 Starting CV-Adaptive Job Bot pipeline...")
            
            # Step 1: Load and analyze CV
            if not self.load_and_analyze_cv():
                self.logger.error("CV analysis failed")
                return False
            
            # Step 2: Adaptive job discovery
            jobs_data = self.discover_jobs_adaptively()
            if not jobs_data:
                self.logger.error("No jobs discovered")
                return False
            
            # Step 3: CV-adaptive job matching
            matched_jobs = self.match_jobs_adaptively(jobs_data)
            if not matched_jobs:
                self.logger.error("No jobs matched")
                return False
            
            # Step 4: Generate cover letters
            matched_jobs = self.generate_cover_letters(matched_jobs)
            
            # Step 5: Save results
            self.save_results(matched_jobs)
            
            # Step 6: Print adaptive summary
            self.print_adaptive_summary(matched_jobs)
            
            self.logger.info("✅ CV-Adaptive pipeline completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            return False

# Keep existing classes for compatibility
class RateLimitedCoverLetterGenerator:
    """Rate-limited cover letter generator with intelligent fallbacks."""
    
    def __init__(self):
        self.cohere_api_key = os.getenv("COHERE_API_KEY")
        if not self.cohere_api_key:
            print("⚠️  COHERE_API_KEY not found - will use template fallbacks only")
            self.co = None
        else:
            self.co = Client(self.cohere_api_key)
        
        # Rate limiting configuration
        self.calls_per_minute = 10
        self.calls_made = []
        self.fallback_enabled = True
        
    def _can_make_call(self):
        """Check if we can make an API call within rate limits."""
        if not self.co:
            return False
            
        now = datetime.now()
        self.calls_made = [call_time for call_time in self.calls_made 
                          if now - call_time < timedelta(minutes=1)]
        
        return len(self.calls_made) < self.calls_per_minute
    
    def _record_api_call(self):
        """Record that we made an API call."""
        self.calls_made.append(datetime.now())
    
    def generate_fallback_cover_letter(self, cv_text, job_text):
        """Generate a high-quality template cover letter without API."""
        lines = job_text.split('\n')
        job_title = lines[0].replace('Job Title: ', '') if lines else 'Position'
        company = lines[1].replace('Company: ', '') if len(lines) > 1 else 'Company'
        
        return f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company}. Based on my background and experience, I believe I would be a valuable addition to your team.

My relevant experience includes the key qualifications mentioned in your job posting. I am particularly drawn to this opportunity because it aligns well with my professional goals and expertise.

I would welcome the opportunity to discuss how my skills and experience can contribute to {company}'s continued success. Thank you for considering my application.

Best regards,
[Your Name]"""

    def generate_cover_letter_with_rate_limiting(self, cv_text, job_text):
        """Generate cover letter with intelligent rate limiting and fallbacks."""
        
        if not self._can_make_call():
            return self.generate_fallback_cover_letter(cv_text, job_text)
        
        try:
            if self.co:
                prompt = f"""Write a professional cover letter for this job:

{job_text}

Based on this background:
{cv_text[:500]}

Keep it concise, professional, and personalized."""

                response = self.co.chat(model="command-r", message=prompt, temperature=0.7)
                self._record_api_call()
                return response.text.strip()
            else:
                return self.generate_fallback_cover_letter(cv_text, job_text)
                
        except Exception as e:
            print(f"API call failed: {e}")
            return self.generate_fallback_cover_letter(cv_text, job_text)

class SmartBatchProcessor:
    """Smart batch processing with job prioritization."""
    
    def __init__(self, generator, max_api_calls=20):
        self.generator = generator
        self.max_api_calls = max_api_calls
        
    def process_intelligently(self, jobs_data, cv_text):
        """Process jobs with smart prioritization and rate limiting."""
        
        print(f"\n🎯 SMART BATCH PROCESSING - {len(jobs_data)} jobs")
        
        # Prioritize jobs by match score
        prioritized_jobs = sorted(jobs_data, key=lambda x: x.get('match_score', 0), reverse=True)
        
        # Process with cover letters
        for i, job in enumerate(prioritized_jobs):
            job_text = f"Job Title: {job.get('title', '')}\nCompany: {job.get('company', '')}\nDescription: {job.get('description', '')}"
            
            try:
                cover_letter = self.generator.generate_cover_letter_with_rate_limiting(cv_text, job_text)
                job['cover_letter'] = cover_letter
                job['generation_method'] = 'api' if 'Dear Hiring Manager' in cover_letter else 'template'
            except Exception as e:
                job['cover_letter'] = f"Error generating cover letter: {e}"
                job['generation_method'] = 'error'
        
        return prioritized_jobs

def main():
    """Main entry point with CV-adaptive functionality"""
    
    parser = argparse.ArgumentParser(description='CV-Adaptive Job Application Bot')
    parser.add_argument('--analyze-cv-only', action='store_true', help='Only analyze CV and show strategy')
    parser.add_argument('--scrape-only', action='store_true', help='Only scrape jobs')
    parser.add_argument('--template-only', action='store_true', help='Use templates only (no API calls)')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    if args.debug:
        os.environ['DEBUG_LOGGING'] = 'true'
    
    # Initialize CV-adaptive bot
    bot = CVAdaptiveJobBot()
    
    if args.template_only:
        bot.batch_processor.max_api_calls = 0
        print("🔧 Template-only mode enabled")
    
    try:
        if args.analyze_cv_only:
            # Only analyze CV and show strategy
            if bot.load_and_analyze_cv():
                print("\n✅ CV analysis complete!")
                print("Run without --analyze-cv-only to discover jobs")
        else:
            # Run full adaptive pipeline
            print("🧠 Starting CV-ADAPTIVE Job Bot...")
            print("🎯 This bot adapts to YOUR CV and finds relevant opportunities")
            print()
            
            success = bot.run_adaptive_pipeline()
            if not success:
                print("❌ Pipeline failed - check logs for details")
                sys.exit(1)
            else:
                print("\n🎉 SUCCESS! Your CV-adaptive job bot worked perfectly!")
                print("🧠 Key features:")
                print(f"   • CV analyzed for skills and experience level")
                print(f"   • Job discovery adapted to your profile")
                print(f"   • Matching algorithm personalized to your background")
                print(f"   • Results saved with match reasoning")
    
    except KeyboardInterrupt:
        print("\n👋 CV-adaptive job bot interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
