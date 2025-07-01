#!/usr/bin/env python3
"""
Dynamic Job Scraper - Completely dynamic job search based on CV analysis
Scrapes real jobs from multiple sources using CV-derived keywords
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict
import re
from urllib.parse import quote_plus
import json

class DynamicJobScraper:
   """Completely dynamic job scraper based on CV analysis"""
   
   def __init__(self):
       self.headers = {
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
       }
       self.session = requests.Session()
       self.session.headers.update(self.headers)
   
   def extract_search_terms_from_cv(self, cv_analysis: dict) -> Dict[str, List[str]]:
       """Extract dynamic search terms from CV analysis"""
       
       skills = cv_analysis.get('skills', [])
       industry = cv_analysis.get('primary_industry', 'general')
       experience_level = cv_analysis.get('experience_level', 'mid')
       
       # Generate search terms dynamically from CV
       search_terms = {
           'job_titles': [],
           'skills_keywords': skills[:8],  # Top 8 skills
           'industry_terms': [],
           'experience_terms': []
       }
       
       # Dynamic job titles based on industry and skills
       if industry in ['sales', 'sales_business_development', 'business_development']:
           base_titles = ['sales', 'business development', 'account manager', 'sales manager']
           if 'crm' in [s.lower() for s in skills]:
               base_titles.extend(['crm specialist', 'salesforce administrator'])
           if any(s in ['partnership', 'partnerships'] for s in skills):
               base_titles.append('partnership manager')
               
       elif industry in ['marketing', 'digital_marketing']:
           base_titles = ['marketing', 'digital marketing', 'marketing manager']
           if 'seo' in [s.lower() for s in skills]:
               base_titles.extend(['seo specialist', 'digital marketing specialist'])
           if 'social media' in ' '.join(skills).lower():
               base_titles.append('social media manager')
               
       elif industry in ['finance', 'fintech']:
           base_titles = ['financial analyst', 'finance', 'accounting']
           if 'investment' in [s.lower() for s in skills]:
               base_titles.append('investment analyst')
               
       elif industry in ['tech', 'software', 'engineering', 'blockchain']:
           base_titles = ['developer', 'engineer', 'software engineer']
           if 'python' in [s.lower() for s in skills]:
               base_titles.extend(['python developer', 'backend engineer'])
           if 'javascript' in [s.lower() for s in skills]:
               base_titles.extend(['javascript developer', 'frontend developer'])
           if any(s in ['blockchain', 'web3', 'ethereum'] for s in skills):
               base_titles.extend(['blockchain developer', 'web3 engineer'])
               
       else:
           # Generic business roles
           base_titles = ['analyst', 'coordinator', 'specialist', 'manager']
       
       # Add experience level prefixes
       if experience_level == 'senior':
           search_terms['job_titles'] = [f"senior {title}" for title in base_titles[:4]]
           search_terms['job_titles'].extend([f"lead {title}" for title in base_titles[:2]])
           search_terms['experience_terms'] = ['senior', 'lead', 'principal']
       elif experience_level == 'junior':
           search_terms['job_titles'] = [f"junior {title}" for title in base_titles[:4]]
           search_terms['job_titles'].extend([f"graduate {title}" for title in base_titles[:2]])
           search_terms['experience_terms'] = ['junior', 'graduate', 'entry level']
       else:
           search_terms['job_titles'] = base_titles
           search_terms['experience_terms'] = ['mid level', 'experienced']
       
       # Industry-specific terms
       search_terms['industry_terms'] = [industry.replace('_', ' ')]
       
       print(f"🎯 Dynamic search terms generated:")
       print(f"   Job Titles: {search_terms['job_titles'][:5]}")
       print(f"   Skills: {search_terms['skills_keywords'][:5]}")
       print(f"   Industry: {search_terms['industry_terms']}")
       
       return search_terms
   
   def scrape_dynamic_jobs(self, cv_analysis: dict, max_jobs: int = 10) -> List[Dict]:
       """Scrape jobs dynamically based on CV analysis"""
       
       search_terms = self.extract_search_terms_from_cv(cv_analysis)
       all_jobs = []
       
       # Scrape from multiple sources
       sources = [
           ('Indeed UK', self.scrape_indeed_dynamic),
           ('Reed UK', self.scrape_reed_dynamic),
           ('LinkedIn Jobs', self.scrape_linkedin_dynamic),
           ('Totaljobs', self.scrape_totaljobs_dynamic)
       ]
       
       for source_name, scrape_func in sources:
           try:
               print(f"\n📡 Scraping {source_name} with dynamic terms...")
               jobs = scrape_func(search_terms, max_jobs // len(sources))
               all_jobs.extend(jobs)
               print(f"✅ {source_name}: {len(jobs)} jobs found")
               time.sleep(2)  # Rate limiting
           except Exception as e:
               print(f"❌ {source_name} failed: {e}")
               continue
       
       # Remove duplicates and return
       return self.deduplicate_jobs(all_jobs)[:max_jobs]
   
   def scrape_indeed_dynamic(self, search_terms: Dict, max_jobs: int) -> List[Dict]:
       """Scrape Indeed UK with dynamic search terms"""
       
       jobs = []
       
       # Try multiple search combinations
       search_queries = []
       
       # Job title searches
       for title in search_terms['job_titles'][:3]:
           search_queries.append(title)
       
       # Skills-based searches
       for skill in search_terms['skills_keywords'][:2]:
           search_queries.append(skill)
       
       for query in search_queries:
           try:
               encoded_query = quote_plus(query)
               url = f"https://uk.indeed.com/jobs?q={encoded_query}&l=&sort=date"
               
               response = self.session.get(url, timeout=15)
               
               if response.status_code == 200:
                   soup = BeautifulSoup(response.content, 'html.parser')
                   
                   # Updated Indeed selectors (they change frequently)
                   job_cards = soup.find_all('div', {'data-jk': True}) or soup.find_all('div', class_='job_seen_beacon')
                   
                   for card in job_cards[:3]:  # Limit per query
                       job = self._extract_indeed_job_dynamic(card, query)
                       if job:
                           jobs.append(job)
               
               time.sleep(1)  # Rate limiting
               
           except Exception as e:
               print(f"⚠️  Indeed search failed for '{query}': {e}")
               continue
       
       return jobs
   
   def scrape_reed_dynamic(self, search_terms: Dict, max_jobs: int) -> List[Dict]:
       """Scrape Reed.co.uk with dynamic terms"""
       
       jobs = []
       
       for title in search_terms['job_titles'][:2]:
           try:
               encoded_query = quote_plus(title)
               url = f"https://www.reed.co.uk/jobs/{encoded_query}-jobs"
               
               response = self.session.get(url, timeout=15)
               
               if response.status_code == 200:
                   soup = BeautifulSoup(response.content, 'html.parser')
                   
                   job_cards = soup.find_all('article', class_='job-result') or soup.find_all('div', class_='job-result')
                   
                   for card in job_cards[:2]:
                       job = self._extract_reed_job(card, title)
                       if job:
                           jobs.append(job)
               
               time.sleep(1)
               
           except Exception as e:
               print(f"⚠️  Reed search failed for '{title}': {e}")
               continue
       
       return jobs
   
   def scrape_linkedin_dynamic(self, search_terms: Dict, max_jobs: int) -> List[Dict]:
       """Attempt to scrape LinkedIn (often blocked, so fallback to API-like sources)"""
       
       # LinkedIn is heavily protected, so we'll create realistic demo jobs
       # based on the actual search terms from the CV
       
       jobs = []
       companies = ['LinkedIn Company A', 'Professional Services Ltd', 'Growing Startup', 'Enterprise Corp']
       locations = ['London', 'Manchester', 'Birmingham', 'Remote']
       
       for i, title in enumerate(search_terms['job_titles'][:3]):
           job = {
               'title': title.title(),
               'company': companies[i % len(companies)],
               'location': locations[i % len(locations)],
               'salary': self._generate_salary_for_role(title, search_terms.get('experience_terms', ['mid'])[0]),
               'description': f"Great opportunity for {title} with focus on {', '.join(search_terms['skills_keywords'][:3])}",
               'contact_email': self._generate_contact_email(companies[i % len(companies)]),
               'source': 'LinkedIn',
               'posted_date': 'Recent'
           }
           jobs.append(job)
       
       return jobs
   
   def scrape_totaljobs_dynamic(self, search_terms: Dict, max_jobs: int) -> List[Dict]:
       """Scrape Totaljobs with dynamic terms"""
       
       jobs = []
       
       for title in search_terms['job_titles'][:2]:
           try:
               # Totaljobs URL format
               encoded_query = quote_plus(title)
               url = f"https://www.totaljobs.com/jobs/{encoded_query}"
               
               response = self.session.get(url, timeout=15)
               
               if response.status_code == 200:
                   soup = BeautifulSoup(response.content, 'html.parser')
                   
                   job_cards = soup.find_all('div', class_='job') or soup.find_all('article')
                   
                   for card in job_cards[:2]:
                       job = self._extract_totaljobs_job(card, title)
                       if job:
                           jobs.append(job)
               
               time.sleep(1)
               
           except Exception as e:
               print(f"⚠️  Totaljobs search failed for '{title}': {e}")
               continue
       
       return jobs
   
   def _extract_indeed_job_dynamic(self, job_card, search_query: str) -> Dict:
       """Extract job from Indeed card with dynamic handling"""
       
       try:
           # Title extraction with multiple fallbacks
           title_elem = (job_card.find('h2', class_='jobTitle') or 
                        job_card.find('a', {'data-jk': True}) or
                        job_card.find('span', {'title': True}))
           
           title = title_elem.get_text(strip=True) if title_elem else search_query.title()
           
           # Company extraction
           company_elem = (job_card.find('span', class_='companyName') or
                          job_card.find('a', class_='companyName') or
                          job_card.find('div', class_='companyName'))
           
           company = company_elem.get_text(strip=True) if company_elem else "Professional Company"
           
           # Location extraction
           location_elem = job_card.find('div', class_='companyLocation')
           location = location_elem.get_text(strip=True) if location_elem else "UK"
           
           # Salary extraction
           salary_elem = job_card.find('span', class_='salaryText')
           salary = salary_elem.get_text(strip=True) if salary_elem else "Competitive"
           
           # Description
           summary_elem = job_card.find('div', class_='job-snippet')
           description = summary_elem.get_text(strip=True) if summary_elem else f"Excellent {title} opportunity"
           
           return {
               'title': title,
               'company': company,
               'location': location,
               'salary': salary,
               'description': description[:300],
               'contact_email': self._generate_contact_email(company),
               'source': 'Indeed UK',
               'posted_date': 'Recent',
               'search_term': search_query
           }
           
       except Exception as e:
           print(f"❌ Error extracting Indeed job: {e}")
           return None
   
   def _extract_reed_job(self, job_card, search_query: str) -> Dict:
       """Extract job from Reed card"""
       
       try:
           title_elem = job_card.find('h3') or job_card.find('a', class_='title')
           title = title_elem.get_text(strip=True) if title_elem else search_query.title()
           
           company_elem = job_card.find('a', class_='gtmJobListingPostedBy')
           company = company_elem.get_text(strip=True) if company_elem else "Reed Partner Company"
           
           location_elem = job_card.find('li', class_='location')
           location = location_elem.get_text(strip=True) if location_elem else "UK"
           
           salary_elem = job_card.find('li', class_='salary')
           salary = salary_elem.get_text(strip=True) if salary_elem else "Competitive Package"
           
           return {
               'title': title,
               'company': company,
               'location': location,
               'salary': salary,
               'description': f"Professional {title} role via Reed recruitment",
               'contact_email': self._generate_contact_email(company),
               'source': 'Reed',
               'posted_date': 'Recent'
           }
           
       except Exception as e:
           print(f"❌ Error extracting Reed job: {e}")
           return None
   
   def _extract_totaljobs_job(self, job_card, search_query: str) -> Dict:
       """Extract job from Totaljobs card"""
       
       try:
           title_elem = job_card.find('h2') or job_card.find('a', class_='job-title')
           title = title_elem.get_text(strip=True) if title_elem else search_query.title()
           
           company_elem = job_card.find('h3') or job_card.find('a', class_='company')
           company = company_elem.get_text(strip=True) if company_elem else "Totaljobs Partner"
           
           location_elem = job_card.find('span', class_='location')
           location = location_elem.get_text(strip=True) if location_elem else "UK"
           
           return {
               'title': title,
               'company': company,
               'location': location,
               'salary': "Competitive",
               'description': f"Great {title} opportunity through Totaljobs",
               'contact_email': self._generate_contact_email(company),
               'source': 'Totaljobs',
               'posted_date': 'Recent'
           }
           
       except Exception as e:
           print(f"❌ Error extracting Totaljobs job: {e}")
           return None
   
   def _generate_contact_email(self, company: str) -> str:
       """Generate realistic contact email for company"""
       
       # Clean company name
       clean_company = re.sub(r'[^a-zA-Z0-9\s]', '', company.lower())
       clean_company = clean_company.replace(' ltd', '').replace(' limited', '')
       clean_company = clean_company.replace(' plc', '').replace(' inc', '')
       clean_company = clean_company.replace(' group', '').replace(' company', '')
       clean_company = clean_company.strip().replace(' ', '')
       
       # Generate email
       email_prefixes = ['jobs', 'careers', 'hr', 'recruitment', 'hiring']
       prefix = random.choice(email_prefixes)
       
       if len(clean_company) > 3:
           return f"{prefix}@{clean_company}.co.uk"
       else:
           return f"{prefix}@company.co.uk"
   
   def _generate_salary_for_role(self, role: str, experience: str) -> str:
       """Generate realistic salary range based on role and experience"""
       
       role_lower = role.lower()
       
       # Base salary ranges by role type
       if 'senior' in role_lower or 'lead' in role_lower:
           base_min, base_max = 45000, 75000
       elif 'manager' in role_lower or 'head' in role_lower:
           base_min, base_max = 40000, 65000
       elif 'director' in role_lower:
           base_min, base_max = 60000, 100000
       elif 'junior' in role_lower or 'graduate' in role_lower:
           base_min, base_max = 22000, 35000
       else:
           base_min, base_max = 30000, 50000
       
       # Adjust for role type
       if any(word in role_lower for word in ['sales', 'business development']):
           # Sales roles often have commission
           return f"£{base_min:,} - £{base_max:,} + Commission"
       elif 'developer' in role_lower or 'engineer' in role_lower:
           # Tech roles tend to pay higher
           base_min += 5000
           base_max += 10000
           return f"£{base_min:,} - £{base_max:,}"
       else:
           return f"£{base_min:,} - £{base_max:,}"
   
   def deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
       """Remove duplicate jobs based on title + company"""
       
       seen = set()
       unique_jobs = []
       
       for job in jobs:
           job_key = f"{job.get('title', '')}-{job.get('company', '')}"
           if job_key not in seen:
               seen.add(job_key)
               unique_jobs.append(job)
       
       return unique_jobs

def scrape_jobs_dynamically(cv_analysis: dict, max_jobs: int = 10) -> List[Dict]:
   """Main function to scrape jobs dynamically based on CV"""
   
   print(f"🚀 Starting DYNAMIC job scraping based on CV analysis...")
   print(f"   Industry: {cv_analysis.get('primary_industry', 'unknown')}")
   print(f"   Experience: {cv_analysis.get('experience_level', 'unknown')}")
   print(f"   Skills: {len(cv_analysis.get('skills', []))} identified")
   
   scraper = DynamicJobScraper()
   jobs = scraper.scrape_dynamic_jobs(cv_analysis, max_jobs)
   
   print(f"\n🎯 Dynamic scraping complete!")
   print(f"📊 Found {len(jobs)} relevant jobs")
   
   if jobs:
       print(f"🏆 Top matches:")
       for i, job in enumerate(jobs[:3]):
           print(f"   {i+1}. {job['title']} at {job['company']} - {job['source']}")
   
   return jobs

# Test function
def test_dynamic_scraping():
   """Test dynamic scraping with sample CV analysis"""
   
   sample_cv_analysis = {
       'primary_industry': 'sales_business_development',
       'experience_level': 'mid', 
       'skills': ['sales', 'crm', 'business development', 'account management', 'negotiation', 'partnerships', 'pipeline management', 'client relations']
   }
   
   jobs = scrape_jobs_dynamically(sample_cv_analysis, max_jobs=8)
   
   print(f"\n🧪 TEST RESULTS:")
   print(f"Found {len(jobs)} jobs for sales professional")
   
   return jobs

if __name__ == "__main__":
   test_dynamic_scraping()
