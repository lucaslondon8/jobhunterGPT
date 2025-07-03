#!/usr/bin/env python3
"""
scraper/scrape_and_match.py - Real Job Scraping Module
Scrapes actual job sites for Web3/tech positions
"""

import os
import sys
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
from typing import List, Dict, Any
import json

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

class RealJobScraper:
    """Real job scraper for Web3 and tech positions"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _check_connection(self, url: str) -> bool:
        """Return True if a HEAD request succeeds."""
        try:
            resp = self.session.head(url, timeout=10)
            return resp.status_code < 400
        except Exception:
            return False
        
    def scrape_remote_ok(self, keywords=['web3', 'blockchain', 'defi', 'solidity'], limit=20):
        """Scrape Remote OK for Web3 jobs"""
        jobs = []

        try:
            print("🔍 Scraping Remote OK...")
            if not self._check_connection("https://remoteok.io"):
                print("⚠️  Cannot connect to Remote OK")
                return jobs
            
            # Remote OK has a JSON API
            url = "https://remoteok.io/api"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Skip the first item (it's metadata)
                job_listings = data[1:] if len(data) > 1 else []
                
                for job in job_listings[:limit]:
                    if self._is_relevant_job(job, keywords):
                        processed_job = self._process_remote_ok_job(job)
                        if processed_job:
                            jobs.append(processed_job)
                
                print(f"✅ Found {len(jobs)} relevant jobs on Remote OK")
            else:
                print(f"❌ Remote OK request failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error scraping Remote OK: {e}")
        
        return jobs
    
    def scrape_crypto_jobs(self, limit=20):
        """Scrape CryptoJobs.com for blockchain positions"""
        jobs = []

        try:
            print("🔍 Scraping CryptoJobs...")
            if not self._check_connection("https://cryptojobs.com"):
                print("⚠️  Cannot connect to CryptoJobs")
                return jobs
            
            url = "https://cryptojobs.com/"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find job listings (adjust selectors based on actual site structure)
                job_cards = soup.find_all('div', class_='job-card') or soup.find_all('article', class_='job')
                
                for card in job_cards[:limit]:
                    processed_job = self._process_crypto_jobs_job(card)
                    if processed_job:
                        jobs.append(processed_job)
                
                print(f"✅ Found {len(jobs)} jobs on CryptoJobs")
            else:
                print(f"❌ CryptoJobs request failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error scraping CryptoJobs: {e}")
        
        return jobs
    
    def scrape_indeed_uk(self, keywords=['web3', 'blockchain', 'solidity'], location='United Kingdom', limit=20):
        """Scrape Indeed UK for tech jobs"""
        jobs = []

        try:
            print("🔍 Scraping Indeed UK...")
            if not self._check_connection("https://uk.indeed.com"):
                print("⚠️  Cannot connect to Indeed UK")
                return jobs
            
            base_url = "https://uk.indeed.com/jobs"
            search_terms = " OR ".join(keywords)
            
            params = {
                'q': search_terms,
                'l': location,
                'start': 0
            }
            
            response = self.session.get(base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Indeed job cards (selector may need updating)
                job_cards = soup.find_all('div', class_='job_seen_beacon') or soup.find_all('a', {'data-jk': True})
                
                for card in job_cards[:limit]:
                    processed_job = self._process_indeed_job(card)
                    if processed_job:
                        jobs.append(processed_job)
                
                print(f"✅ Found {len(jobs)} jobs on Indeed UK")
            else:
                print(f"❌ Indeed UK request failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error scraping Indeed UK: {e}")
        
        return jobs
    
    def scrape_github_jobs(self, keywords=['web3', 'blockchain', 'ethereum'], limit=15):
        """Scrape GitHub Jobs API (if available) or job boards"""
        jobs = []

        try:
            print("🔍 Searching GitHub for job repos...")
            if not self._check_connection("https://api.github.com"):
                print("⚠️  Cannot connect to GitHub")
                return jobs
            
            # Search GitHub repositories that contain job postings
            for keyword in keywords:
                url = f"https://api.github.com/search/repositories"
                params = {
                    'q': f'{keyword} jobs OR {keyword} careers',
                    'sort': 'updated',
                    'order': 'desc'
                }
                
                response = self.session.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for repo in data.get('items', [])[:5]:  # Check top 5 repos per keyword
                        repo_jobs = self._extract_jobs_from_github_repo(repo, keyword)
                        jobs.extend(repo_jobs)
                
                time.sleep(1)  # Rate limiting
                
            print(f"✅ Found {len(jobs)} jobs from GitHub")
                
        except Exception as e:
            print(f"❌ Error scraping GitHub: {e}")
        
        return jobs
    
    def _is_relevant_job(self, job_data, keywords):
        """Check if job is relevant to our keywords"""
        text_to_check = ""
        
        if isinstance(job_data, dict):
            text_to_check = f"{job_data.get('position', '')} {job_data.get('description', '')} {job_data.get('tags', '')}"
        
        text_to_check = text_to_check.lower()
        
        # Check for Web3/blockchain relevance
        web3_keywords = ['web3', 'blockchain', 'defi', 'ethereum', 'solidity', 'smart contract', 'crypto', 'dapp']
        tech_keywords = ['python', 'javascript', 'node.js', 'react', 'backend', 'full stack']
        
        has_web3 = any(keyword in text_to_check for keyword in web3_keywords)
        has_tech = any(keyword in text_to_check for keyword in tech_keywords)
        
        return has_web3 or (has_tech and len(text_to_check) > 50)
    
    def _process_remote_ok_job(self, job_data):
        """Process Remote OK job data"""
        try:
            return {
                'title': job_data.get('position', 'Unknown Title'),
                'company': job_data.get('company', 'Unknown Company'),
                'location': 'Remote',
                'salary': self._extract_salary(job_data.get('description', '')),
                'description': job_data.get('description', '')[:500],
                'tags': job_data.get('tags', []) if isinstance(job_data.get('tags'), list) else [],
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'url': job_data.get('url', ''),
                'contact_email': self._extract_email(job_data.get('description', '')),
                'source': 'Remote OK'
            }
        except Exception as e:
            print(f"❌ Error processing Remote OK job: {e}")
            return None
    
    def _process_crypto_jobs_job(self, job_card):
        """Process CryptoJobs job card"""
        try:
            title = job_card.find('h3') or job_card.find('h2') or job_card.find('a')
            company = job_card.find(class_='company') or job_card.find('span', text=re.compile(r'Company|Organization'))
            
            return {
                'title': title.get_text(strip=True) if title else 'Unknown Title',
                'company': company.get_text(strip=True) if company else 'Unknown Company',
                'location': 'Remote/Global',
                'salary': 'Competitive',
                'description': job_card.get_text(strip=True)[:500],
                'tags': ['Crypto', 'Blockchain'],
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'url': self._extract_link(job_card),
                'contact_email': self._extract_email(job_card.get_text()),
                'source': 'CryptoJobs'
            }
        except Exception as e:
            print(f"❌ Error processing CryptoJobs job: {e}")
            return None
    
    def _process_indeed_job(self, job_card):
        """Process Indeed job card"""
        try:
            title_elem = job_card.find('h2') or job_card.find('a', {'data-jk': True})
            company_elem = job_card.find(class_='companyName') or job_card.find('span', class_='companyName')
            location_elem = job_card.find(class_='companyLocation')
            
            return {
                'title': title_elem.get_text(strip=True) if title_elem else 'Unknown Title',
                'company': company_elem.get_text(strip=True) if company_elem else 'Unknown Company',
                'location': location_elem.get_text(strip=True) if location_elem else 'UK',
                'salary': self._extract_salary_from_card(job_card),
                'description': job_card.get_text(strip=True)[:500],
                'tags': ['Tech'],
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'url': self._extract_indeed_link(job_card),
                'contact_email': '',
                'source': 'Indeed UK'
            }
        except Exception as e:
            print(f"❌ Error processing Indeed job: {e}")
            return None
    
    def _extract_jobs_from_github_repo(self, repo, keyword):
        """Extract job postings from GitHub repository"""
        jobs = []
        
        try:
            # Look for README or jobs directory
            contents_url = repo['contents_url'].replace('{+path}', '')
            response = self.session.get(contents_url, timeout=15)
            
            if response.status_code == 200:
                files = response.json()
                
                for file_info in files:
                    if file_info['name'].lower() in ['readme.md', 'jobs.md', 'careers.md']:
                        # Download and parse the file
                        file_response = self.session.get(file_info['download_url'], timeout=15)
                        if file_response.status_code == 200:
                            content = file_response.text
                            
                            # Extract job-like patterns from markdown
                            job_sections = self._parse_markdown_jobs(content, repo['name'])
                            jobs.extend(job_sections)
                        
                        break  # Only check first relevant file
                
        except Exception as e:
            print(f"⚠️  Error extracting from GitHub repo: {e}")
        
        return jobs
    
    def _parse_markdown_jobs(self, content, repo_name):
        """Parse job postings from markdown content"""
        jobs = []
        
        try:
            # Look for job-like sections (headers with "engineer", "developer", etc.)
            lines = content.split('\n')
            current_job = None
            
            for line in lines:
                line = line.strip()
                
                # Check if line looks like a job title
                if (line.startswith('#') and 
                    any(word in line.lower() for word in ['engineer', 'developer', 'position', 'role', 'job'])):
                    
                    if current_job:
                        jobs.append(current_job)
                    
                    current_job = {
                        'title': line.lstrip('# ').strip(),
                        'company': repo_name.replace('-', ' ').title(),
                        'location': 'Remote',
                        'salary': 'Not specified',
                        'description': '',
                        'tags': ['Open Source'],
                        'posted_date': datetime.now().strftime('%Y-%m-%d'),
                        'url': f"https://github.com/{repo_name}",
                        'contact_email': '',
                        'source': 'GitHub'
                    }
                
                elif current_job and line:
                    current_job['description'] += line + ' '
            
            if current_job:
                jobs.append(current_job)
                
        except Exception as e:
            print(f"❌ Error parsing markdown: {e}")
        
        return jobs
    
    def _extract_salary(self, text):
        """Extract salary information from text"""
        if not text:
            return 'Not specified'
        
        # Look for salary patterns
        salary_patterns = [
            r'[\$£€]\s*\d{1,3}[,\d]*\s*[-–]\s*[\$£€]?\s*\d{1,3}[,\d]*',
            r'\d{1,3}[,\d]*\s*[-–]\s*\d{1,3}[,\d]*\s*[k|K]',
            r'[\$£€]\s*\d{1,3}[,\d]*[k|K]?'
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return 'Competitive'
    
    def _extract_salary_from_card(self, card):
        """Extract salary from job card"""
        salary_elem = card.find(class_='salary') or card.find('span', text=re.compile(r'[\$£€]'))
        return salary_elem.get_text(strip=True) if salary_elem else 'Not specified'
    
    def _extract_email(self, text):
        """Extract email address from text"""
        if not text:
            return ''
        
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else ''
    
    def _extract_link(self, element):
        """Extract link from element"""
        link = element.find('a')
        if link and link.get('href'):
            href = link.get('href')
            if href.startswith('http'):
                return href
            elif href.startswith('/'):
                return f"https://cryptojobs.com{href}"
        return ''
    
    def _extract_indeed_link(self, card):
        """Extract Indeed job link"""
        link = card.find('a', {'data-jk': True})
        if link and link.get('data-jk'):
            return f"https://uk.indeed.com/job/{link.get('data-jk')}"
        return ''

def scrape_web3_jobs(max_jobs=120):
    """Main function to scrape Web3 jobs from multiple sources"""
    print("🚀 Starting REAL job scraping...")
    
    scraper = RealJobScraper()
    all_jobs = []
    
    # Scrape from multiple sources
    sources = [
        ('Remote OK', lambda: scraper.scrape_remote_ok(limit=40)),
        ('CryptoJobs', lambda: scraper.scrape_crypto_jobs(limit=30)),
        ('Indeed UK', lambda: scraper.scrape_indeed_uk(limit=30)),
        ('GitHub', lambda: scraper.scrape_github_jobs(limit=20))
    ]
    
    for source_name, scrape_func in sources:
        try:
            print(f"\n📡 Scraping {source_name}...")
            jobs = scrape_func()
            all_jobs.extend(jobs)
            print(f"✅ {source_name}: {len(jobs)} jobs found")
            
            # Rate limiting between sources
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ {source_name} failed: {e}")
            continue
    
    # Remove duplicates based on title + company
    seen = set()
    unique_jobs = []
    
    for job in all_jobs:
        job_key = f"{job.get('title', '')}-{job.get('company', '')}"
        if job_key not in seen:
            seen.add(job_key)
            unique_jobs.append(job)
    
    print(f"\n🎯 Total unique jobs found: {len(unique_jobs)}")
    
    # Limit to max_jobs and return
    return unique_jobs[:max_jobs]

def save_jobs_to_csv(jobs_data, output_path):
    """Save scraped jobs to CSV file"""
    try:
        if not jobs_data:
            print("❌ No jobs to save")
            return False
            
        df = pd.DataFrame(jobs_data)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Add metadata
        for i, job in enumerate(jobs_data):
            df.loc[i, 'scraped_date'] = datetime.now().isoformat()
            df.loc[i, 'application_status'] = 'pending'
            
        # Save to CSV
        df.to_csv(output_path, index=False)
        print(f"✅ Saved {len(jobs_data)} real jobs to {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving jobs: {e}")
        return False

def main():
    """Main scraping function called by your bot"""
    print("🚀 Starting REAL Web3 job discovery...")
    
    try:
        # Import config for output path
        try:
            from config import config
            output_path = str(config.output_csv)
        except ImportError:
            output_path = "output/jobs.csv"
        
        # Scrape real jobs
        jobs_data = scrape_web3_jobs(max_jobs=120)
        
        if not jobs_data:
            print("❌ No real jobs found")
            return False
        
        # Save to CSV
        success = save_jobs_to_csv(jobs_data, output_path)
        
        if success:
            print(f"🎯 REAL job discovery complete! Found {len(jobs_data)} opportunities")
            print(f"📊 Sources used: Remote OK, CryptoJobs, Indeed UK, GitHub")
            print(f"📧 Jobs with contact emails: {sum(1 for job in jobs_data if job.get('contact_email'))}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Real scraping failed: {e}")
        return False

if __name__ == "__main__":
    # Test the real scraper
    main()
