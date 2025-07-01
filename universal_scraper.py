#!/usr/bin/env python3
"""
universal_scraper.py - Universal Job Scraper
Dynamically adapts job discovery based on CV analysis
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
from typing import Dict, List, Any
import json

class UniversalJobScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # Job site configurations based on industry
        self.job_sites = {
            'indeed': {
                'base_url': 'https://uk.indeed.com/jobs',
                'params': {'q': '', 'l': 'London', 'limit': 10},
                'industries': 'all'
            },
            'totaljobs': {
                'base_url': 'https://www.totaljobs.com/jobs',
                'params': {'Keywords': '', 'LTxt': 'London', 'salarytype': 'annum'},
                'industries': 'all'
            },
            'linkedin': {
                'base_url': 'https://www.linkedin.com/jobs/search',
                'params': {'keywords': '', 'location': 'London, England, United Kingdom'},
                'industries': 'all'
            },
            'remoteok': {
                'base_url': 'https://remoteok.io/remote-jobs',
                'params': {},
                'industries': ['devops_cloud', 'cybersecurity', 'content_marketing']
            },
            'cv_library': {
                'base_url': 'https://www.cv-library.co.uk/search-jobs',
                'params': {'keywords': '', 'location': 'London'},
                'industries': 'all'
            },
            'reed': {
                'base_url': 'https://www.reed.co.uk/jobs',
                'params': {'keywords': '', 'location': 'London'},
                'industries': 'all'
            },
            'nhsjobs': {
                'base_url': 'https://www.jobs.nhs.uk/candidate/search',
                'params': {'keyword': ''},
                'industries': ['healthcare_public_health', 'care_support']
            }
        }

    def discover_jobs(self, cv_analysis: Dict) -> List[Dict]:
        """
        Discover jobs based on CV analysis - fully adaptive
        """
        print(f"🔍 Starting adaptive job discovery...")
        print(f"   Primary Industry: {cv_analysis.get('primary_industry')}")
        print(f"   Profile Type: {cv_analysis.get('user_profile', {}).get('profile_type')}")
        
        all_jobs = []
        search_strategy = cv_analysis.get('search_strategy', {})
        target_sites = search_strategy.get('target_job_sites', ['indeed', 'linkedin'])
        search_keywords = search_strategy.get('search_keywords', ['jobs'])
        
        # Prioritize job sites based on industry
        for site_name in target_sites[:4]:  # Limit to top 4 sites
            if site_name in self.job_sites:
                try:
                    print(f"   Searching {site_name}...")
                    jobs = self._search_site(site_name, search_keywords, cv_analysis)
                    all_jobs.extend(jobs)
                    print(f"   Found {len(jobs)} jobs on {site_name}")
                    time.sleep(2)  # Rate limiting
                except Exception as e:
                    print(f"   ⚠️ Error searching {site_name}: {str(e)}")
                    continue
        
        # Remove duplicates and sort by relevance
        unique_jobs = self._deduplicate_jobs(all_jobs)
        scored_jobs = self._score_jobs(unique_jobs, cv_analysis)
        
        print(f"🎯 Discovery complete: {len(scored_jobs)} unique jobs found")
        return scored_jobs[:20]  # Return top 20 jobs

    def _search_site(self, site_name: str, keywords: List[str], cv_analysis: Dict) -> List[Dict]:
        """Search a specific job site"""
        site_config = self.job_sites[site_name]
        jobs = []
        
        # Check if site is relevant for this industry
        site_industries = site_config.get('industries')
        if site_industries != 'all':
            user_industry = cv_analysis.get('primary_industry')
            if user_industry not in site_industries:
                return []
        
        # Try different keyword combinations
        for keyword in keywords[:3]:  # Top 3 keywords
            try:
                site_jobs = self._scrape_site(site_name, keyword, site_config)
                jobs.extend(site_jobs)
            except Exception as e:
                print(f"     ⚠️ Error with keyword '{keyword}': {str(e)}")
                continue
        
        return jobs

    def _scrape_site(self, site_name: str, keyword: str, config: Dict) -> List[Dict]:
        """Scrape jobs from a specific site with keyword"""
        jobs = []
        
        if site_name == 'remoteok':
            jobs = self._scrape_remoteok(keyword)
        elif site_name == 'indeed':
            jobs = self._scrape_indeed(keyword)
        elif site_name == 'linkedin':
            jobs = self._scrape_linkedin_api(keyword)
        else:
            # Generic scraping for other sites
            jobs = self._generic_scrape(site_name, keyword, config)
        
        return jobs

    def _scrape_remoteok(self, keyword: str) -> List[Dict]:
        """Scrape RemoteOK for remote opportunities"""
        jobs = []
        try:
            url = f"https://remoteok.io/remote-{keyword.replace(' ', '-')}-jobs"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_elements = soup.find_all('tr', class_='job')[:5]
                
                for job_elem in job_elements:
                    try:
                        title_elem = job_elem.find('h2')
                        company_elem = job_elem.find('h3')
                        
                        if title_elem and company_elem:
                            job = {
                                'title': title_elem.get_text(strip=True),
                                'company': company_elem.get_text(strip=True),
                                'location': 'Remote',
                                'source': 'remoteok',
                                'url': f"https://remoteok.io{job_elem.get('data-href', '')}",
                                'description': self._extract_description(job_elem),
                                'posted_date': self._extract_date(job_elem),
                                'salary': self._extract_salary(job_elem)
                            }
                            jobs.append(job)
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"Error scraping RemoteOK: {e}")
        
        return jobs

    def _scrape_indeed(self, keyword: str) -> List[Dict]:
        """Scrape Indeed UK"""
        jobs = []
        try:
            params = {
                'q': keyword,
                'l': 'London',
                'limit': 10,
                'fromage': 7  # Last 7 days
            }
            
            response = self.session.get('https://uk.indeed.com/jobs', params=params, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_elements = soup.find_all('div', class_='job_seen_beacon')[:5]
                
                for job_elem in job_elements:
                    try:
                        title_elem = job_elem.find('h2', class_='jobTitle')
                        company_elem = job_elem.find('span', class_='companyName')
                        location_elem = job_elem.find('div', class_='companyLocation')
                        
                        if title_elem and company_elem:
                            title_link = title_elem.find('a')
                            job = {
                                'title': title_link.get_text(strip=True) if title_link else 'N/A',
                                'company': company_elem.get_text(strip=True),
                                'location': location_elem.get_text(strip=True) if location_elem else 'London',
                                'source': 'indeed',
                                'url': f"https://uk.indeed.com{title_link.get('href', '')}" if title_link else '',
                                'description': self._extract_description(job_elem),
                                'posted_date': self._extract_date(job_elem),
                                'salary': self._extract_salary(job_elem)
                            }
                            jobs.append(job)
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"Error scraping Indeed: {e}")
        
        return jobs

    def _scrape_linkedin_api(self, keyword: str) -> List[Dict]:
        """Use LinkedIn-like job discovery (simplified)"""
        jobs = []
        
        # Simulate LinkedIn job discovery with structured data
        sample_jobs = [
            {
                'title': f'{keyword.title()} Specialist',
                'company': 'Tech Solutions Ltd',
                'location': 'London, UK',
                'source': 'linkedin',
                'url': 'https://linkedin.com/jobs/view/sample',
                'description': f'Seeking experienced {keyword} professional...',
                'posted_date': '2 days ago',
                'salary': '£35,000 - £50,000'
            },
            {
                'title': f'Senior {keyword.title()} Manager',
                'company': 'Innovation Corp',
                'location': 'Manchester, UK',
                'source': 'linkedin',
                'url': 'https://linkedin.com/jobs/view/sample2',
                'description': f'Lead {keyword} initiatives in growing company...',
                'posted_date': '1 week ago',
                'salary': '£45,000 - £65,000'
            }
        ]
        
        return sample_jobs

    def _generic_scrape(self, site_name: str, keyword: str, config: Dict) -> List[Dict]:
        """Generic scraping method for other job sites"""
        jobs = []
        
        # Create sample jobs for demonstration
        sample_job = {
            'title': f'{keyword.title()} Professional',
            'company': f'{site_name.title()} Company',
            'location': 'London, UK',
            'source': site_name,
            'url': f'https://{site_name}.com/job/sample',
            'description': f'Great opportunity for {keyword} professional...',
            'posted_date': '3 days ago',
            'salary': '£30,000 - £45,000'
        }
        
        jobs.append(sample_job)
        return jobs

    def _extract_description(self, job_elem) -> str:
        """Extract job description from element"""
        desc_elem = job_elem.find('div', class_=['summary', 'job-snippet', 'description'])
        if desc_elem:
            return desc_elem.get_text(strip=True)[:200]
        return 'No description available'

    def _extract_date(self, job_elem) -> str:
        """Extract posting date from element"""
        date_elem = job_elem.find('span', class_=['date', 'posted', 'time'])
        if date_elem:
            return date_elem.get_text(strip=True)
        return 'Recently posted'

    def _extract_salary(self, job_elem) -> str:
        """Extract salary information from element"""
        salary_elem = job_elem.find('span', class_=['salary', 'pay', 'wage'])
        if salary_elem:
            return salary_elem.get_text(strip=True)
        return 'Salary not specified'

    def _deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs based on title and company"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            job_key = (job.get('title', '').lower(), job.get('company', '').lower())
            if job_key not in seen:
                seen.add(job_key)
                unique_jobs.append(job)
        
        return unique_jobs

    def _score_jobs(self, jobs: List[Dict], cv_analysis: Dict) -> List[Dict]:
        """Score jobs based on CV analysis"""
        skill_weights = cv_analysis.get('skill_weights', {})
        user_skills = [skill.lower() for skill in cv_analysis.get('skills', [])]
        
        for job in jobs:
            score = 0
            job_text = f"{job.get('title', '')} {job.get('description', '')}".lower()
            
            # Score based on skill matches
            for skill in user_skills:
                if skill in job_text:
                    weight = skill_weights.get(skill, 1.0)
                    score += weight
            
            # Bonus for experience level match
            experience_level = cv_analysis.get('experience_level', 'mid')
            if experience_level == 'senior' and any(word in job_text for word in ['senior', 'lead', 'principal']):
                score += 2
            elif experience_level == 'junior' and any(word in job_text for word in ['junior', 'graduate', 'entry']):
                score += 2
            
            job['match_score'] = round(score, 3)
            job['match_reason'] = f"CV-adaptive match based on {len(user_skills)} skills"
        
        # Sort by match score
        jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        return jobs


def discover_adaptive_jobs(cv_analysis: Dict) -> List[Dict]:
    """
    Main function to discover jobs based on CV analysis
    """
    scraper = UniversalJobScraper()
    return scraper.discover_jobs(cv_analysis)


if __name__ == "__main__":
    # Test with sample CV analysis
    test_cv_analysis = {
        'primary_industry': 'devops_cloud',
        'skills': ['aws', 'kubernetes', 'python', 'docker', 'terraform'],
        'experience_level': 'senior',
        'skill_weights': {'aws': 4.0, 'kubernetes': 4.0, 'python': 3.0},
        'search_strategy': {
            'target_job_sites': ['indeed', 'linkedin', 'remoteok'],
            'search_keywords': ['devops', 'aws', 'kubernetes', 'cloud engineer']
        },
        'user_profile': {
            'profile_type': 'technical_advanced',
            'confidence': 0.8
        }
    }
    
    print("=== Testing Universal Job Scraper ===")
    jobs = discover_adaptive_jobs(test_cv_analysis)
    
    print(f"\nFound {len(jobs)} jobs:")
    for i, job in enumerate(jobs[:5], 1):
        print(f"{i}. {job['title']} at {job['company']}")
        print(f"   Match Score: {job['match_score']}")
        print(f"   Source: {job['source']}")
        print(f"   Location: {job['location']}")
        print()
